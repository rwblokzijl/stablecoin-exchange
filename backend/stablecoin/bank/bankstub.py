from stablecoin.bank.bank import Bank
from enum import Enum

from datetime import datetime

class BankStub(Bank):

    class Status(Enum):
        PAYMENT_PENDING = 0
        PAYMENT_DONE = 0

    def __init__(self):
        self.account = "FAKEIBAN"
        self.transactions = dict()
        self.last_id = 0
        """
        self.transactions = {
            transaction_id: {
                "type":
                "amount":
                "timestamp":
                "status":
                "account":
                "counterparty":
            },
            ...
        }
        """

    def __str__(self):
        return "BankStub"

    "Creation Step 3"
    def create_payment_request(self, amount):
        "Returns payment destiation if successful"

        now = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

        transaction_id = self.get_new_id()

        self.transactions[transaction_id] = {
                "type":         "bank",
                "amount":       amount,
                "timestamp":    now,
                "status":       self.Status.PAYMENT_PENDING,
                "account":      self.account,
                "counterparty": None
                }

        return transaction_id

    "Creation Step 3.5, the user pays" # TODO, REMOVE, this is for testing
    def payment_done_trigger(self, transaction_id, counterparty):
        if transaction_id in self.transactions:
            "STUB WAY TO SUCCEED TRANSACTION"
            if self.transactions[transaction_id]["status"] != self.Status.PAYMENT_DONE:
                self.transactions[transaction_id]["status"] = self.Status.PAYMENT_DONE
                self.transactions[transaction_id]["counterparty"] = counterparty
            return self.transactions[transaction_id]
        else:
            print("No such transaction")
            return None

    "Creation Step 4"
    def attempt_payment_done(self, transaction_id):
        if transaction_id in self.transactions:
            "STUB WAY TO SUCCEED TRANSACTION"
            if self.transactions[transaction_id]["status"] == self.Status.PAYMENT_DONE:
                return self.transactions[transaction_id]["counterparty"]
            else:
                print("Not confirmed yet")
                return None
        else:
            print("No such transaction")
            return None

    def initiate_payment(self, account, amount):
        "Returns transaction_id if successful"
        now = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

        transaction_id = self.get_new_id()

        self.transactions[transaction_id] = {
                "type":         "bank",
                "amount":       amount,
                "timestamp":    now,
                "status":       self.Status.PAYMENT_PENDING,
                "account":      self.account,
                "counterparty": account
                }
        return transaction_id

    def get_available_balance(self):
        return 10000

    def list_transactions(self, dest_wallet):
        return self.transactions

    def payment_request_status(self, transaction_id):
        if transaction_id in self.transactions:
            return self.transactions[transaction_id]["status"]
        return None

    def get_new_id(self):
        self.last_id += 1
        return self.last_id

