from py-ipv8.ipv8.attestation.community import TrustChainCommunity
from ipv8.keyvault.crypto                  import ECCrypto
from ipv8.peer                             import Peer
from ipv8.lazy_community                   import lazy_wrapper

from blockchain.ipv8.trustchain.blocks.block_types import BlockTypes

from blockchain.ipv8.trustchain.blocks.checkpoint  import EuroTokenCheckpointBlockListener
from blockchain.ipv8.trustchain.blocks.creation    import EuroTokenCreationBlockListener
from blockchain.ipv8.trustchain.blocks.destruction import EuroTokenDestructionBlockListener
from blockchain.ipv8.trustchain.blocks.transfer    import EuroTokenTransferBlockListener

from blockchain.ipv8.trustchain.db_helper import get_balance_for_block, get_block_balance_change

from binascii import hexlify, unhexlify

class MyTrustChainCommunity(TrustChainCommunity):

    # master_peer = Peer(ECCrypto().generate_key(u"curve25519"))

    def __init__(self, *args, **kwargs):
        s = super(MyTrustChainCommunity, self).__init__(*args, **kwargs)
        self.add_listener(EuroTokenCheckpointBlockListener(my_peer=self.my_peer, community=self), [BlockTypes.CHECKPOINT])
        self.add_listener(EuroTokenCreationBlockListener(my_peer=self.my_peer, community=self), [BlockTypes.CREATION])
        self.add_listener(EuroTokenDestructionBlockListener(my_peer=self.my_peer, community=self), [BlockTypes.DESTRUCTION])
        self.add_listener(EuroTokenTransferBlockListener(my_peer=self.my_peer, community=self), [BlockTypes.TRANSFER])

        return s

        # self.eurotoken_blockchain.on_user_connection(payment_id, pubkey, peer.address[0], peer.address[1])

    # def

    def set_callback_instance(self, eurotoken_blockchain):
        self.eurotoken_blockchain = eurotoken_blockchain

    def started(self):
        # pass
        async def start_communication():
            peers = self.get_peers()
            print("N. peers: " + str(len(peers)))
            for peer in peers:
                print(peer)
                # self.send_transaction(peer, 5)
        # self.register_task("start_communication", start_communication, interval=5.0, delay=0)

    def send_money(self, amount, public_key, ip, port, payment_id):
        # key = b"LibNaCLPK:" + bytes.fromhex(public_key)
        key = bytes.fromhex(public_key)
        peer = Peer( ECCrypto().key_from_public_bin(key) )
        peer.add_address((ip, port))
        return self.send_transaction_to_peer(peer, amount, payment_id)

    def get_known_balance_for_peer(self, peer):
        key = b"LibNaCLPK:" + peer.public_key.key_to_bin()
        latest = self.persistence.get_latest_blocks(key, limit=1, block_types=BlockTypes.EUROTOKEN_TYPES)
        if len(latest)==1:
            return get_balance_for_block(latest[0], self.persistence)
        else:
            return 0

    def send_transaction_to_peer(self, peer, amount, payment_id):
        # we dont know where the balance gets accepted in the receiver chain, so we dont know the balance
        # balance = amount + self.get_known_balance_for_peer(peer)
        return self.sign_block(peer, public_key=peer.public_key.key_to_bin(), block_type=BlockTypes.CREATION, transaction={
            'amount': amount,
            # 'balance': balance
            'payment_id': payment_id
            })

