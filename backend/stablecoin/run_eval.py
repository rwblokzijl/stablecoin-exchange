#!/usr/bin/env python3

from asyncio import ensure_future, get_event_loop

from blockchain.ipv8.trustchain.eval_community import EvalTrustChainCommunity

from pyipv8.ipv8.attestation.trustchain.settings import TrustChainSettings
from pyipv8.ipv8.configuration import get_default_configuration
from pyipv8.ipv8_service import IPv8

import socket, os

from binascii import hexlify

KEY              = os.environ.get('KEY', socket.gethostname()).strip()
KEY_FILE         = f"/vol/keys/ec-{KEY}.pem"
GATEWAY_KEY_FILE = "/vol/keys/ec-GATEWAY.pem"
IS_GATEWAY       = (KEY == "GATEWAY")

async def start_communities():
    ipv8_port = 8090
    settings = TrustChainSettings()
    settings.broadcast_fanout = 0
    configuration = get_default_configuration()
    configuration['port'] = ipv8_port
    configuration['keys'] = [{
        'alias': "my peer",
        'generation': u"curve25519",
        'file': KEY_FILE
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
            'working_directory': f'/vol/database',
            'is_gateway': IS_GATEWAY,
            'key': KEY,
            'gateway_key': GATEWAY_KEY_FILE,
            'settings': settings
            },
        'on_start': [('started', )]
        }]

    ipv8 = IPv8(configuration, extra_communities={'EvalTrustChainCommunity': EvalTrustChainCommunity})
    await ipv8.start()

def main():
    ensure_future(start_communities())
    get_event_loop().run_forever()

if __name__ == '__main__':
    main()



