from stablecoin.bank.payment_system import PaymentSystem
from abc import abstractmethod


class Blockchain(PaymentSystem):

    def __init__(self, *args, **kwargs):
        self.register_with_identity(*args, **kwargs)

    @abstractmethod
    def register_with_identity(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_identity(self, *args, **kwargs):
        pass

    @abstractmethod
    def __str__(self):
        pass

