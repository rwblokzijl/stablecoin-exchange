from pyipv8.ipv8.attestation.trustchain.community import synchronized
from pyipv8.ipv8.keyvault.crypto                  import default_eccrypto
from pyipv8.ipv8.peer                             import Peer

from blockchain.ipv8.trustchain.blocks.block_types import BlockTypes

from blockchain.ipv8.trustchain.community import MyTrustChainCommunity

from binascii import hexlify, unhexlify
import socket, random, os

from asyncio import sleep

def pretty_peer(peer):
    return hexlify(peer.public_key.key_to_bin())[-8:].decode("utf-8")

class EvalTrustChainCommunity(MyTrustChainCommunity):

    community_id = unhexlify('84c29a24fb2f7f9ca1a2109ee018589480153cab')

    def __init__(self, *args, **kwargs):
        self.is_gateway = kwargs.pop('is_gateway')
        self.key = kwargs.pop('key')
        self.already_sent = []

        gateway_key = kwargs.pop('gateway_key')
        with open(gateway_key, 'rb') as f:
            content = f.read()
        self.gateway_key = default_eccrypto.key_from_private_bin(content).pub()

        super(EvalTrustChainCommunity, self).__init__(*args, **kwargs)

    def get_gateway(self):
        return self.get_peer_from_public_key(self.gateway_key)

    async def started(self):
        print(f"My key: {pretty_peer(self.my_peer)}")

        if self.is_gateway:
            self.register_task("do_checkpoint", self.gateway_create_money_to_all, interval=5.0, delay=1.0)
        else:
            self.replace_task("send_random_money", self.send_random_money, interval=1, delay=1)

    @synchronized
    def request_checkpoint(self):
        gateway = self.get_gateway()
        my_balance = self.get_my_balance()
        self.pprint("V", my_balance, None, gateway)
        return self.sign_block(gateway, public_key=gateway.public_key.key_to_bin(), block_type=BlockTypes.CHECKPOINT, transaction={
            'balance': my_balance
            })

    def gateway_create_money_to_all(self, amount=100):
        for peer in self.get_peers():
            if peer not in self.already_sent:
                self.pprint("C", None, amount, peer)
                self.send_creation(peer, amount)
                self.already_sent.append(peer)

    def get_random_peer(self): #assumes 1 gateway
        peers = self.get_peers()

        if len(peers) == 0:
            return None

        if len(peers) == 1:
            peer = peers[0]
            # Dont return gateway
            if peer.public_key.key_to_bin() == self.gateway_key.key_to_bin():
                return None
            else:
                return peer

        first, second = random.sample(peers, 2)
        # Dont return gateway
        if first.public_key.key_to_bin() == self.gateway_key.key_to_bin():
            return second
        else:
            return first

    async def send_random_money(self, amount=5):
        peer = self.get_random_peer()
        if peer:
            return await self.eval_attempt_send_money(peer, amount)

    async def eval_attempt_send_money(self, peer, amount=5):
        with self.receive_block_lock:
            balance = self.get_my_balance() - amount
            verified_balance = self.get_my_verified_balance() - amount
        if balance < 0:
            return
        if verified_balance < 0:
            resp, prop = await self.request_checkpoint()
        await self.eval_send_money(peer, amount) #future

    @synchronized
    async def eval_send_money(self, peer, amount=5):
        my_balance = self.get_my_balance()
        verified_balance = self.get_my_verified_balance()
        if verified_balance < amount:
            print("INSUFFICIENT BALANCE")
            return
        balance = my_balance - amount
        self.pprint("T", my_balance, amount, peer)
        resp, prop = await self.sign_block(peer, public_key=peer.public_key.key_to_bin(), block_type=BlockTypes.TRANSFER, transaction={
            'amount': amount,
            'balance': balance
            })
        print(f"{prop}, {resp}")

    @synchronized
    def pprint(self, block_type, balance, amount, peer):
        bid = self.next_block_id()
        if type(balance) == int:
            balance = f"{balance: <4}"
        else:
            balance = "    "
        if type(amount) == int:
            amount = f"{amount: <4}"
        else:
            amount = "    "
        print (f"{bid} {block_type} ({balance}) - {amount} -> {pretty_peer(peer)}")

    def next_block_id(self):
        key = pretty_peer(self.my_peer)
        block = self.persistence.get_latest(self.my_peer.public_key.key_to_bin())
        if block is not None:
            seq = block.sequence_number + 1
        else:
            seq = 1
        return f"{key}:{seq: <4}"
