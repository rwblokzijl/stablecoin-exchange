from stablecoin.blockchain.blockchain import Blockchain

class BlockchainStub(Blockchain):
    transactions = []
    def __str__(self):
        return "stub"

    def register_with_identity(self, pubkey):
        self.pubkey = pubkey

    def get_identity(self):
        return self.pubkey

    def transfer_funds(self, amount, wallet):
        self.balance -= amount
        self.transactions.append({
            "sender": self.pubkey,
            "receiver": wallet,
            "amount":amount
            })

    def set_balance(self, balance):
        self.balance = balance

    def get_balance(self):
        return self.balance

    def get_transactions(self):
        return self.transactions

    def generate_payment_request(self):
        pass

    def validate_payment_request(self):
        pass
