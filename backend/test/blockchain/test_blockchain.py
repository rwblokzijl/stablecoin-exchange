from stablecoin.blockchain.blockchain import Blockchain

import unittest

class TestBlockchain(unittest.TestCase):

    def test_init(self):
        with self.assertRaises(TypeError):
            Blockchain()
