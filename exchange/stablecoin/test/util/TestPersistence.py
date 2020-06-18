from stablecoin.persistence.persistence import Persistence

class TestPersistence(Persistence):
    payment_data = {
            }

    def __str__(self):
        return "TestPersistence"

    def create_transaction(self, payment_data):
        self.payment_data[payment_data["payment_id"]] = payment_data

    def get_payment_by_id(self, transaction_id):
        return self.payment_data[transaction_id]

