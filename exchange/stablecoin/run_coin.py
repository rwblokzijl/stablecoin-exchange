#!/usr/bin/env pipenv-shebang

from stablecoin.stablecoin import StabecoinInteractor

from stablecoin.bank.ing              import ING
from stablecoin.blockchain.trustchain import TrustChain
from stablecoin.persistence.database  import Database
# from stablecoin.ui.rest               import REST

def main(*args):
    bank        = ING("")
    blockchain  = TrustChain()
    persistence = Database()
    # ui          = REST()

    s = StabecoinInteractor(
            bank        = bank,
            blockchain  = blockchain,
            persistence = persistence,
            # ui          = ui,
            )

    s.print_struct()

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
