from abc import ABC, abstractmethod

class Persistence(ABC):

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def get_payment_by_id(self, transaction_id):
        pass

    @abstractmethod
    def create_transaction(self, payment_data):
        pass
