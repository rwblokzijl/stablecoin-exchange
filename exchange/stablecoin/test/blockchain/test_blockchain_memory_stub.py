# from stablecoin.blockchain.blockchain_memory_stub import BlockchainStub

import unittest

@unittest.skip
class TestBlockchainStub(unittest.TestCase):

    def test__str__(self):
        instance = BlockchainStub("pubkey")
        self.assertEqual(str(instance), "stub")

    def test_pubkey(self):
        instance = BlockchainStub("pubkeyy")
        self.assertEqual(
                str(instance.get_identity()),
                "pubkeyy"
                )

    # def test_balance(self):
    #     instance = BlockchainStub("pubkeyy")
    #     instance.set_balance(100)
    #     self.assertEqual(
    #             instance.get_balance(),
    #             100
    #             )

    def test_transfer_funds(self):
        instance = BlockchainStub("pubkeyy")
        instance.set_balance(100)
        instance.transfer_funds(50,"someone else")
        self.assertEqual(
                instance.get_balance(),
                50
                )

    # def test_get_transactions(self):
    #     instance = BlockchainStub("pubkey")
    #     instance.set_balance(100)
    #     instance.transfer_funds(50,"someone else")
    #     instance.transfer_funds(20,"someone else again")
    #     instance.transfer_funds(30,"someone else")

    #     expected = [
    #                 {
    #                     "sender": "pubkey",
    #                     "receiver": "someone else",
    #                     "amount" : 50
    #                 }, {
    #                     "sender": "pubkey",
    #                     "receiver": "someone else again",
    #                     "amount" : 20
    #                 }, {
    #                     "sender": "pubkey",
    #                     "receiver": "someone else",
    #                     "amount" : 30
    #                 }
    #             ]
    #     actual = instance.get_transactions()

    #     # same amount of items
    #     self.assertEqual(
    #             len(expected),
    #             len(actual)
    #             )
    #     # same contents
    #     for e, a in zip(expected, actual):
    #         self.assertDictEqual(
    #                 e, a
    #                 )

