from transaction             import Transaction

from abc import ABC, abstractmethod

import base64
import datetime
import hashlib
import json
import math
import copy
import logging

class Response(ABC):
    pass

class StablecoinInteractor:

    def __init__(self, name, bank, persistence, blockchain, rateE2T, rateT2E):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.name        = name
        self.bank        = bank
        self.persistence = persistence
        self.blockchain  = blockchain
        self.rateT2E     = rateT2E
        self.rateE2T     = rateE2T

        self.blockchain.set_callback_instance(self)
        self.bank.set_callback_instance(self)

        self.provider_map = {
                "bank" : self.bank,
                "blockchain" : self.blockchain
                }

    def get_additional_post_routes(self):
        return self.bank.get_post_callback_routes() or {}

    # Creation interface
    # CREATE_initiate # Step 1 -> returns info to connect to gateway over ipv8
    # CREATE_connect # Step 2 -> user connects through ipv8 to register its node and address
    # CREATE_start_payment # Step 3 -> returns the payment link to the user
    # CREATE_finish_payment # Step 4 -> triggers_payout

    # Destruction interface:
    # DESTROY_initiate # Step 1 -> returns: wallet_address and payment id to send money to with trustchain ipv8
    # DESTROY_pay      # Step 2 -> user connects through ipv8 and sends the funds providing the payment id

    "Creation interface"
    # Step 1 -> returns info to connect to gateway over ipv8
    def CREATE_initiate(self, collatoral_amount_cent : int) -> Transaction:
        "Registers payment in the DB"
        "Returns gateway key, ip and port, as well as a payment id"

        payout_amount=self.get_exchange_rate_col_to_tok(collatoral_amount_cent)

        payout_provider = self.provider_map["blockchain"]
        gateway_connection_data = payout_provider.get_connection_info()

        transaction = Transaction(
                payment_provider="bank", payment_currency="euro",
                payout_provider="blockchain", payout_currency="eurotoken",
                gateway_connection_data=gateway_connection_data,
                amount=collatoral_amount_cent, payout_amount=payout_amount
                )

        self.persistence.create_transaction(transaction)

        return transaction

    # Step 2 -> user connects through ipv8 to register its node and address
    def CREATE_connect(self, payment_id, pubkey, ip, port) -> Transaction:
        "Registers extra info in the DB"
        transaction = self.persistence.get_payment_by_id(payment_id)

        if transaction is None:
            self.logger.info("no transaction found for id " + payment_id)
            return None

        if transaction["status"] not in [Transaction.Status.CREATED, Transaction.Status.PAYMENT_READY]:
            self.logger.info("create_connect: Transaction in wrong state for id " + payment_id, transaction["status"])
            return None

        transaction.add_payout_connection_data(payout_connection_data={
            'pubkey' : pubkey,
            'ip'     : ip,
            'port'   : port,
            })

        self.persistence.update_transaction(transaction)

        # Steps for skipping payment and going directly to send (for testing trustchain transactions)
        # self.CREATE_start_payment(transaction["payment_id"])
        # return self.CREATE_finish_payment(transaction["payment_id"])

        return transaction

    # Step 3 -> returns the payment link to the user
    def CREATE_start_payment(self, payment_id) -> Transaction:
        "Returns a payment link"

        transaction = self.persistence.get_payment_by_id(payment_id)

        if transaction is None:
            self.logger.info("no transaction found for id " + payment_id)
            return None

        if transaction["status"] != Transaction.Status.PAYMENT_READY:
            self.logger.info("create_start_payment: Transaction in wrong state for id " + payment_id, transaction["status"])
            return None

        payment_provider = self.provider_map[transaction["payment_provider"]]
        payment_transaction_data = payment_provider.create_payment_request(transaction["amount"], payment_id)

        transaction.start_payment(
                payment_connection_data=payment_transaction_data
                )

        self.persistence.update_transaction(transaction)

        return transaction

    # Step 4 -> triggers_payout
    def CREATE_finish_payment(self, payment_id):
        "Will be called when"
        "Pays out tokens to pubkey@ip:port"

        transaction = self.persistence.get_payment_by_id(payment_id)

        if transaction is None:
            self.logger.info("no transaction found for id " + payment_id)
            return None

        if transaction["status"] != Transaction.Status.PAYMENT_PENDING:
            self.logger.info("create_finish_payment: Transaction in wrong state for id " + payment_id, transaction["status"])
            return None

        payment_provider = self.provider_map[transaction["payment_provider"]]

        # # TODO: remove
        # payment_provider.payment_done_trigger(transaction["payment_connection_data"], "IBAN")

        payment_counterparty = payment_provider.attempt_payment_done(transaction["payment_connection_data"]['payment_id'])

        if payment_counterparty:
            transaction.confirm_payment(payment_transaction_data=payment_counterparty)

            payout_provider = self.provider_map[transaction["payout_provider"]]
            payout_id = payout_provider.initiate_payment(
                    transaction["payout_connection_data"],
                    transaction["payout_amount"], payment_id)
            # self.logger.info(payout_id) # TODO: get block id here, query db for latest block (try to make this safe)
            # if payout_id:
            transaction.payout_done("ID NOT IMPLEMENTED")

            def when_finished(fut):
                self.logger.info("Delivery: ", fut.result())

            payout_id.add_done_callback(when_finished)

            self.persistence.update_transaction(transaction)

        return transaction

    def get_transaction(self, payment_id):
        return self.persistence.get_payment_by_id(payment_id)

    "Destruction interface"
    # Step 1 -> returns: wallet_address and payment id to send money to with trustchain ipv8
    def DESTROY_initiate(self, amount, iban):
        "Registers payment in the DB"
        "Returns gateway key, ip and port, as well as a payment id"

        payout_amount = self.get_exchange_rate_tok_to_col(amount)

        payout_provider = self.provider_map["blockchain"]
        gateway_connection_data = payout_provider.get_connection_info()

        transaction = Transaction(
                payment_provider="blockchain", payment_currency="eurotoken",
                payout_provider="bank", payout_currency="euro",
                gateway_connection_data=gateway_connection_data,
                payout_connection_data=iban,
                amount=amount, payout_amount=payout_amount
                )

        transaction.start_payment(
                payment_connection_data=gateway_connection_data
                )

        self.persistence.create_transaction(transaction)

        return transaction

    # Step 2 -> user connects through ipv8 and sends the funds providing the payment id
    def DESTROY_pay(self, payment_id, iban, amount, pubkey):
        if iban is not None:
            transaction = self.DESTROY_initiate(amount, iban)
        else:
            transaction = self.persistence.get_payment_by_id(payment_id)
            if transaction is None:
                self.logger.info("no transaction found for id " + payment_id)
                return False

        if transaction["status"] != Transaction.Status.PAYMENT_PENDING:
            self.logger.info("destroy_pay: Transaction in wrong state for id " + payment_id, transaction["status"])
            return False

        if transaction["amount"] != amount:
            "Incorrect amount"
            self.logger.info("incorrect amount transfered, reject block")
            return False

        transaction.confirm_payment(payment_transaction_data=pubkey)

        payout_provider = self.provider_map[transaction["payout_provider"]]
        payout_id = payout_provider.initiate_payment(
                transaction["payout_connection_data"],
                transaction["payout_amount"], payment_id)

        # if payout_id: #shouldn't fail
        transaction.payout_done(payout_id)

        self.persistence.update_transaction(transaction)

        return transaction # TODO: Return or raise what ipv8 expects

    "Other"

    def get_wallet_transactions(self, wallet):
        return [transaction for transaction in self.persistence.get_all().values() if
                (transaction['payment_provider'] == 'blockchain' and transaction.get("counterparty_account") == wallet) or
                (transaction['payout_provider'] == 'blockchain' and transaction["payout_account"] == wallet)
                ]

    def get_iban_transactions(self, iban):
        return [transaction for transaction in self.persistence.get_all().values() if
                (transaction['payment_provider'] == 'bank' and transaction.get("counterparty_account") == iban) or
                (transaction['payout_provider'] == 'bank' and transaction["payout_account"] == iban)
                ]

    def get_wallet_balance(self, wallet):
        return self.blockchain.get_balance(wallet)

    def print_struct(self):
        self.logger.warning(self.bank)
        self.logger.warning(self.persistence)
        self.logger.warning(self.blockchain)

    def get_exchange_rate_col_to_tok(self, collatoral_amount_cent):
        if not type(collatoral_amount_cent) == int:
            raise self.VerificationError("Collatoral cent amount must be an Integer")
        # return math.floor(collatoral_amount_cent * 0.99)
        return math.floor(collatoral_amount_cent * self.rateE2T)

    def get_exchange_rate_tok_to_col(self, token_amount_cent):
        if not type(token_amount_cent) == int:
            raise self.VerificationError("Token cent amount must be an Integer")
        # return math.floor(token_amount_cent * 0.99)
        return math.floor(token_amount_cent * self.rateT2E)

    class VerificationError(Exception):
        pass

    class CommunicationError(Exception):
        pass

