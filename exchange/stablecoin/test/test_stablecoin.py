import unittest
from unittest import mock

from stablecoin.stablecoin import StabecoinInteractor

from stablecoin.bank.bank               import Bank
from stablecoin.persistence.persistence import Persistence
from stablecoin.blockchain.blockchain   import Blockchain
# from stablecoin.ui.ui                   import UI

class TestStablecoinBusinessLogic(unittest.TestCase):

    """Testing the business logic"""

    def setUp(self):
        bank        = mock.MagicMock(name="bank")
        # ui          = mock.MagicMock(name="ui")
        persistence = mock.MagicMock(name="persistence")
        blockchain  = mock.MagicMock(name="blockchain")
        si = StabecoinInteractor(
                bank=bank,
                # ui=ui,
                persistence=persistence,
                blockchain=blockchain)

