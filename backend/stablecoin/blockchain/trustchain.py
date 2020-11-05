from stablecoin.bank.payment_system import PaymentSystem
from dataclasses                    import dataclass
from enum                           import Enum
from stablecoin.blockchain.ipv8     import MyTrustChainCommunity
from datetime                       import datetime

from binascii import hexlify, unhexlify

class TrustChain(PaymentSystem):

    @dataclass(unsafe_hash=True)
    class TrustChainPaymentRequest:
        class Status(Enum):
            PAYMENT_PENDING = 1
            PAYMENT_DONE = 2

        id: str
        amount: int
        timestamp: int
        wallet: str
        status: int = Status.PAYMENT_PENDING
        counterparty: str = None
        blockhash: str = None

    def __init__(self, identity, ipv8, address=("127.0.0.1", 8090)):
        self.trustchain = ipv8.get_overlay(MyTrustChainCommunity)
        self.identity = hexlify(self.trustchain.my_peer.public_key.key_to_bin())
        self.address = address
        self.payment_request_map = {}
        self.payout_log = {}
        self.last_id = 0

    def get_connection_info(self):
        return {
                'public_key' : self.identity,
                'ip' : self.address[0],
                'port' : self.address[1]
                }

    "OLD"

    "Payment side"

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

    "Payout side"

    "Step 2: Start the payout"
    #TODO
    def initiate_payment(self, account, amount):
        "Returns transaction_id if successful"

        public_key = account["pubkey"]
        ip = account["ip"]
        port = account["port"]

        now = datetime.now()

        transaction_id = self.get_new_id()

        # self.transactions[transaction_id] = {
        #         "type": "chain",
        #         "amount": amount,
        #         "timestamp": now,
        #         "status": "payout",
        #         "wallet": self.identity,
        #         "counterparty": account
        #         }

        # self.update_balance(account, amount)

        self.trustchain.send_test()

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

    def get_balance(self, wallet):
        return 1337

    def __str__(self):
        return "trustchain"

    def get_new_id(self):
        self.last_id += 1
        return self.last_id

