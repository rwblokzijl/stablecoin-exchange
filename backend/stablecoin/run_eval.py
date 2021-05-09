#!/usr/bin/env python3

from asyncio import ensure_future, get_event_loop, sleep

from blockchain.ipv8.trustchain.eval_community import EvalTrustChainCommunity

from pyipv8.ipv8.attestation.trustchain.settings import TrustChainSettings
from pyipv8.ipv8.configuration import get_default_configuration
from pyipv8.ipv8_service import IPv8

import socket, os, time

from binascii import hexlify

PORT               = int(os.environ.get('PORT', 8090))
KEY                = os.environ.get('KEY', f"{socket.gethostname()}:{PORT}" ).strip()
BASE_DIR           = os.environ.get('BASE_DIR', '/vol/').strip()

# print()
# print(KEY)
# print(PORT)
# print(BASE_DIR)

GATEWAYS           = int(os.environ.get('GATEWAYS', None))
CLIENTS            = int(os.environ.get('CLIENTS',  None))
TRANSACTIONS_TO_DO = int(os.environ.get('TRANSACTIONS_TO_DO',  None))
CHECKPOINT_EVERY   = int(os.environ.get('CHECKPOINT_EVERY',  None))

# print(GATEWAYS)
# print(CLIENTS)
# print(TRANSACTIONS_TO_DO)
# print(CHECKPOINT_EVERY)

IS_GATEWAY       = bool(int(os.environ.get('IS_GATEWAY', 0)))
if IS_GATEWAY:
    KEY_FILE         = f"ec-g-{KEY}.pem"
else:
    KEY_FILE         = f"ec-c-{KEY}.pem"
KEY_PATH         = os.path.join(BASE_DIR, "keys", KEY_FILE)

print(IS_GATEWAY)
print(KEY_FILE)
# print(KEY_PATH)


STOP=False
ipv8=None

# exit()

async def start_communities():
    ipv8_port = PORT
    settings = TrustChainSettings()
    settings.broadcast_fanout = 0
    configuration = get_default_configuration()
    configuration['port'] = ipv8_port
    configuration['keys'] = [{
        'alias': "my peer",
        'generation': u"curve25519",
        'file': KEY_PATH
        }]
    configuration['address'] = "0.0.0.0"
    configuration['logger'] = {
            'level': "WARNING",
            }
    configuration['overlays'] = [{
        'class': 'EvalTrustChainCommunity',
        'key': "my peer",
        'walkers': [{
            'strategy': "RandomWalk",
            'peers': 10,
            'init': {
                'timeout': 3.0
                }
            }],
        'initialize': {
            'base_dir': BASE_DIR,
            'working_directory': os.path.join(BASE_DIR, 'database', KEY),
            'is_gateway': IS_GATEWAY,
            'n_gateways': GATEWAYS,
            'n_clients': CLIENTS,
            'key_file': KEY_FILE,
            'settings': settings,
            'transactions_to_do': TRANSACTIONS_TO_DO,
            'min_checkpoint_freq': CHECKPOINT_EVERY,
            },
        'on_start': [('started', )]
        }]
    global ipv8
    ipv8 = IPv8(configuration, extra_communities={'EvalTrustChainCommunity': EvalTrustChainCommunity})
    def stop():
        global STOP
        STOP=True
    ipv8.get_overlay(EvalTrustChainCommunity).set_stop(stop)
    await ipv8.start()

async def stopper():
    while True:
        global STOP
        global ipv8
        if STOP:
            await ipv8.stop()
            STOP=False
        await sleep(0.5)

def main():
    ensure_future(start_communities())
    ensure_future(stopper())
    get_event_loop().run_forever()

if __name__ == '__main__':
    main()
    time.sleep(1)

