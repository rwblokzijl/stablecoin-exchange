from stablecoin.bank.ing import ING

import unittest

class TestING(unittest.TestCase):

    def test__str__(self):
        instance = ING()
        self.assertEqual(str(instance), "ing")
