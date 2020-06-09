from abc import ABC, abstractmethod

class Bank(ABC):

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def create_payment_request(self, amount):
        pass

    @abstractmethod
    def initiate_payment(self, account, amount):
        pass

