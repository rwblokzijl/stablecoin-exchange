from ipv8.attestation.trustchain.community import TrustChainCommunity
from ipv8.keyvault.crypto                  import ECCrypto
from ipv8.peer                             import Peer

from stablecoin.blockchain.ipv8.trustchain.blocks.checkpoint  import EuroTokenCheckpointBlockListener
from stablecoin.blockchain.ipv8.trustchain.blocks.creation    import EuroTokenCreationBlockListener
from stablecoin.blockchain.ipv8.trustchain.blocks.destruction import EuroTokenDestructionBlockListener
from stablecoin.blockchain.ipv8.trustchain.blocks.transfer    import EuroTokenTransferBlockListener

class MyTrustChainCommunity(TrustChainCommunity):

    # master_peer = Peer(ECCrypto().generate_key(u"curve25519"))

    def __init__(self, *args, **kwargs):
        super(MyTrustChainCommunity, self).__init__(*args, **kwargs)
        self.add_listener(EuroTokenCheckpointBlockListener(my_peer=self.my_peer, community=self), [self.BlockTypes.CHECKPOINT])
        self.add_listener(EuroTokenCreationBlockListener(my_peer=self.my_peer, community=self), [self.BlockTypes.CREATION])
        self.add_listener(EuroTokenDestructionBlockListener(my_peer=self.my_peer, community=self), [self.BlockTypes.DESTRUCTION])
        self.add_listener(EuroTokenTransferBlockListener(my_peer=self.my_peer, community=self), [self.BlockTypes.TRANSFER])

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
        key = b"LibNaCLPK:" + public_key.encode('utf-8')
        peer = Peer( ECCrypto().key_from_public_bin(key) )
        peer.add_address((ip, port))
        return self.send_transaction_to_peer(peer, amount, payment_id)

    def get_known_balance_for_peer(self, peer):
        latest = get_latest_blocks(self, peer.public_key, limit=1, block_types=[ self.BlockTypes.CHECKPOINT,
            self.BlockTypes.CREATION, self.BlockTypes.DESTRUCTION, self.BlockTypes.TRANSFER ])
        if len(latest)==1:
            return latest[0].transaction['balance']
        else:
            return 0

    def send_transaction_to_peer(self, peer, amount, payment_id):
        balance = self.get_known_balance_for_peer(self, peer)
        return self.sign_block(peer, public_key=peer.public_key.key_to_bin(), block_type=self.BlockTypes.CREATION, transaction={
            'amount': amount,
            'balance': balance,
            'payment_id': payment_id
            })

    class BlockTypes:
        DESTRUCTION = b'eurotoken_destruction'
        CHECKPOINT  = b'eurotoken_checkpoint'
        CREATION    = b'eurotoken_creation'
        TRANSFER    = b'eurotoken_transfer'


