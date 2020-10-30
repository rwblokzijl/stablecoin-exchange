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

    "Entry point for all outgoing payments"
    def complete_payment(self, payment_id, counterparty):
        transaction = self.persistence.get_payment_by_id(payment_id)

        if transaction is None:
            print("no transaction found for id " + payment_id)
            return False

        if transaction["status"] != Transaction.Status.PAYMENT_PENDING:
            return True

        payment_provider = self.provider_map[transaction["payment_provider"]]

        ans = payment_provider.payment_done_trigger(transaction["payment_provider_id"], counterparty)
        if ans:
            transaction.confirm_payment(counterparty)
            self.persistence.update_transaction(transaction)
        return ans

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

    "Creation"
    def initiate_creation(self, collatoral_amount_cent, destination_wallet, temp_counterparty=None):
        payout_amount=self.get_exchange_rate_col_to_tok(collatoral_amount_cent)

        payment_data = Transaction(
                payment_provider="bank", payment_currency="euro",
                payout_provider="blockchain", payout_currency="eurotoken",
                payout_account=destination_wallet,
                amount=collatoral_amount_cent, payout_amount=payout_amount
                )

        bank_transaction_id = self.bank.create_payment_request(collatoral_amount_cent)

        payment_data.start_payment(
                payment_provider_id=bank_transaction_id,
                expected_payment_account=None,
                temp_counterparty=temp_counterparty
                )

        self.persistence.create_transaction(payment_data)

        return payment_data.get_data()

    def attempt_finish_creation_payment(self, transaction):
        if transaction["status"] != transaction.Status.PAYMENT_DONE:
            return False
        payout_transaction_id = self.provider_map[transaction["payout_provider"]].initiate_payment(transaction["payout_account"], transaction["payout_amount"])
        transaction.payout_done(payout_transaction_id)
        self.persistence.update_transaction(transaction)
        return transaction

    "Destruction"
    def initiate_destruction(self, token_amount_cent, destination_iban, temp_counterparty=None):
        payout_amount = self.get_exchange_rate_tok_to_col(token_amount_cent)

        payment_data = Transaction(
                payment_provider="blockchain", payment_currency="eurotoken",
                payout_provider="bank", payout_currency="euro",
                payout_account=destination_iban,
                amount=token_amount_cent, payout_amount=payout_amount
                )

        chain_transaction_id = self.blockchain.create_payment_request(token_amount_cent)

        payment_data.start_payment(
                payment_provider_id=chain_transaction_id,
                expected_payment_account=None,
                temp_counterparty=temp_counterparty
                )

        self.persistence.create_transaction(payment_data)

        return payment_data.get_data()

    "Status"

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

