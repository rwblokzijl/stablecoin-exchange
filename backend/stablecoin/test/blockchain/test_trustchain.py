from blockchain.trustchain import TrustChain

from unittest.mock import Mock

import unittest

class TestTrustChain(unittest.TestCase):

    def setUp(self):
        self.trustchain = TrustChain(
                identity="PUBKEY",
                ipv8 = Mock()
                )

    def test__str__(self):
        instance = TrustChain("pubkey", Mock())
        self.assertEqual(str(instance), "trustchain")

    def test_init(self):
        instance = TrustChain("pubkey", Mock())

    def test_create_payment_request(self):
        ans = self.trustchain.create_payment_request(100)
        self.assertEqual(ans["ip"], "127.0.0.1")

    def test_on_payment(self):
        ans = self.trustchain.create_payment_request(100)

