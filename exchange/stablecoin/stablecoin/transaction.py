from copy     import copy
from datetime import datetime
from enum     import Enum

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

    def __init__(self,
            payment_provider, payment_currency,
            payout_provider, payout_currency,
            amount, **kwargs):

        self.data = copy(kwargs)
        self.data["amount"] = amount

        self.data["payment_provider"] = payment_provider
        self.data["payment_currency"] = payment_currency

        self.data["payout_provider"] = payout_provider
        self.data["payout_currency"] = payout_currency

        self.data["created_on"] = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

        self.data["status"] = self.Status.CREATED

    def start_payment(self, payment_provider_id, payment_account, payout_account):
        self.data["payment_provider_id"] = payment_provider_id
        self.data["payment_account"] = payment_account
        self.data["payout_account"] = payout_account

        self.data["started_on"] = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

        self.data["status"] = self.Status.PAYMENT_PENDING

    def confirm_payment(self, counterparty_account):

        self.data["counterparty_account"] = counterparty_account

        self.data["payment_confirmed_on"] = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

        self.data["status"] = self.Status.PAYMENT_DONE

    def payout_done(self):
        self.data["payment_done_on"] = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

        self.data["status"] = self.Status.PAYOUT_DONE


