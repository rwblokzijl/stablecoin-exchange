from copy     import copy
from datetime import datetime
from enum     import Enum

import json
import base64
import hashlib

class Transaction:
    class Status(Enum):
        CREATED = 0
        PAYMENT_PENDING = 1
        PAYMENT_DONE = 2
        PAYOUT_DONE = 3

    def __contains__(self, key):
        return key in self.data

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        if key in self.data:
            return self.data[key]
        else:
            return default

    def get_data(self):
        data = copy(self.data)
        return(data)

    def __init__(self,
            payment_provider, payment_currency,
            payout_provider, payout_currency,
            payout_account,
            amount, payout_amount
            ):

        self.data = dict()
        self.data["amount"] = amount
        self.data["payout_amount"] = payout_amount

        self.data["payment_provider"] = payment_provider
        self.data["payment_currency"] = payment_currency

        self.data["payout_provider"] = payout_provider
        self.data["payout_currency"] = payout_currency

        self.data["created_on"] = datetime.now().strftime("%Y/%m/%d, %H:%M:%S.%f")

        self.data["status"] = self.Status.CREATED

        self.data["payout_account"] = payout_account

        self.data["payment_id"]             = self.generate_payment_id(self.data)

    def start_payment(self, payment_provider_id, expected_payment_account, temp_counterparty=None):
        self.data["payment_provider_id"] = payment_provider_id
        self.data["expected_payment_account"] = expected_payment_account
        self.data["counterparty_account"] = temp_counterparty

        self.data["started_on"] = datetime.now().strftime("%Y/%m/%d, %H:%M:%S.%f")

        self.data["status"] = self.Status.PAYMENT_PENDING

    def confirm_payment(self, counterparty_account):

        self.data["counterparty_account"] = counterparty_account

        self.data["payment_confirmed_on"] = datetime.now().strftime("%Y/%m/%d, %H:%M:%S.%f")

        self.data["status"] = self.Status.PAYMENT_DONE

    def payout_done(self, payout_transaction_id):
        self.data["payment_done_on"] = datetime.now().strftime("%Y/%m/%d, %H:%M:%S.%f")

        self.data["payout_transaction_id"] = payout_transaction_id

        self.data["status"] = self.Status.PAYOUT_DONE

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
                "destination_account" : payment_data["payout_account"],
                }
        serialised = json.dumps(relevant_data, sort_keys=True, ensure_ascii=True).encode('utf-8')
        return base64.b64encode(hashlib.sha1(
            serialised
            ).digest()).decode("utf-8")


