from pyipv8.ipv8.attestation.trustchain.block     import EMPTY_PK, ValidationResult
from pyipv8.ipv8.attestation.trustchain.community import synchronized
from pyipv8.ipv8.keyvault.crypto                  import default_eccrypto
from pyipv8.ipv8.peer                             import Peer
from pyipv8.ipv8.util                             import succeed

from blockchain.ipv8.trustchain.blocks.block_types import BlockTypes

from blockchain.ipv8.trustchain.community     import MyTrustChainCommunity
from blockchain.ipv8.trustchain.eval_database import EvalTrustChainDB

from binascii import hexlify, unhexlify
import socket, random, os

from asyncio import sleep

def pretty_peer(peer):
    if type(peer) == Peer:
        peer = peer.public_key.key_to_bin()
    return hexlify(peer)[-8:].decode("utf-8")

def pretty_block(block):
    return pretty_peer(block.public_key) + f":{block.sequence_number: <4}"

class EvalTrustChainCommunity(MyTrustChainCommunity):

    community_id = unhexlify('84c29a24fb2f7f9ca1a2109ee018589480153cab')
    DB_CLASS = EvalTrustChainDB

    def __init__(self, *args, **kwargs):
        self.is_gateway = kwargs.pop('is_gateway')
        self.key_file   = kwargs.pop('key_file')
        self.n_gateways = kwargs.pop('n_gateways')
        self.n_clients  = kwargs.pop('n_clients')
        self.crawl_counter = {}

        self.n_peers    = self.n_gateways+self.n_clients
        self.already_sent = []

        super(EvalTrustChainCommunity, self).__init__(*args, **kwargs)

    async def wait_for_peer_keys(self):
        all_keys = os.listdir("/vol/keys/")
        while len(all_keys) != self.n_peers: # wait for all gateways and peers to generate their keys
            await sleep(0.1)
            all_keys = os.listdir("/vol/keys/")

    def send_crawl_request(self, peer, public_key, start_seq_num, end_seq_num, for_half_block=None):
        if for_half_block:
            self.crawl_counter[for_half_block.block_id] = self.crawl_counter.get(for_half_block.block_id, 0) + 1
        return super(EvalTrustChainCommunity, self).send_crawl_request(peer, public_key, start_seq_num, end_seq_num, for_half_block)

    def log_extra_validate(self, block):
        self.persistence.reset_counter()
        block.validate(self.persistence)
        val = self.persistence.counter
        self.persistence.reset_counter()
        block.validate_transaction(self.persistence)
        trans = self.persistence.counter
        self.persistence.reset_counter()
        return val, trans

    def sign_block(self, peer, public_key=EMPTY_PK, block_type=b'unknown', transaction=None, linked=None, additional_info=None):
        if linked and linked.block_id in self.crawl_counter:
            print(f"{pretty_block(linked)} M {self.crawl_counter[linked.block_id]}")
            del self.crawl_counter[linked.block_id]
            ans = self.log_extra_validate(linked)
            print(f"{pretty_block(linked)} D {ans[0]}")
            print(f"{pretty_block(linked)} E {ans[1]}")
        return super(EvalTrustChainCommunity, self).sign_block(peer, public_key, block_type, transaction, linked, additional_info)

    def set_gateway(self):
        """
        the gateway_index = client_index % n_gateways
        """
        all_keys = os.listdir("/vol/keys/")
        all_keys.sort()
        my_index = all_keys.index(self.key_file)
        gateway_key = "/vol/keys/" + all_keys[self.n_clients + my_index%self.n_gateways]

        with open(gateway_key, 'rb') as f:
            content = f.read()
        self.gateway_key = default_eccrypto.key_from_private_bin(content).pub()

    def set_clients(self):
        """
        All clients where my_index = client_index % n_gateways
        """
        self.my_clients = []
        all_keys = os.listdir("/vol/keys/")
        all_keys.sort()
        my_index = all_keys.index(self.key_file) - self.n_clients
        for n in range(self.n_clients):
            if n % self.n_gateways == my_index:
                client_key = "/vol/keys/" + all_keys[n]

                with open(client_key, 'rb') as f:
                    content = f.read()
                self.my_clients.append(default_eccrypto.key_from_private_bin(content).pub())

    def set_valid_peers(self):
        self.valid_peers = []
        all_keys = os.listdir("/vol/keys/")
        all_keys.sort()
        for n in range(self.n_clients):
            client_key = all_keys[n]
            if client_key == self.key_file:
                continue
            with open("/vol/keys/" + client_key, 'rb') as f:
                content = f.read()
            self.valid_peers.append(default_eccrypto.key_from_private_bin(content).pub())

    def get_gateway(self):
        return self.get_peer_from_public_key(self.gateway_key)

    async def started(self):
        await self.wait_for_peer_keys()

        if self.is_gateway:
            self.set_clients()
            print(f"My key:     {pretty_peer(self.my_peer)}")
            for client in self.my_clients:
                print(f"Client: {pretty_peer(self.get_peer_from_public_key(client))}")

        else:
            self.set_gateway()
            self.set_valid_peers()
            print(f"My key:     {pretty_peer(self.my_peer)}")
            print(f"My gateway: {pretty_peer(self.get_gateway())}")
            for client in self.valid_peers:
                print(f"Peer: {pretty_peer(self.get_peer_from_public_key(client))}")


        if self.is_gateway:
            self.register_task("do_checkpoint", self.gateway_create_money_to_all, interval=5.0, delay=1.0)
        else:
            self.replace_task("send_random_money", self.send_random_money, interval=1, delay=1)

    @synchronized
    def eval_send_money(self, peer, amount=5):
        my_balance = self.get_my_balance()
        if my_balance < amount:
            self._logger.error("INSUFFICIENT BALANCE") #only happens in tight race condition
            return succeed(None, None) # stop processing, but dont error
        verified_balance = self.get_my_verified_balance()
        if verified_balance < amount:
            self._logger.error("INSUFFICIENT BALANCE") #only happens in tight race condition
            return succeed(None, None) # stop processing, but dont error
        return self.sign_block(peer, public_key=peer.public_key.key_to_bin(), block_type=BlockTypes.TRANSFER, transaction={
            'amount': amount,
            'balance': my_balance - amount
            })

    @synchronized
    def request_checkpoint(self):
        gateway = self.get_gateway()
        my_balance = self.get_my_balance()
        return self.sign_block(gateway, public_key=gateway.public_key.key_to_bin(), block_type=BlockTypes.CHECKPOINT, transaction={
            'balance': my_balance
            })

    async def gateway_create_money_to_all(self, amount=100):
        for client in self.my_clients:
            if client not in self.already_sent:
                peer = self.get_peer_from_public_key(client)
                # self.pprint("C", None, amount, peer=peer)
                resp, prop = await self.send_creation(peer, amount)
                self.pprint("C", None, amount, resp, prop)
                self.already_sent.append(client)

    def get_random_peer(self):
        client = random.choice(self.valid_peers)
        return self.get_peer_from_public_key(client)

    async def send_random_money(self, amount=5):
        peer = self.get_random_peer()
        if peer:
            return await self.eval_attempt_send_money(peer, amount)

    async def eval_attempt_send_money(self, peer, amount=5):
        with self.receive_block_lock:
            my_balance = self.get_my_balance()
            verified_balance = self.get_my_verified_balance() - amount
        if my_balance < amount:
            return
        if verified_balance < 0:
            # self.pprint("V", my_balance, amount, peer=peer)
            resp, prop = await self.request_checkpoint()
            self.pprint("V", my_balance, None, resp, prop)
        # self.pprint("T", my_balance - amount, amount, peer=peer)
        resp, prop = await self.eval_send_money(peer, amount) #future
        self.pprint("T", my_balance - amount, amount, resp, prop)

    def pprint(self, block_type, balance, amount, resp=None, prop=None, peer=None):
        if not any([prop, peer, resp]):
            self._logger.error("CANCELED")
            return

        if prop:
            fr = pretty_peer(prop.public_key) + f":{prop.sequence_number: <4}"
        else:
            fr = self.next_block_id()

        if resp:
            to = pretty_peer(resp.public_key) + f":{resp.sequence_number: <4}"
        else:
            to = pretty_peer(peer) + ":?"

        if type(balance) == int:
            balance = f"{balance: <4}"
        else:
            balance = "    "
        if type(amount) == int:
            amount = f"{amount: <4}"
        else:
            amount = "    "
        print (f"{fr} {block_type} {balance} - {amount} -> {to}")

    def next_block_id(self):
        key = pretty_peer(self.my_peer)
        block = self.persistence.get_latest(self.my_peer.public_key.key_to_bin())
        if block is not None:
            seq = block.sequence_number + 1
        else:
            seq = 1
        return f"{key}:{seq: <4}"
