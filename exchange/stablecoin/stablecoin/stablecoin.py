from stablecoin.bank.bank               import Bank
from stablecoin.blockchain.blockchain   import Blockchain
from stablecoin.persistence.persistence import Persistence
from stablecoin.ui.ui                   import UI

import base64
import datetime
import hashlib
import json
import math

# from abc import ABC, abstractmethod

# class StableCoin(ABC):
#     @abstractmethod
#     def assign_mony(self):
#         pass

class StabecoinInteractor:

    def __init__(self, bank, persistence, blockchain
            # , ui
            ):
        self.bank        = bank
        self.persistence = persistence
        self.blockchain  = blockchain
        # self.ui          = ui

    def print_struct(self):
        print(self.bank)
        print(self.persistence)
        print(self.blockchain)
        # print(self.ui)

    def get_payment_id(self, payment_data):
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
        return base64.b64encode(hashlib.sha1(
            serialised
            ).digest())

    def get_exchange_rate(self, collatoral_amount_cent):
        if not type(collatoral_amount_cent) == int:
            raise self.VerificationError("Collatoral cent amount must be an Integer")
        return math.ceil(collatoral_amount_cent * 0.99)

    def start_transaction(self, collatoral_amount_cent, destination_wallet):
        payment_data = self.bank.initiate_payment(collatoral_amount_cent)

        payment_data["status"]             = "open"
        payment_data["created"]            = datetime.datetime.now().timestamp()
        payment_data["token_amount_cent"]  = self.get_exchange_rate(collatoral_amount_cent)
        payment_data["destination_wallet"] = destination_wallet

        payment_data["payment_id"] = self.get_payment_id(payment_data)
        self.persistence.create_transaction(payment_data)

        return payment_data

    def finish_transaction(self, transaction_id):
        transaction = self.persistence.get_payment_by_id(transaction_id)
        if self.bank.check_payment_status(transaction) != "done":
            return False
        self.blockchain.transfer("ASDFASDF", transaction["token_amount_cent"])
        return transaction

    class VerificationError(Exception):
        pass

