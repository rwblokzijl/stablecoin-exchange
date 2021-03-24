from blockchain.trustchain import TrustChain

from unittest.mock import Mock

import unittest

class TestTrustChain(unittest.TestCase):

    def test__str__(self):
        instance = TrustChain("pubkey", Mock())
        self.assertEqual(str(instance), "trustchain")

    def test_init(self):
        instance = TrustChain("pubkey", Mock())
