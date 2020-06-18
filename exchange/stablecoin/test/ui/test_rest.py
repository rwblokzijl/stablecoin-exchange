from stablecoin.ui.rest import REST
from stablecoin.stablecoin import StabecoinInteractor

import unittest
from unittest.mock import Mock

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

import time

class TestREST(AioHTTPTestCase):

    async def get_application(self):
        import warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        return REST(self.si).app

    def test__str__(self):
        instance = REST(0)
        self.assertEqual(str(instance), "rest")

    def setUp(self):
        self.si = Mock()
        super().setUp()

    @unittest_run_loop
    async def test_init(self):
        pass

    @unittest_run_loop
    async def test_exchange_rate_euro_to_token(self):
        expected = {
                "eur": 100,
                "token": 99
                }
        self.si.get_exchange_rate.return_value = 99
        resp = await self.client.get("/exchange/e2t/100")
        data = await resp.json()
        self.assertDictEqual(data, expected)
        assert resp.status == 200

    @unittest_run_loop
    async def test_exchange_rate_different_values_euro_to_token(self):
        expected1 = {
                "eur": 100,
                "token": 99
                }
        expected2 = {
                "eur": 200,
                "token": 198
                }
        self.si.get_exchange_rate.return_value = 99
        resp1 = await self.client.get("/exchange/e2t/100")
        data1 = await resp1.json()

        self.si.get_exchange_rate.return_value = 198
        resp2 = await self.client.get("/exchange/e2t/200")
        data2 = await resp2.json()

        self.assertDictEqual(data1, expected1)
        assert resp1.status == 200
        self.assertDictEqual(data2, expected2)
        assert resp2.status == 200

    @unittest_run_loop
    async def test_exchange_euro_to_token_success(self):
        self.si.start_transaction.return_value = ""
        resp = await self.client.post("/exchange/e2t", data={
            "collatoral_cent": 100,
            "dest_wallet": "ASDFASDF",
            })
        assert resp.status == 200

    @unittest_run_loop
    async def test_exchange_euro_to_token_missing_collatoral(self):
        self.si.start_transaction.return_value = ""
        resp = await self.client.post("/exchange/e2t", data={
            "dest_wallet": "ASDFASDF",
            })
        assert resp.status == 400

    @unittest_run_loop
    async def test_exchange_euro_to_token_non_int_collatoral(self):
        self.si.start_transaction.return_value = ""
        resp = await self.client.post("/exchange/e2t", data={
            "collatoral_cent": "a lot",
            "dest_wallet": "ASDFASDF",
            })
        assert resp.status == 400

    @unittest_run_loop
    async def test_exchange_euro_to_token_missing_wallet(self):
        self.si.start_transaction.return_value = ""
        resp = await self.client.post("/exchange/e2t", data={
            "collatoral_cent": 100,
            })
        assert resp.status == 400

    @unittest_run_loop
    async def test_exchange_euro_to_token_internal_error(self):
        def error(collatoral_amount_cent, destination_wallet):
            raise StabecoinInteractor.CommunicationError
        self.si.start_transaction.side_effect = error
        resp = await self.client.post("/exchange/e2t", data={
            "collatoral_cent": 100,
            "dest_wallet": "NL05 INGB",
            })
        assert resp.status == 500

    @unittest_run_loop
    async def test_exchange_euro_to_token(self):
        collatoral_amount_cent = 100
        destination_wallet = "ASDFASDF"
        payment_data = {
                "link"                   : "https://pay.moeneyyys.shrnarf/payment/<id>",
                "collatoral_amount_cent" : collatoral_amount_cent,
                "token_amount_cent"      : 99,
                "provider"               : "bank",
                "timeout"                : 3000,
                "status"                 : "open",
                "created"                : 100000.12345,
                "destination_wallet"     : destination_wallet,
                "payment_id"             : "somehash",
                }

        self.si.start_transaction.return_value = payment_data

        # excecute
        resp = await self.client.post("/exchange/e2t", data={
            "collatoral_cent": collatoral_amount_cent,
            "dest_wallet": destination_wallet,
            })
        data = await resp.json()

        # assert
        assert resp.status == 200
        self.assertIn("link", data)

    @unittest_run_loop
    async def test_exchange_token_to_euro_success(self):
        resp = await self.client.post("/exchange/t2e", data={
            "token_amount_cent": 99,
            "dest_iban": "NL05 INGB",
            })
        assert resp.status == 200

    @unittest_run_loop
    async def test_exchange_token_to_euro_success(self):
        resp = await self.client.post("/exchange/t2e", data={
            "token_amount_cent": 99,
            "dest_iban": "NL05 INGB",
            })
        assert resp.status == 200
