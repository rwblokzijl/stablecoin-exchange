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
        return self.data.get(key, default)

    def __getitem__(self, key):
        return self.data[key]

    "For both"
    # Step 1: init
    def __init__(self,
            payment_provider, payment_currency,
            payout_provider, payout_currency,
            amount, payout_amount,
            gateway_connection_data,
            payout_connection_data=None
            ):

        self.data                             = dict()

        self.data["amount"]                   = amount
        self.data["payout_amount"]            = payout_amount

        self.data["payment_provider"]         = payment_provider
        self.data["payment_currency"]         = payment_currency

        self.data["payout_provider"]          = payout_provider
        self.data["payout_currency"]          = payout_currency

        self.data["created_on"]               = datetime.now().strftime("%Y/%m/%d, %H:%M:%S.%f")

        self.data["status"]                   = self.Status.CREATED

        self.data["gateway_connection_data"] = gateway_connection_data

        if payout_connection_data:
            self.data["payout_connection_data"]  = payout_connection_data
            self.data["status"]                  = self.Status.PAYMENT_READY

        self.data["payment_id"]               = self.generate_payment_id(self.data)

    "Creation step"
    # Step 2: Add user connection info
    def add_payout_connection_data(self, payout_connection_data):
        self.data["payout_connection_data"] = payout_connection_data
        self.data["status"] = self.Status.PAYMENT_READY

    # Step 3: Add payment information
    def start_payment(self, payment_connection_data):
        self.data["payment_connection_data"]  = payment_connection_data
        self.data["payment_started_on"]       = datetime.now().strftime("%Y/%m/%d, %H:%M:%S.%f")

        self.data["status"]                   = self.Status.PAYMENT_PENDING

    # Step 4.1: confirm_payment
    def confirm_payment(self, payment_transaction_data):
        self.data["payment_transaction_data"] = payment_transaction_data
        self.data["payment_confirmed_on"]     = datetime.now().strftime("%Y/%m/%d, %H:%M:%S.%f")

        self.data["status"]                   = self.Status.PAYMENT_DONE

    # Step 4.2: Finish payout
    def payout_done(self, payout_transaction_data):
        self.data["payout_transaction_data"] = payout_transaction_data
        self.data["payout_done_on"]          = datetime.now().strftime("%Y/%m/%d, %H:%M:%S.%f")

        self.data["status"]                  = self.Status.PAYOUT_DONE

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

    def clean_status(self):
        if self["status"] == Transaction.Status.CREATED:
            return "Transaction created"
        elif self["status"] == Transaction.Status.PAYMENT_READY:
            return "Ready for payment"
        elif self["status"] == Transaction.Status.PAYMENT_PENDING:
            return "Waiting for payment"
        elif self["status"] == Transaction.Status.PAYMENT_DONE:
            return "Payment Done"
        elif self["status"] == Transaction.Status.PAYOUT_DONE:
            return "Payout Done"
        else:
            return "Invalid Status"

    def __str__(self):
        return str(self.serialise())

    def serialise(self):
        return {
            "status_text":              self.clean_status(),
            "status":                   self["status"].value,
            "created":                  self['created_on'],
            "payment_amount":           self['amount'],
            "payout_amount":            self['payout_amount'],
            "payment_currency":         self['payment_currency'],
            "payout_currency":          self['payout_currency'],
            "payment_id":               self['payment_id'],

            "gateway_connection_data":  self.get('gateway_connection_data', None),

            "payment_connection_data":  self.get('payment_connection_data', None),
            "payment_started_on":       self.get('payment_started_on', None),

            "payment_transaction_data": self.get('payment_transaction_data', None),
            "payment_confirmed_on":     self.get('payment_confirmed_on', None),

            "payout_connection_data":   self.get('payout_connection_data', None),
            "payout_transaction_data":  self.get('payout_transaction_data', None),
            "payout_done_on":           self.get('payout_done_on', None),
            }


