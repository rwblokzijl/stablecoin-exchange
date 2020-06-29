from abc import ABC, abstractmethod

class PaymentSystem(ABC):

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def create_payment_request(self, amount):
        pass

    @abstractmethod
    def initiate_payment(self, account, amount):
        pass

    @abstractmethod
    def get_available_balance(self):
        pass

    @abstractmethod
    def list_transactions(self, dest_wallet):
        pass

    @abstractmethod
    def payment_request_status(self):
        pass




