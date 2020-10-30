from abc import ABC, abstractmethod

class PaymentSystem(ABC):

    "Helpers"
    @abstractmethod
    def __str__(self):
        pass

    "Payment end"

    "Step 0: Creation"
    @abstractmethod
    def create_payment_request(self, amount):
        "Returns payment identifier string if succesful"

    "Step 1: Waiting"
    @abstractmethod
    def payment_request_status(self, identifier):
        "Returns status of transaction???, will include payee when payment successful"

    "Payout End"

    "Step 2: Start the payout"
    @abstractmethod
    def initiate_payment(self, account, amount):
        "Returns true if succesful"
        pass

    "Bookkeeping functions"

    @abstractmethod
    def list_transactions(self, account):
        pass

    @abstractmethod
    def get_available_balance(self):
        pass



