from stablecoin.bank.bank               import Bank
from stablecoin.blockchain.blockchain   import Blockchain
from stablecoin.persistence.persistence import Persistence
from stablecoin.ui.ui                   import UI

# from abc import ABC

class StabecoinInteractor:#(ABC):

    def __init__(self, bank, persistence, blockchain, ui):
        self.bank        = bank
        self.persistence = persistence
        self.blockchain  = blockchain
        self.ui          = ui

    def print_struct(self):
        print(self.bank)
        print(self.persistence)
        print(self.blockchain)
        print(self.ui)

