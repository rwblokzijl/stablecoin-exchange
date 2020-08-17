from stablecoin.bank.payment_system import PaymentSystem
from abc import abstractmethod
from datetime import datetime


class ChainStub(PaymentSystem):

    def __init__(self, *args, **kwargs):
        self.register_with_identity(*args, **kwargs)
        self.last_id = 0

        self.ledger = dict()
        """
        self.ledger = {
            "wallet": amount,
            ...
        }
        """

        self.transactions = dict()
        """
        self.transactions = {
            transaction_id: {
                "type":
                "amount":
                "timestamp":
                "status":
                "wallet":
                "counterparty":
            },
            ...
        }
        """

    def get_new_id(self):
        self.last_id += 1
        return self.last_id

    def register_with_identity(self, identity):
        self.identity = identity

    def get_identity(self, *args, **kwargs):
        return self.identity

    def __str__(self):
        return "ChainStub"

    def create_payment_request(self, amount):
        "Returns wallet address if successful"

        now = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

        transaction_id = self.get_new_id()

        self.transactions[transaction_id] = {
                "type": "chain",
                "amount": amount,
                "timestamp": now,
                "status": "open",
                "wallet": self.identity,
                "counterparty": None
                }

        return transaction_id

    def initiate_payment(self, account, amount):
        "Returns true if successful"
        now = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

        transaction_id = self.get_new_id()

        self.transactions[transaction_id] = {
                "type": "chain",
                "amount": amount,
                "timestamp": now,
                "status": "payout",
                "wallet": self.identity,
                "counterparty": account
                }
        return True

    def get_available_balance(self, identity):
        return 10000

    def list_transactions(self, dest_wallet):
        return self.transactions

    def update_balance(self, wallet, amount):
        if wallet not in self.ledger:
            self.ledger[wallet] = 0
        self.ledger[wallet] += amount

    def payment_done_trigger(self, transaction_id, counterparty):
        if transaction_id in self.transactions:
            "STUB WAY TO SUCCEED TRANSACTION"
            if self.transactions[transaction_id]["status"] != "successful":
                self.transactions[transaction_id]["status"] = "successful"
                self.transactions[transaction_id]["counterparty"] = "counterparty"

                self.update_balance( counterparty, self.transactions[transaction_id]["amount"] )

    def payment_request_status(self, transaction_id):
        if transaction_id in self.transactions:
            return self.transactions[transaction_id]["status"]
        else:
            return None




