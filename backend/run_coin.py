#!/usr/bin/env pipenv-shebang

from stablecoin.stablecoin import StablecoinInteractor

# from stablecoin.bank.ing              import ING
from stablecoin.blockchain.trustchain import TrustChain
# from stablecoin.persistence.database  import Database

from stablecoin.bank.bankstub                   import BankStub
from stablecoin.blockchain.chainstub            import ChainStub
from stablecoin.persistence.inmemorypersistence import InMemoryPersistence
from stablecoin.blockchain.ipv8                 import MyTrustChainCommunity

from stablecoin.ui.rest import MyRESTManager

from asyncio import ensure_future, get_event_loop

from ipv8.configuration import get_default_configuration
from ipv8_service import IPv8

from binascii import hexlify, unhexlify
from base64 import b64encode

async def start_communities():
    print("starting")
    port = 8000
    configuration = get_default_configuration()
    configuration['keys'] = [{
        'alias': "my peer",
        'generation': u"curve25519",
        'file': f".keys/ec.pem"
        }]
    configuration['logger'] = {
            'level': "WARNING",
            # 'level': "INFO",
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
            'working_directory':f'.local'
            },
        'on_start': [('started', )]
        }]

    ipv8 = IPv8(configuration, extra_communities={'MyTrustChainCommunity': MyTrustChainCommunity})
    await ipv8.start()
    interactor = buildSI(ipv8)
    rest_manager = MyRESTManager(interactor)
    await rest_manager.start(port)

def buildSI(ipv8):
    bank        = BankStub()
    blockchain  = TrustChain("pubkey0123456789abcdef", ipv8)
    persistence = InMemoryPersistence()

    s = StablecoinInteractor(
            bank        = bank,
            blockchain  = blockchain,
            persistence = persistence,
            # ui          = ui,
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

    ensure_future(start_communities())
    get_event_loop().run_forever()



