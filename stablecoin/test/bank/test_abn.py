from stablecoin.bank.abn import ABN

import unittest

class TestABN(unittest.TestCase):

    def test__str__(self):
        instance = ABN()
        self.assertEqual(str(instance), "abn")
