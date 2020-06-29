from stablecoin.bank.bank               import Bank
from stablecoin.blockchain.blockchain   import Blockchain
from stablecoin.persistence.persistence import Persistence
from stablecoin.ui.ui                   import UI

from abc import ABC, abstractmethod

import base64
import datetime
import hashlib
import json
import math

class Response(ABC):
    pass

class StableCoin(ABC):
    def __init__(self, bank, persistence, blockchain):
        self.bank        = bank
        self.persistence = persistence
        self.blockchain  = blockchain

    @abstractmethod
    def initiate_creation(self):
        pass

    @abstractmethod
    def initiate_destruction(self, collatoral_amount_cent, destination_wallet):
        pass

    @abstractmethod
    def transaction_status(self, transaction_id):
        pass

    @abstractmethod
    def finish_creation_payment(self, transaction_id) -> Response:
        pass

class StabecoinInteractor(StableCoin):

    def print_struct(self):
        print(self.bank)
        print(self.persistence)
        print(self.blockchain)

    def generate_payment_id(self, payment_data):
        """
        Seed for ID:
            - Creation date
            - Euro Amount
            - Euro Token Amount
            - Dest Wallet
        """
        relevant_data = {
                "created"                : payment_data["created"],
                "collatoral_amount_cent" : payment_data["collatoral_amount_cent"],
                "token_amount_cent"      : payment_data["token_amount_cent"],
                "destination_wallet"     : payment_data["destination_wallet"],
                }
        serialised = json.dumps(relevant_data, sort_keys=True, ensure_ascii=True).encode('utf-8')
        return str(base64.b64encode(hashlib.sha1(
            serialised
            ).digest()))

    def get_exchange_rate_col_to_tok(self, collatoral_amount_cent):
        if not type(collatoral_amount_cent) == int:
            raise self.VerificationError("Collatoral cent amount must be an Integer")
        return math.floor(collatoral_amount_cent * 0.99)

    def get_exchange_rate_tok_to_col(self, token_amount_cent):
        if not type(token_amount_cent) == int:
            raise self.VerificationError("Token cent amount must be an Integer")
        return math.floor(token_amount_cent * 0.99)

    "Creation"
    def initiate_creation(self, collatoral_amount_cent, destination_wallet):
        payment_data = self.bank.create_payment_request(collatoral_amount_cent)

        payment_data["status"]             = "open"
        payment_data["created"]            = datetime.datetime.now().timestamp()
        payment_data["token_amount_cent"]  = self.get_exchange_rate_col_to_tok(collatoral_amount_cent)
        payment_data["destination_wallet"] = destination_wallet

        payment_data["payment_id"] = self.generate_payment_id(payment_data)
        self.persistence.create_transaction(payment_data)

        return payment_data

    def finish_creation_payment(self, transaction_id):
        if self.bank.payment_request_status(transaction_id) != "done":
            return False
        transaction = self.persistence.get_payment_by_id(transaction_id)
        self.blockchain.transfer("ASDFASDF", transaction["token_amount_cent"])
        return transaction

    "Destruction"
    def initiate_destruction(self, token_amount_cent, destination_iban):
        payment_data = self.blockchain.create_payment_request(token_amount_cent)

        payment_data["status"]                  = "open"
        payment_data["created"]                 = datetime.datetime.now().timestamp()
        payment_data["collatoral_amount_cent"]  = self.get_exchange_rate_tok_to_col(token_amount_cent)
        payment_data["destination_iban"]        = destination_iban

        payment_data["payment_id"]              = self.generate_payment_id(payment_data)
        self.persistence.create_transaction(payment_data)

        return payment_data

    "Status"

    def transaction_status(self, transaction_id):
        pass


    class VerificationError(Exception):
        pass

    class CommunicationError(Exception):
        pass

