from stablecoin.bank.bank               import Bank
from stablecoin.blockchain.blockchain   import Blockchain
from stablecoin.persistence.persistence import Persistence
from stablecoin.ui.ui                   import UI
from stablecoin.transaction             import Transaction

from abc import ABC, abstractmethod

import base64
import datetime
import hashlib
import json
import math
import copy

class Response(ABC):
    pass

class StableCoin(ABC):
    def __init__(self, bank, persistence, blockchain):
        self.bank        = bank
        self.persistence = persistence
        self.blockchain  = blockchain
        self.blockchain.set_callback_instance(self)

        self.provider_map = {
                "bank" : self.bank,
                "blockchain" : self.blockchain
                }

    @abstractmethod
    def initiate_creation(self):
        pass

    @abstractmethod
    def initiate_destruction(self, collatoral_amount_cent, destination_account):
        pass

    @abstractmethod
    def transaction_status(self, transaction_id):
        pass

    @abstractmethod
    def attempt_finish_creation_payment(self, transaction_id) -> Response:
        pass

class StablecoinInteractor(StableCoin):

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
            print("no transaction found for id " + payment_id)
            return None

        if transaction["status"] not in [Transaction.Status.CREATED, Transaction.Status.PAYMENT_READY]:
            print("create_connect: Transaction in wrong state for id " + payment_id, transaction["status"])
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
            print("no transaction found for id " + payment_id)
            return None

        if transaction["status"] != Transaction.Status.PAYMENT_READY:
            print("create_start_payment: Transaction in wrong state for id " + payment_id, transaction["status"])
            return None

        payment_provider = self.provider_map[transaction["payment_provider"]]
        payment_transaction_link = payment_provider.create_payment_request(transaction["amount"])

        transaction.start_payment(
                payment_connection_data=payment_transaction_link
                )

        self.persistence.update_transaction(transaction)

        return transaction

    # Step 4 -> triggers_payout
    def CREATE_finish_payment(self, payment_id):
        "Pays out tokens to pubkey@ip:port"

        transaction = self.persistence.get_payment_by_id(payment_id)

        if transaction is None:
            print("no transaction found for id " + payment_id)
            return None

        if transaction["status"] != Transaction.Status.PAYMENT_PENDING:
            print("create_finish_payment: Transaction in wrong state for id " + payment_id, transaction["status"])
            return None

        payment_provider = self.provider_map[transaction["payment_provider"]]

        # TODO: remove
        payment_provider.payment_done_trigger(transaction["payment_connection_data"], "IBAN")

        payment_counterparty = payment_provider.attempt_payment_done(transaction["payment_connection_data"])

        if payment_counterparty:
            transaction.confirm_payment(payment_transaction_data=payment_counterparty)

            payout_provider = self.provider_map[transaction["payout_provider"]]
            payout_id = payout_provider.initiate_payment(
                    transaction["payout_connection_data"],
                    transaction["payout_amount"], payment_id)
            # print(payout_id) # TODO: get block id here, query db for latest block (try to make this safe)
            # if payout_id:
            transaction.payout_done("ID NOT IMPLEMENTED")

        def when_finished(fut):
            print("Delivery: ", fut.result())

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
    def DESTROY_pay(self, payment_id, amount, pubkey):
        transaction = self.persistence.get_payment_by_id(payment_id)

        if transaction is None:
            print("no transaction found for id " + payment_id)
            return False # TODO: Raise validation error

        if transaction["status"] != Transaction.Status.PAYMENT_PENDING:
            print("destroy_pay: Transaction in wrong state for id " + payment_id, transaction["status"])
            return False # TODO: Raise validation error

        print("payment recieved")

        if transaction["amount"] != amount:
            "Incorrect amount"
            print("incorrect amount transfered, reject block") #TODO: Make sure trustchain asks this function for validation
            return False # TODO: Raise validation error

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
        print(self.bank)
        print(self.persistence)
        print(self.blockchain)

    def get_exchange_rate_col_to_tok(self, collatoral_amount_cent):
        if not type(collatoral_amount_cent) == int:
            raise self.VerificationError("Collatoral cent amount must be an Integer")
        return math.floor(collatoral_amount_cent * 0.99)

    def get_exchange_rate_tok_to_col(self, token_amount_cent):
        if not type(token_amount_cent) == int:
            raise self.VerificationError("Token cent amount must be an Integer")
        return math.floor(token_amount_cent * 0.99)

    "OLD"

    "1. Creation (Status -> PAYMENT_PENDING)"
    def initiate_creation(self, collatoral_amount_cent, destination_wallet, temp_counterparty=None):
        payout_amount=self.get_exchange_rate_col_to_tok(collatoral_amount_cent)

        transaction = Transaction(
                payment_provider="bank", payment_currency="euro",
                payout_provider="blockchain", payout_currency="eurotoken",
                payout_account=destination_wallet,
                amount=collatoral_amount_cent, payout_amount=payout_amount
                )

        payment_provider = self.provider_map[transaction["payment_provider"]]
        payment_transaction_id = payment_provider.create_payment_request(collatoral_amount_cent)

        transaction.start_payment(
                payment_transaction_id=payment_transaction_id,
                expected_payment_account=None,
                temp_counterparty=temp_counterparty
                )

        self.persistence.create_transaction(transaction)

        return transaction.get_data()

    "1. Destruction (Status -> PAYMENT_PENDING)"
    def initiate_destruction(self, token_amount_cent, destination_iban, temp_counterparty=None):
        payout_amount = self.get_exchange_rate_tok_to_col(token_amount_cent)

        transaction = Transaction(
                payment_provider="blockchain", payment_currency="eurotoken",
                payout_provider="bank", payout_currency="euro",
                payout_account=destination_iban,
                amount=token_amount_cent, payout_amount=payout_amount
                )

        payment_provider = self.provider_map[transaction["payment_provider"]]
        chain_transaction_id = payment_provider.create_payment_request(token_amount_cent)

        transaction.start_payment(
                payment_transaction_id=chain_transaction_id,
                expected_payment_account=None,
                temp_counterparty=temp_counterparty
                )

        self.persistence.create_transaction(transaction)

        return transaction.get_data()

    "2. Payment done, Entry point for all outgoing payments (Status -> PAYMENT_DONE)"
    def complete_payment(self, payment_id, counterparty):
        transaction = self.persistence.get_payment_by_id(payment_id)

        if transaction is None:
            print("no transaction found for id " + payment_id)
            return None

        if transaction["status"] != Transaction.Status.PAYMENT_PENDING:
            return True

        payment_provider = self.provider_map[transaction["payment_provider"]]

        ans = payment_provider.payment_done_trigger(transaction["payment_transaction_id"], counterparty)
        if ans:
            transaction.confirm_payment(counterparty)
            self.persistence.update_transaction(transaction)
        return ans

    def attempt_finish_creation_payment(self, transaction):
        if transaction["status"] != transaction.Status.PAYMENT_DONE:
            return None
        payout_provider = self.provider_map[transaction["payout_provider"]]

        payout_transaction_id = payout_provider.initiate_payment(transaction["payout_account"], transaction["payout_amount"])

        transaction.payout_done(payout_transaction_id)
        self.persistence.update_transaction(transaction)
        return transaction

    "Status and check completion trigger"
    def transaction_status(self, transaction_id):
        transaction = copy.copy(self.persistence.get_payment_by_id(transaction_id))

        if not transaction:
            return None

        self.attempt_finish_creation_payment(transaction)

        return transaction.get_data()

    class VerificationError(Exception):
        pass

    class CommunicationError(Exception):
        pass

