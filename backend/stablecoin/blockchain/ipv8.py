from ipv8.attestation.trustchain.block     import TrustChainBlock, ValidationResult
from ipv8.attestation.trustchain.community import TrustChainCommunity
from ipv8.attestation.trustchain.listener  import BlockListener
from ipv8.community                        import Community
from ipv8.keyvault.crypto                  import ECCrypto
from ipv8.lazy_community                   import lazy_wrapper
from ipv8.messaging.lazy_payload           import VariablePayload, vp_compile
from ipv8.messaging.serialization          import Serializable

from ipv8.peer                             import Peer

from binascii import hexlify, unhexlify

INITIAL_BALANCE = 100

class EuroTokenBlockOld(TrustChainBlock):

    def __init__(self, *args, **kwargs):
        super(EuroTokenBlockOld, self).__init__(*args, **kwargs)
        self.balance = 100
        self.amount = self.transaction["amount"]

    def __str__(self):
        # This makes debugging and logging easier
        trans = self.transaction
        trans['sender'] = trans['sender'][-8:]
        trans['receiver'] = trans['receiver'][-8:]
        return "Block {0} from ...{1}:{2} links ...{3}:{4} for {5} type {6}".format(
                hexlify(self.hash)[-8:],
                hexlify(self.public_key)[-8:],
                self.sequence_number,
                hexlify(self.link_public_key)[-8:],
                self.link_sequence_number,
                trans,
                self.type)

        def balance(self, database):
            if self.transaction['sender'] == self.public_key:
                return self.transaction['balance']
            else:
                return self.get_sender_balance_from_chain_before_block(database) + self.transaction['amount']

    def get_sender_balance_from_chain_before_block(self, database):

        # TODO: This can be made more efficient
        # 1. include the receiver balance in the agreement somehow, else
        # 2. get the blocks in 1 query and loop over them
        " Get the balance of self.transaction[sender] at the point before this block "
        sender = self.transaction['sender']

        # self is first
        if self.sequence_number == 1:
            return INITIAL_BALANCE

        #add up all balances until last verified balance
        known_balance = 0
        check_block = database.get_block_before(self)
        while (check_block is not None and
                check_block.sequence_number != 1 and
                check_block.transaction['receiver'] != sender):
            # sender revieved money this block
            if check_block.type == b'transfer': #ignore wrong blocks
                known_balance += check_block.transaction['amount']
            check_block = database.get_block_before(check_block)
        if check_block is None:
            return None
        if check_block.sequence_number == 1:
            # We are at the genesis block
            known_balance += INITIAL_BALANCE
        else:
            # check_block is the last verified block
            known_balance += check_block.transaction['balance']

        return known_balance

    def validate_transaction(self, database):
        return ValidationResult.valid, []
    # link = database.get_linked(self)

        sender_trans_pub = unhexlify(self.transaction['sender'])
        receiv_trans_pub = unhexlify(self.transaction['receiver'])

        # Check if transaction ids matches block ids
        if (sender_trans_pub == self.public_key) and (receiv_trans_pub == self.link_public_key):
            # This is a proposal block
            pass
        elif (sender_trans_pub == self.link_public_key) and(receiv_trans_pub == self.public_key):
            # This is an agreement block
            pass
        else:
            # print("sender_trans_pub     ", sender_trans_pub)
            # print("receiv_trans_pub     ", receiv_trans_pub)

            # print("self.public_key      ", self.public_key)
            # print("self.link_public_key ", self.link_public_key)
            return ValidationResult.invalid, ["Transaction keys do not match block keys"]

        # Get senders balance
        sender_balance = self.get_sender_balance_from_chain_before_block(database)
        if sender_balance is None:
            return ValidationResult.partial_previous, ["Missing blocks"]

        if self.transaction['balance'] != sender_balance - self.transaction['amount']:
            return ValidationResult.invalid, [f"Inconsistent balance, block: ({self}), known_balance: ({sender_balance})"]
        if self.transaction['balance'] < 0:
            return ValidationResult.invalid, ["Insufficient funds"]
        return ValidationResult.valid, []

class EuroTokenDestructionBlock(TrustChainBlock):

    def __init__(self, *args, **kwargs):
        super(EuroTokenDestructionBlock, self).__init__(*args, **kwargs)
        self.balance = 100
        # self.amount = self.transaction["amount"]

class EuroTokenDestructionBlockListener(BlockListener):
    def __init__(self, my_peer, community):
        self.my_peer = my_peer
        self.community = community

    BLOCK_CLASS = EuroTokenDestructionBlock

    def should_sign(self, block):
        print("should_sign")
        if block.balance < 0: # TODO expand to the full range of validation: checkpoints included
            return False
        return True

    def received_block(self, block):
        print(block.public_key)
        self.community.eurotoken_blockchain.on_payment(
                block.transaction["payment_id"],
                block.transaction["amount"],
                "temp")

# class EuroTokenBlockListenerFail(BlockListener):
#     BLOCK_CLASS = EuroTokenBlock

#     def should_sign(self, block):
#         return False

class MyTrustChainCommunity(TrustChainCommunity):

    # master_peer = Peer(ECCrypto().generate_key(u"curve25519"))

    def __init__(self, *args, **kwargs):
        super(MyTrustChainCommunity, self).__init__(*args, **kwargs)
        self.add_listener(EuroTokenDestructionBlockListener(self.my_peer, self), [b'eurotoken_destruction'])
        # self.add_listener(EuroTokenBlockListenerFail(self.my_peer, self), [b'eurotoken_transfer']) # we dont accept transfers
        # self.balance = INITIAL_BALANCE

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

    def send_money(self, amount, public_key, ip, port):
        key = b"LibNaCLPK:" + public_key.encode('utf-8')
        peer = Peer( ECCrypto().key_from_public_bin(key) )
        peer.add_address((ip, port))
        return self.send_transaction_to_peer(peer, amount)

    def send_transaction_to_peer(self, peer, amount):
        return self.sign_block(peer, public_key=peer.public_key.key_to_bin(), block_type=b'eurotoken_creation', transaction={
            'amount': amount
            })

@vp_compile
class GatewayConnectMessage(VariablePayload):
    msg_id      = 1  # Gateway Connect message
    format_list = ["Q", "varlenI"]
    names       = ["global_time", "payment_id"]

class EuroTokenCommunity(Community):

    # import os
    community_id = bytes.fromhex("f0eb36102436bd55c7a3cdca93dcaefb08df0750")

    def __init__(self, my_peer, endpoint, network):
        super().__init__(my_peer, endpoint, network)
        # Register the message handler for messages with the identifier "1".
        self.add_message_handler(1, self.on_message)

    def set_callback_instance(self, eurotoken_blockchain):
        print("set eb")
        self.eurotoken_blockchain = eurotoken_blockchain

    def started(self):
        print("started eurotoken")
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



