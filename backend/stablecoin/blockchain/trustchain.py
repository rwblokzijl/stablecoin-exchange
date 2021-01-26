from stablecoin.bank.payment_system                  import PaymentSystem
from dataclasses                                     import dataclass
from enum                                            import Enum
from stablecoin.blockchain.ipv8.eurotoken.community  import EuroTokenCommunity
from stablecoin.blockchain.ipv8.trustchain.community import MyTrustChainCommunity
from datetime                                        import datetime

from binascii import hexlify, unhexlify
import base64

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
        self.eurotoken  = ipv8.get_overlay(EuroTokenCommunity)
        self.eurotoken.set_callback_instance(self)
        self.trustchain.set_callback_instance(self)

        self.identity = self.trustchain.my_peer.public_key.key_to_bin().hex()
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

    def on_user_connection(self, payment_id, user_pk, user_ip, user_port ):
        self.stablecoin.CREATE_connect(payment_id, user_pk, user_ip, user_port)

    "OLD"

    "Payment side"

    def create_payment_request(self, amount):
        "Does nothing, simply returns connection info"
        return self.get_connection_info()

    def payment_request_status(self, pid):
        return False

    def on_payment(self, payment_id, amount, user_pk):
        return self.stablecoin.DESTROY_pay(payment_id, amount, user_pk)

    "Payout side"
    def attempt_payment_done(self, payment_id):
        pass

    "Step 2: Start the payout"
    #TODO return block id
    def initiate_payment(self, account, amount, payment_id):
        "Returns transaction_id if successful"

        print(account)

        public_key = account["pubkey"]
        ip = account["ip"]
        port = account["port"]

        now = datetime.now()

        # transaction_id = self.get_new_id()

        return self.trustchain.send_money(amount, public_key, ip, port, payment_id)

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

