from stablecoin.ui.rest import REST

import unittest

class TestREST(unittest.TestCase):

    def test__str__(self):
        instance = REST()
        self.assertEqual(str(instance), "rest")
