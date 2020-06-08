from stablecoin.bank.bank import Bank

import unittest

class TestBank(unittest.TestCase):

    def test_init(self):
        with self.assertRaises(TypeError):
            Bank()
