#!/usr/bin/env python3

from asyncio import ensure_future, get_event_loop

from stablecoin import StablecoinInteractor

from blockchain.trustchain import TrustChain
# from persistence.database  import Database

from bank.tikkie                          import Tikkie
from persistence.inmemorypersistence      import InMemoryPersistence
from blockchain.ipv8.eurotoken.community  import EuroTokenCommunity
from blockchain.ipv8.trustchain.community import MyTrustChainCommunity

from ui.rest import MyRESTManager

from pyipv8.ipv8.configuration import get_default_configuration
from pyipv8.ipv8_service import IPv8

from binascii import hexlify, unhexlify
from base64 import b64encode

import os

GATEWAY_NAME     =       os.environ.get('GATEWAY_NAME',     "Demo Gateway")
GATEWAY_HOSTNAME =       os.environ.get('GATEWAY_HOSTNAME', "gateway.euro-token.nl")
GATEWAY_IP       =       os.environ.get('GATEWAY_IP',       "0.0.0.0")
RATE_E2T         = float(os.environ.get('RATE_E2T',         1.00))
RATE_T2E         = float(os.environ.get('RATE_T2E',         1.00))

DOCKER = bool(int(os.environ.get('DOCKER', 0)))

def resolve_user(path):
    return os.path.expanduser(path)

async def start_communities():
    rest_port = 8000
    ipv8_port = 8090
    hostname = GATEWAY_HOSTNAME
    ip_address = GATEWAY_IP
    configuration = get_default_configuration()
    configuration['port'] = ipv8_port
    configuration['keys'] = [{
        'alias': "my peer",
        'generation': u"curve25519",
        'file': f"/vol/keys/trustchain/ec.pem" if DOCKER else resolve_user("~/.ssh/eurotoken/trustchain/ec.pem")
        }]
    configuration['address'] = ip_address
    configuration['logger'] = {
            'level': "INFO",
            }
    configuration['overlays'] = [{
        'class': 'MyTrustChainCommunity',
        'key': "my peer",
        'walkers': [{
            'strategy': "RandomWalk",
            'peers': 10,
            'init': {
                'timeout': 3.0
                }
            }],
        'initialize': {
            'working_directory': f'/vol/database'if DOCKER else f'.local'
            },
        'on_start': [('started', )]
        }, {
        'class': 'EuroTokenCommunity',
        'key': "my peer",
        'walkers': [{
            'strategy': "RandomWalk",
            'peers': 10,
            'init': {
                'timeout': 3.0
                }
            }],
        'initialize': {},
        'on_start': [('started', )]
        }
        ]

    ipv8 = IPv8(configuration, extra_communities={'MyTrustChainCommunity': MyTrustChainCommunity, 'EuroTokenCommunity': EuroTokenCommunity})
    await ipv8.start()
    interactor = buildSI(ipv8, hostname, ipv8_port)
    rest_manager = MyRESTManager(interactor)
    await rest_manager.start(ip_address, rest_port)

def buildSI(ipv8, address, ipv8_port):
    prefix = '/vol/keys/' if DOCKER else resolve_user('~/.ssh/eurotoken/')
    bank = Tikkie(
            production=False,

            # abn_api_path='/vol/keys/tikkie/abn_stablecoin_key',
            # sandbox_key_path='/vol/keys/tikkie/tikkie_key_sandbox',
            # production_key_path='/vol/keys/tikkie/tikkie_key_prod',

            abn_api_path=f'{prefix}/tikkie/abn_stablecoin_key',
            sandbox_key_path=f'{prefix}/tikkie/tikkie_key_sandbox',
            production_key_path=f'{prefix}/tikkie/tikkie_key_prod',

            global_url="http://bagn.blokzijl.family",
            url="/api/exchange/e2t/tikkie_callback")

    blockchain  = TrustChain(identity="pubkey0123456789abcdef", ipv8=ipv8, address=(address, ipv8_port) )
    persistence = InMemoryPersistence()

    s = StablecoinInteractor(
            name        = GATEWAY_NAME,
            bank        = bank,
            blockchain  = blockchain,
            persistence = persistence,
            rateE2T     = RATE_E2T,
            rateT2E     = RATE_T2E,
            )

    return s

def main():

    s = buildSI()

    ui          = REST(s)
    ui.start()

if __name__ == '__main__':
    ensure_future(start_communities())
    get_event_loop().run_forever()



