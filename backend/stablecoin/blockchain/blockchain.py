from payment_system import PaymentSystem
from abc import abstractmethod


class Blockchain(PaymentSystem):

    @abstractmethod
    def get_identity(self, *args, **kwargs):
        pass

    @abstractmethod
    def __str__(self):
        pass

