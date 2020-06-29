from stablecoin.blockchain.trustchain import TrustChain

import unittest

class TestTrustChain(unittest.TestCase):

    def test__str__(self):
        instance = TrustChain("pubkey")
        self.assertEqual(str(instance), "trustchain")
