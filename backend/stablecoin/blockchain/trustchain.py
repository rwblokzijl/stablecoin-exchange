from stablecoin.bank.payment_system import PaymentSystem
from dataclasses import dataclass
from enum     import Enum
from stablecoin.blockchain.ipv8 import TrustChainCommunity

class TrustChain(PaymentSystem):

    class Status(Enum):
        PAYMENT_PENDING = 1
        PAYMENT_DONE = 2

    @dataclass(unsafe_hash=True)
    class TrustChainPaymentRequest:
        id: str
        amount: int
        timestamp: int
        status: int = self.Status.PAYMENT_PENDING
        wallet: str
        counterparty: str = None
        blockhash: str = None

    def __init__(self):
        self.payment_request_map = {}
        self.payout_log = {}

        self.register_with_identity(*args, **kwargs)
        self.last_id = 0

    def __str__(self):
        return "trustchain"

    def get_new_id(self):
        self.last_id += 1
        return self.last_id

    def register_with_identity(self, identity):
        self.identity = identity

    def get_identity(self, *args, **kwargs):
        return self.identity

    "Payment end"

    "Step 0: Creation"
    #TODO
    def create_payment_request(self, amount):
        "Returns payment id if succesful"
        "does nothing, simply notes the amount in the DB with a unique ID"

        now = datetime.now()#.strftime("%Y/%m/%d, %H:%M:%S")

        transaction_id = self.get_new_id()

        self.payment_request_map[transaction_id] = TrustChainPaymentRequest(
                pid=transaction_id,
                amount=amount,
                timestamp=now,
                wallet=self.identity
                )

        return transaction_id


    "Step 1: Waiting"
    #TODO
    def payment_request_status(self, identifier):
        "Returns status of transaction???, will include payee when payment successful"
        return self.payment_request_map[identifier].status

    "Payout End"

    "Step 2: Start the payout"
    #TODO
    def initiate_payment(self, account, amount):
        "Returns transaction_id if successful"
        now = datetime.now()

        transaction_id = self.get_new_id()

        self.transactions[transaction_id] = {
                "type": "chain",
                "amount": amount,
                "timestamp": now,
                "status": "payout",
                "wallet": self.identity,
                "counterparty": account
                }
        self.update_balance(account, amount)
        return transaction_id

    "Bookkeeping functions"

    #TODO
    def list_transactions(self, account):
        pass

    #TODO
    def get_available_balance(self):
        pass

    "Blockchain Specific"

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
