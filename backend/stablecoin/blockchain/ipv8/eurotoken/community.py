from pyipv8.ipv8.community                        import Community
from pyipv8.ipv8.lazy_community                   import lazy_wrapper

from blockchain.ipv8.eurotoken.message import GatewayConnectMessage

class EuroTokenCommunity(Community):

    # import os
    community_id = bytes.fromhex("f0eb36102436bd55c7a3cdca93dcaefb08df0750")

    def __init__(self, my_peer, endpoint, network):
        s = super().__init__(my_peer, endpoint, network)
        # Register the message handler for messages with the identifier "1".
        self.add_message_handler(1, self.on_message)
        return s

    def set_callback_instance(self, eurotoken_blockchain):
        self.eurotoken_blockchain = eurotoken_blockchain

    def started(self):
        self.logger.warning("started eurotoken")
        async def start_communication():
            peers = self.get_peers()
            print( str(len(peers)) + " EuroToken peers")
            for peer in peers:
                print(peer)
                # self.send_transaction(peer, 5)
        # self.register_task("start_communication", start_communication, interval=5.0, delay=0)

    @lazy_wrapper(GatewayConnectMessage)
    def on_message(self, peer, payload):
        payment_id = payload.payment_id.decode('utf-8')
        pubkey = peer.public_key.key_to_bin().hex()

        self.eurotoken_blockchain.on_user_connection(payment_id, pubkey, peer.address[0], peer.address[1])



