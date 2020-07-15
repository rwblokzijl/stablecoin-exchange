from stablecoin.blockchain.blockchain import Blockchain

class TrustChain(Blockchain):

    def __str__(self):
        return "trustchain"

    def get_identity(self):
        return self.identity

    def get_available_balance(self):
        pass

    def create_payment_request(self):
        pass

    def initiate_payment(self):
        pass

    def list_transactions(self):
        return list()

    def payment_request_status(self, payment_id):
        pass

    def register_with_identity(self, identity):
        self.identity = identity
