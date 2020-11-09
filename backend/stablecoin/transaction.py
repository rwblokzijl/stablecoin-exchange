from copy     import copy
from datetime import datetime
from enum     import Enum

import json
import base64
import hashlib
import random

class Transaction:
    class Status(Enum):
        CREATED = 0
        PAYMENT_READY = 1
        PAYMENT_PENDING = 2
        PAYMENT_DONE = 3
        PAYOUT_DONE = 4

    def __contains__(self, key):
        return key in self.data

    def get(self, key, default=None):
        return self.data.get(key)

    def __getitem__(self, key):
        return self.data[key]

    "For both"
    # Step 1: init
    def __init__(self,
            payment_provider, payment_currency,
            payout_provider, payout_currency,
            amount, payout_amount,
            payout_info=None,
            connection_info=None,
            ):

        self.data                     = dict()

        self.data["amount"]           = amount
        self.data["payout_amount"]    = payout_amount

        self.data["payment_provider"] = payment_provider
        self.data["payment_currency"] = payment_currency

        self.data["payout_provider"]  = payout_provider
        self.data["payout_currency"]  = payout_currency

        self.data["created_on"]       = datetime.now().strftime("%Y/%m/%d, %H:%M:%S.%f")

        self.data["status"]           = self.Status.CREATED

        self.data["connection_info"]  = connection_info
        if payout_info:
            self.data["payout_info"]      = payout_info
            self.data["status"]           = self.Status.PAYMENT_READY

        self.data["payment_id"]       = self.generate_payment_id(self.data)

    "Creation steps"
    # Step 2: Add user connection info
    def add_user_connection_info(self, pubkey, ip, port):
        self.data["payout_info"] = {
                'pubkey' : pubkey,
                'ip' : ip,
                'port' : port,
                }
        self.data["status"] = self.Status.PAYMENT_READY

    # Step 3: Add payment information
    def start_payment(self, payment_transaction_data):
        self.data["payment_transaction_data"] = payment_transaction_data
        self.data["payment_started_on"] = datetime.now().strftime("%Y/%m/%d, %H:%M:%S.%f")

        self.data["status"] = self.Status.PAYMENT_PENDING

    # Step 4: confirm_payment
    def confirm_payment(self, counterparty_account):
        self.data["counterparty_account"] = counterparty_account

        self.data["payment_confirmed_on"] = datetime.now().strftime("%Y/%m/%d, %H:%M:%S.%f")

        self.data["status"] = self.Status.PAYMENT_DONE

    # Step 4: Finish payout
    def payout_done(self, payout_transaction_id):
        self.data["payout_done_on"] = datetime.now().strftime("%Y/%m/%d, %H:%M:%S.%f")
        self.data["payout_transaction_id"] = payout_transaction_id
        self.data["status"] = self.Status.PAYOUT_DONE

    def get(self, key, default=None):
        if key in self.data:
            return self.data[key]
        else:
            return default

    def get_data(self):
        data = copy(self.data)
        return(data)

    def generate_payment_id(self, payment_data):
        """
        Seed for ID:
            - Creation date
            - Euro Amount
            - Euro Token Amount
            - Dest Wallet
        """
        relevant_data = {
                "timestamp"           : payment_data["created_on"],
                "amount"              : payment_data["amount"],
                "payout_amount"       : payment_data["payout_amount"],
                # "destination_account" : payment_data["payout_amount"],
                "rand"                : chr(random.randint(0, 2^64))
                }
        serialised = json.dumps(relevant_data, sort_keys=True, ensure_ascii=True).encode('utf-8')
        return base64.b64encode(hashlib.sha1(
            serialised
            ).digest()).decode("utf-8")


