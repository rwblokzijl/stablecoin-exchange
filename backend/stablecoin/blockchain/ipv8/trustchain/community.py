from pyipv8.ipv8.attestation.trustchain.community import TrustChainCommunity
from pyipv8.ipv8.keyvault.crypto                  import default_eccrypto
from pyipv8.ipv8.peer                             import Peer
from pyipv8.ipv8.lazy_community                   import lazy_wrapper

from blockchain.ipv8.trustchain.blocks.block_types import BlockTypes

from blockchain.ipv8.trustchain.blocks.checkpoint  import EuroTokenCheckpointBlockListener
from blockchain.ipv8.trustchain.blocks.creation    import EuroTokenCreationBlockListener
from blockchain.ipv8.trustchain.blocks.destruction import EuroTokenDestructionBlockListener
from blockchain.ipv8.trustchain.blocks.transfer    import EuroTokenTransferBlockListener
from blockchain.ipv8.trustchain.blocks.rollback    import EuroTokenRollBackBlockListener

from binascii import hexlify, unhexlify

class MyTrustChainCommunity(TrustChainCommunity):

    def __init__(self, *args, **kwargs):
        s = super(MyTrustChainCommunity, self).__init__(*args, **kwargs)

        self.add_listener(EuroTokenCheckpointBlockListener(my_peer=self.my_peer, community=self), [BlockTypes.CHECKPOINT])
        self.add_listener(EuroTokenCreationBlockListener(my_peer=self.my_peer, community=self), [BlockTypes.CREATION])
        self.add_listener(EuroTokenDestructionBlockListener(my_peer=self.my_peer, community=self), [BlockTypes.DESTRUCTION])
        self.add_listener(EuroTokenTransferBlockListener(my_peer=self.my_peer, community=self), [BlockTypes.TRANSFER])
        self.add_listener(EuroTokenRollBackBlockListener(my_peer=self.my_peer, community=self), [BlockTypes.ROLLBACK])

        return s

    def set_callback_instance(self, eurotoken_blockchain):
        self.eurotoken_blockchain = eurotoken_blockchain

    def started(self): # entrypoint
        pass

    def get_my_latest_eurotoken(self, block=None):
        if block is None:
            block = self.persistence.get_latest(self.my_peer.public_key.key_to_bin())
        if block is None:
            return None
        elif block.public_key != self.my_peer.public_key.key_to_bin():
            raise Exception("This can only be called for yourself")
        if block.type in BlockTypes.EUROTOKEN_TYPES:
            return block
        return self.persistence.get_block_before(block)

    def get_my_balance(self):
        blk = self.get_my_latest_eurotoken()
        if blk is None:
            return 0
        return blk.get_balance(self.persistence)

    def get_my_verified_balance(self):
        blk = self.get_my_latest_eurotoken()
        if blk is None:
            return 0
        return blk.get_verified_balance(self.persistence)

    def get_peer_from_public_key(self, public_key):
        if type(public_key) == bytes:
            b = public_key
            key = default_eccrypto.key_from_public_bin(public_key)
        else:
            b = public_key.key_to_bin()
            key = public_key
        for peer in self.get_peers():
            if peer.public_key.key_to_bin() == b:
                return peer
        return Peer(key)

    def send_money(self, amount, public_key, ip, port, payment_id):
        peer = self.get_peer_from_public_key(unhexlify(public_key))
        peer.add_address((ip, port))
        return self.send_creation(peer, amount, payment_id)

    def send_creation(self, peer, amount, payment_id=""):
        return self.sign_block(peer, public_key=peer.public_key.key_to_bin(), block_type=BlockTypes.CREATION, transaction={
            'amount': amount,
            'payment_id': payment_id
            })

