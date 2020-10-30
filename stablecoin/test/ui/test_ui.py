from stablecoin.ui.ui import UI

import unittest

class TestUI(unittest.TestCase):

    def test_init(self):
        with self.assertRaises(TypeError):
            UI()
