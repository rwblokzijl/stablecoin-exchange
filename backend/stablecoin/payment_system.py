from abc import ABC, abstractmethod

class PaymentSystem(ABC):

    "Set the stablecoin instance"
    def set_callback_instance(self, stablecoin_instance):
        self.stablecoin = stablecoin_instance

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

    "Step 4: Validate the request"
    @abstractmethod
    def attempt_payment_done(self):
        pass

    "Step 4: Start the payout"
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



