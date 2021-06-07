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

from asyncio import sleep, wait
import time
from pathlib import Path

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
        self.base_dir                      = kwargs.pop('base_dir')
        self.sync_dir                      = os.path.join(self.base_dir, 'sync/')
        self.keys_dir                      = os.path.join(self.base_dir, 'keys/')

        self.is_gateway                    = kwargs.pop('is_gateway')
        self.key_file                      = kwargs.pop('key_file')
        self.n_gateways                    = kwargs.pop('n_gateways')
        self.n_clients                     = kwargs.pop('n_clients')
        self.transactions_to_do            = kwargs.pop('transactions_to_do')
        self.min_checkpoint_freq           = kwargs.pop('min_checkpoint_freq')
        self.tps_test                      = kwargs.pop('tps_test')

        self.crawl_counter                 = {}
        self.transactions_sent             = 0
        self.transactions_since_checkpoint = 0
        self.test_amount                   = 5
        self.has_money                     = False

        self.n_peers                       = self.n_gateways+self.n_clients
        self.already_sent                  = []

        super(EvalTrustChainCommunity, self).__init__(*args, **kwargs)

    def set_stop(self, stop):
        self.stop = stop

    async def sync_peers(self, sync_id, wait=0.1, print=lambda *args: None):
        print("sync: " + sync_id)
        (Path(self.sync_dir) / Path(sync_id+ "_"+self.key_file)).touch()

        all_files = [filename for filename in os.listdir(self.sync_dir) if filename.startswith(sync_id+"_")]
        print(all_files)
        while len(all_files) != self.n_peers: # wait for all gateways and peers to generate their files
            print(all_files)
            await sleep(wait)
            all_files = [filename for filename in os.listdir(self.sync_dir) if filename.startswith(sync_id+"_")]
        # os.remove(self.sync_dir +sync_id+ "_"+self.key_file)
        print("done: " + sync_id)

    def sync_next(self, sync_id, name, task, interval=None, delay=None, wait=1, print=lambda *args: None):
        print("sync: " + sync_id)
        (Path(self.sync_dir) / Path(sync_id+ "_"+self.key_file)).touch()

        def attempt_ready():
            all_files = [filename for filename in os.listdir(self.sync_dir) if filename.startswith(sync_id+"_")]
            if len(all_files) == self.n_peers: # wait for all gateways and peers to generate their files
                self.replace_task(sync_id, lambda: None)
                self.register_task(name, task, interval=interval, delay=delay)
            else:
                print(all_files)

        self.register_task(sync_id, attempt_ready, interval=wait)

        # os.remove(self.sync_dir +sync_id+ "_"+self.key_file)
        print("done: " + sync_id)

    def send_crawl_request(self, peer, public_key, start_seq_num, end_seq_num, for_half_block=None):
        if for_half_block:
            self.crawl_counter[for_half_block.block_id] = self.crawl_counter.get(for_half_block.block_id, 0) + 1
        return super(EvalTrustChainCommunity, self).send_crawl_request(peer, public_key, start_seq_num, end_seq_num, for_half_block)

    def measure_database_and_time(self, func, *args, **kwargs):
        self.persistence.reset_counter()

        t = time.process_time()
        func(*args, **kwargs)
        elapsed_time = time.process_time() - t

        database_lookups = self.persistence.counter
        self.persistence.reset_counter()
        return database_lookups, elapsed_time

    def time_last_validate(self, block):
        n_crawled = self.crawl_counter.pop(block.block_id, 0)
        db_lookups, processing_time = self.measure_database_and_time(block.validate_transaction, self.persistence)
        if self.is_gateway:
            total_time_p = time.process_time() - self.start_time_p
            total_time = time.time() - self.start_time
        else:
            total_time_p = 0
            total_time = 0
        print(f"{pretty_block(block)} M {n_crawled} E {db_lookups} {processing_time} TT {total_time}/{total_time_p}")

    def sign_block(self, peer, public_key=EMPTY_PK, block_type=b'unknown', transaction=None, linked=None, additional_info=None):
        if linked:
            self.time_last_validate(linked)
        ans = super(EvalTrustChainCommunity, self).sign_block(peer, public_key, block_type, transaction, linked, additional_info)
        return ans

    def set_gateway(self):
        """
        the gateway_index = client_index % n_gateways
        """
        all_keys = os.listdir(self.keys_dir)
        all_keys.sort()
        my_index = all_keys.index(self.key_file)
        gateway_key = self.keys_dir + all_keys[self.n_clients + my_index%self.n_gateways]

        with open(gateway_key, 'rb') as f:
            content = f.read()
        self.gateway_key = default_eccrypto.key_from_private_bin(content).pub()

    def get_delay(self):
        all_keys = os.listdir(self.keys_dir)
        all_keys.sort()
        return all_keys.index(self.key_file) / self.n_clients

    def set_clients(self):
        """
        All clients where my_index = client_index % n_gateways
        """
        self.my_clients = []
        all_keys = os.listdir(self.keys_dir)
        all_keys.sort()
        my_index = all_keys.index(self.key_file) - self.n_clients
        for n in range(self.n_clients):
            if n % self.n_gateways == my_index:
                client_key = self.keys_dir + all_keys[n]

                with open(client_key, 'rb') as f:
                    content = f.read()
                self.my_clients.append(default_eccrypto.key_from_private_bin(content).pub())

    def set_valid_peers(self):
        self.valid_peers = []
        all_keys = os.listdir(self.keys_dir)
        all_keys.sort()
        for n in range(self.n_clients):
            client_key = all_keys[n]
            if client_key == self.key_file:
                continue
            with open(self.keys_dir + client_key, 'rb') as f:
                content = f.read()
            self.valid_peers.append(default_eccrypto.key_from_private_bin(content).pub())

    def get_gateway(self):
        return self.get_peer_from_public_key(self.gateway_key)

    async def started(self):
        await self.sync_peers("startup")

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

        await self.sync_peers("wait_for_config")

        self.start_time = 0

        if self.is_gateway:
            self.register_task("create_money", self.gateway_create_money_to_all, delay=2+self.get_delay())
        else:
            if self.tps_test:
                self.sync_next("await_money", "run_test", self.run_stress_test, delay=1)
            else:
                self.sync_next("await_money", "run_test", self.run_normal_test)

    @synchronized
    def eval_send_money(self, peer, amount=None):
        amount=amount or self.test_amount
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
        self.transactions_since_checkpoint = 0
        gateway = self.get_gateway()
        my_balance = self.get_my_balance()
        return self.sign_block(gateway, public_key=gateway.public_key.key_to_bin(), block_type=BlockTypes.CHECKPOINT, transaction={
            'balance': my_balance
            })

    async def gateway_create_money_to_all(self, amount=None):
        amount= amount or self.transactions_to_do * self.test_amount
        while len(self.my_clients) != len(self.already_sent):
            futures = []
            for client in self.my_clients:
                if client not in self.already_sent:
                    peer = self.get_peer_from_public_key(client)
                    # futures.append(self.await_and_time(self.send_creation, peer, amount))
                    await self.await_and_time(self.send_creation, peer, amount)
                    self.already_sent.append(client)
            # await wait(futures)

        # wait for clients to do their thing
        self.sync_next("await_money", "await", self.run_until_done)
        # await self.run_until_done()

    def get_random_peer(self):
        client = random.choice(self.valid_peers)
        return self.get_peer_from_public_key(client)

    async def run_until_done(self):
        # Global start time
        if self.is_gateway:
            self.start_time_p = time.process_time()
            self.start_time = time.time()

        # wait until everyone is done
        await self.sync_peers("shutdown", 1)
        self.stop()

    async def run_stress_test(self): # no delay
        while self.transactions_sent < self.transactions_to_do:
            await self.eval_attempt_send_money()
        await self.run_until_done()

    async def run_normal_test(self): # with delay
        self.register_task("send_random_money", self.send_random_money, interval=1, delay=1)

    async def send_random_money(self):
        await self.eval_attempt_send_money()
        if self.transactions_sent >= self.transactions_to_do:
            self.replace_task("send_random_money", self.run_until_done)

    async def eval_attempt_send_money(self, amount=5):
        peer = self.get_random_peer()
        if not peer:
            return

        with self.receive_block_lock:
            my_balance = self.get_my_balance()
            verified_balance = self.get_my_verified_balance() - amount
        if my_balance < amount:
            return
        if verified_balance < 0 or self.transactions_since_checkpoint >= self.min_checkpoint_freq:
            await self.await_and_time(self.request_checkpoint)
        resp, prop = await self.await_and_time(self.eval_send_money, peer, amount)
        self.transactions_sent += 1
        self.transactions_since_checkpoint += 1

    async def await_and_time(self, func, *args, **kwargs):
        t = time.process_time()
        future = func(*args, **kwargs)
        processing_time = time.process_time() - t
        resp, prop = await future
        wait_time = time.process_time() - t
        if not prop or not resp:
            return None, None
        self.pprint(prop, resp, processing_time, wait_time)#, total_time)
        return resp, prop

    def pprint(self, prop, resp, processing_time, wait_time):
        type_map = {
                BlockTypes.CHECKPOINT : "V",
                BlockTypes.TRANSFER : "T",
                BlockTypes.CREATION : "C"
                }
        balance = prop.transaction.get("balance", None)
        amount  = prop.transaction.get("amount", None)

        if type(balance) == int:
            balance = f"{balance: <4}"
        else:
            balance = "    "

        if type(amount) == int:
            amount = f"{amount: <4}"
        else:
            amount = "    "

        print (f"{pretty_block(prop)} {type_map[prop.type]} {balance} - {amount} -> {pretty_block(resp)} TD {self.transactions_sent} LC {self.transactions_since_checkpoint} T {processing_time}/{wait_time}")

    def next_block_id(self):
        key = pretty_peer(self.my_peer)
        block = self.persistence.get_latest(self.my_peer.public_key.key_to_bin())
        if block is not None:
            seq = block.sequence_number + 1
        else:
            seq = 1
        return f"{key}:{seq: <4}"
