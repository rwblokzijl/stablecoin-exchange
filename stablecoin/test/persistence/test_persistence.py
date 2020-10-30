from stablecoin.persistence.persistence import Persistence

import unittest

class TestPersistence(unittest.TestCase):

    def test_init(self):
        with self.assertRaises(TypeError):
            Persistence()
