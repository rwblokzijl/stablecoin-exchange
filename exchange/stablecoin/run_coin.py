#!/usr/bin/env pipenv-shebang

from stablecoin.stablecoin import StabecoinInteractor

# from stablecoin.bank.ing              import ING
# from stablecoin.blockchain.trustchain import TrustChain
# from stablecoin.persistence.database  import Database

from stablecoin.bank.bankstub                   import BankStub
from stablecoin.blockchain.chainstub            import ChainStub
from stablecoin.persistence.inmemorypersistence import InMemoryPersistence

from stablecoin.ui.rest import REST

def main(*args):
    bank        = BankStub()
    blockchain  = ChainStub("pubkey0123456789abcdef")
    persistence = InMemoryPersistence()

    s = StabecoinInteractor(
            bank        = bank,
            blockchain  = blockchain,
            persistence = persistence,
            # ui          = ui,
            )

    ui          = REST(s)
    ui.start()

    # s.print_struct()

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
