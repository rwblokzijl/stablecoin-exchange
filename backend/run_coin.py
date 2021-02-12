#!/usr/bin/env python3

#### #!/usr/bin/env pipenv-shebang

from stablecoin.stablecoin import StablecoinInteractor

# from stablecoin.bank.ing              import ING
from stablecoin.blockchain.trustchain import TrustChain
# from stablecoin.persistence.database  import Database

from stablecoin.bank.tikkie                     import Tikkie
from stablecoin.blockchain.chainstub            import ChainStub
from stablecoin.persistence.inmemorypersistence import InMemoryPersistence
from stablecoin.blockchain.ipv8.eurotoken.community  import EuroTokenCommunity
from stablecoin.blockchain.ipv8.trustchain.community import MyTrustChainCommunity

from stablecoin.ui.rest import MyRESTManager

from asyncio import ensure_future, get_event_loop

from ipv8.configuration import get_default_configuration
from ipv8_service import IPv8

from binascii import hexlify, unhexlify
from base64 import b64encode

GATEWAY_NAME = "Demo Gateway"
GATEWAY_HOSTNAME = "gateway.euro-token.nl"
GATEWAY_IP = "10.0.0.27"
RATE_E2T = 1.00
RATE_T2E = 1.00

async def start_communities(args):
    print("starting")
    rest_port = 8000
    ipv8_port = 8090
    hostname = GATEWAY_HOSTNAME
    ip_address = GATEWAY_IP
    print(f"Address: {ip_address}")
    configuration = get_default_configuration()
    configuration['address'] = ip_address
    configuration['port'] = ipv8_port
    configuration['keys'] = [{
        'alias': "my peer",
        'generation': u"curve25519",
        'file': f".keys/ec.pem"
        }]
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
            'working_directory':f'/vol/database'
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
    await rest_manager.start(rest_port)

def buildSI(ipv8, address, ipv8_port):
    bank = Tikkie(
            production=False,
            abn_api_path='~/.ssh/abn_stablecoin_key',
            sandbox_key_path='~/.ssh/tikkie_key_sandbox',
            production_key_path='~/.ssh/tikkie_key_prod',
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

def main(*args):

    s = buildSI()

    ui          = REST(s)
    ui.start()

    # s.print_struct()

if __name__ == '__main__':
    import sys
    # main(sys.argv[1:])

    ensure_future(start_communities(sys.argv[1:]))
    get_event_loop().run_forever()



