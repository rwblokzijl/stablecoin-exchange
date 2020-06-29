from stablecoin.stablecoin import StabecoinInteractor
from stablecoin.ui.rest               import REST

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

import unittest
from unittest.mock import Mock
from test.util.TestBank import TestBank

class TestMain(AioHTTPTestCase):

    """Test the main funcion"""

    async def get_application(self):
        import warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        return REST(self.si).app

    def setUp(self):
        self.bank        = TestBank()
        self.blockchain  = Mock()
        self.persistence = Mock()
        self.si = StabecoinInteractor(
                bank        = self.bank,
                blockchain  = self.blockchain,
                persistence = self.persistence,
                )
        super().setUp()

    @unittest_run_loop
    async def test_ui_to_stablecoin(self):
        expected = {
                "eur": 100,
                "token": 99
                }
        resp = await self.client.get("/exchange/e2t/rate/100")
        data = await resp.json()
        self.assertDictEqual(data, expected)
        assert resp.status == 200

    @unittest_run_loop
    async def test_ui_to_bank(self):
        collatoral_amount_cent = 100
        dest_wallet = "ASDFASDF"

        # excecute
        resp = await self.client.post("/exchange/e2t", data={
            "collatoral_cent": collatoral_amount_cent,
            "dest_wallet": dest_wallet,
            })
        self.assertEqual(resp.status, 200)

        data = await resp.json()


        self.assertIn("link", data)
