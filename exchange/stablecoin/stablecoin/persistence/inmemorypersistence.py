from abc import ABC, abstractmethod

class InMemoryPersistence(ABC):

    def __init__(self):
        self.persistence = dict()
        """
        self.persistence = {
            "global_transaction_id": {
                "bank_transaction_id": bank_id,
                "chain_transaction_id": chain_id,
                ...
            }
        }
        """


    def __str__(self):
        return "In Memory Persistence"

    def get_payment_by_id(self, transaction_id):
        return self.persistence.get(transaction_id) or None

    def create_transaction(self, payment_data):
        pid = payment_data["payment_id"]
        if pid in self.persistence:
            print("WARNING: transaction with id exists, overwriting")
        self.persistence[pid] = payment_data

    def update_transaction(self, payment_data):
        pid = payment_data["payment_id"]
        if pid in self.persistence:
            self.persistence[pid] = payment_data
