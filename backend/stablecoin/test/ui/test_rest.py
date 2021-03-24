from stablecoin  import StablecoinInteractor
from transaction import Transaction
from ui.rest     import APIEndpoint

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

class TestRESTCreateLoop(TestREST):

    @unittest_run_loop
    async def test_exchange_rate_euro_to_token(self):
        expected = {
                "eur": 100,
                "token": 99
                }
        self.si.get_exchange_rate_col_to_tok.return_value = 99
        resp = await self.client.get("/exchange/e2t/rate", params={'base':100})
        data = await resp.json()
        self.assertDictEqual(data, expected)
        self.assertEqual(
                resp.status,
                200
                )

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
        self.si.get_exchange_rate_col_to_tok.return_value = 99
        resp1 = await self.client.get("/exchange/e2t/rate", params={'base':100} )
        data1 = await resp1.json()

        self.si.get_exchange_rate_col_to_tok.return_value = 198
        resp2 = await self.client.get("/exchange/e2t/rate", params={'base':200})
        data2 = await resp2.json()

        self.assertDictEqual(data1, expected1)
        self.assertEqual(
                resp1.status,
                200
                )
        self.assertDictEqual(data2, expected2)
        self.assertEqual(
                resp2.status,
                200
                )

    @unittest_run_loop
    async def test_exchange_euro_to_token_success(self):
        self.si.initiate_creation.return_value = {'status':'done'}
        resp = await self.client.post("/exchange/e2t", data={
            "collatoral_cent": 100,
            "dest_wallet": "ASDFASDF",
            })
        self.assertEqual(
                resp.status,
                200
                )

    @unittest_run_loop
    async def test_exchange_euro_to_token_missing_collatoral(self):
        self.si.initiate_creation.return_value = ""
        resp = await self.client.post("/exchange/e2t", data={
            "dest_wallet": "ASDFASDF",
            })
        self.assertEqual(
                resp.status,
                400
                )

    @unittest_run_loop
    async def test_exchange_euro_to_token_non_int_collatoral(self):
        self.si.initiate_creation.return_value = ""
        resp = await self.client.post("/exchange/e2t", data={
            "collatoral_cent": "a lot",
            "dest_wallet": "ASDFASDF",
            })
        self.assertEqual(
                resp.status,
                400
                )

    @unittest_run_loop
    async def test_exchange_euro_to_token_missing_wallet(self):
        self.si.initiate_creation.return_value = ""
        resp = await self.client.post("/exchange/e2t", data={
            "collatoral_cent": 100,
            })
        self.assertEqual(
                resp.status,
                400
                )

    @unittest_run_loop
    async def test_exchange_euro_to_token_internal_error(self):
        def error(collatoral_amount_cent, destination_wallet):
            raise StablecoinInteractor.CommunicationError
        self.si.initiate_creation.side_effect = error
        resp = await self.client.post("/exchange/e2t", data={
            "collatoral_cent": 100,
            "dest_wallet": "WALLETFORPAYMENT",
            })
        self.assertEqual(
                resp.status,
                500
                )

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
                "status"                 : "PAYMENT_PENDING",
                "created"                : 100000.12345,
                "destination_wallet"     : destination_wallet,
                "payment_id"             : "somehash",
                }

        self.si.initiate_creation.return_value = payment_data

        # excecute
        resp = await self.client.post("/exchange/e2t", data={
            "collatoral_cent": collatoral_amount_cent,
            "dest_wallet": destination_wallet,
            })
        data = await resp.json()

        # assert
        self.assertEqual(
                resp.status,
                200
                )
        self.assertIn("link", data)

class TestRESTDestroyLoop(TestREST):

    @unittest_run_loop
    async def test_exchange_rate_euro_to_token(self):
        expected = {
                "eur": 100,
                "token": 101
                }
        self.si.get_exchange_rate_col_to_tok.return_value = 101
        resp = await self.client.get("/exchange/e2t/rate", params={'base':100})
        data = await resp.json()
        self.assertDictEqual(data, expected)
        self.assertEqual(
                resp.status,
                200
                )

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
        self.si.get_exchange_rate_col_to_tok.return_value = 99
        resp1 = await self.client.get("/exchange/e2t/rate", params={'base':100})
        data1 = await resp1.json()

        self.si.get_exchange_rate_col_to_tok.return_value = 198
        resp2 = await self.client.get("/exchange/e2t/rate", params={'base':200})
        data2 = await resp2.json()

        self.assertDictEqual(data1, expected1)
        self.assertEqual(
                resp1.status,
                200
                )
        self.assertDictEqual(data2, expected2)
        self.assertEqual(
                resp2.status,
                200
                )


    @unittest_run_loop
    async def test_exchange_token_to_euro_success(self):
        resp = await self.client.post("/exchange/t2e", data={
            "token_amount_cent": 99,
            "destination_iban": "NL05 INGB 0XXX XXXX XX",
            })
        self.assertEqual(
                resp.status,
                200
                )

    @unittest_run_loop
    async def test_exchange_token_to_euro_status_confirmed(self):
        d_iban = "NL05 INGB 0XXX XXXX XX"
        payment_data = {
                "payment wallet"         : "WALLETFORPAYMENT",
                "token_amount_cent"      : 101,
                "collatoral_amount_cent" : 100,
                "provider"               : "bank",
                "timeout"                : 3000,
                "status"                 : Transaction.Status.PAYMENT_PENDING,
                "created"                : 100000.12345,
                "destination_iban  "     : d_iban,
                "payment_id"             : "somehash",
                }


        self.si.initiate_destruction.return_value = payment_data
        self.si.transaction_status.return_value = Transaction.Status.PAYMENT_PENDING

        # setup transaction
        resp = await self.client.post("/exchange/t2e", data={
            "token_amount_cent": 101,
            "destination_iban": d_iban
            })
        data = await resp.json()

        # assert
        self.assertEqual(
                resp.status,
                200
                )
        self.assertDictEqual(
                data,
                payment_data
                )

        self.si.Transaction.Status.PAYMENT_DONE

        # excecute get status
        resp = await self.client.get("/exchange/payment", params={
            "payment_id" : data["payment_id"]
            })
        data = await resp.json()

        # assert
        self.assertEqual(
                resp.status,
                200
                )

        self.assertEqual(
                data,
                "Waiting for payment"
                )

    @unittest_run_loop
    async def test_exchange_token_to_euro_status_pending(self):
        d_iban = "NL05 INGB 0XXX XXXX XX"
        payment_data = {
                "payment wallet"         : "WALLETFORPAYMENT",
                "token_amount_cent"      : 101,
                "collatoral_amount_cent" : 100,
                "provider"               : "bank",
                "timeout"                : 3000,
                "status"                 : "PAYMENT_PENDING",
                "created"                : 100000.12345,
                "destination_iban  "     : d_iban,
                "payment_id"             : "somehash",
                }


        self.si.initiate_destruction.return_value = payment_data
        self.si.transaction_status.return_value = Transaction.Status.PAYMENT_PENDING

        # setup transaction
        resp = await self.client.post("/exchange/t2e", data={
            "token_amount_cent": 101,
            "destination_iban": d_iban
            })
        data = await resp.json()

        # assert
        self.assertEqual(
                resp.status,
                200
                )
        self.assertDictEqual(
                data,
                payment_data
                )

        payment_data["status"] = "pending"

        # excecute get status
        # setup transaction
        resp = await self.client.get("/exchange/payment", params={
            "payment_id" : "somehash"
            })
        data = await resp.json()

        # assert
        self.assertEqual(
                resp.status,
                200
                )
        self.assertEqual(
                data,
                "Waiting for payment"
                )

    @unittest_run_loop
    async def test_exchange_token_to_euro_success(self):
        d_iban = "NL05 INGB 0XXX XXXX XX"
        payment_data = {
                "payment wallet"         : "WALLETFORPAYMENT",
                "token_amount_cent"      : 101,
                "collatoral_amount_cent" : 100,
                "provider"               : "bank",
                "timeout"                : 3000,
                "status"                 : "PAYMENT_PENDING",
                "created"                : 100000.12345,
                "destination_iban  "     : d_iban,
                "payment_id"             : "somehash",
                }

        self.si.initiate_destruction.return_value = payment_data

        resp = await self.client.post("/exchange/t2e", data={
            "token_amount_cent": 101,
            "destination_iban": d_iban
            })
        self.assertEqual(
                resp.status,
                200
                )
        data = await resp.json()

        self.assertDictEqual(
                data,
                payment_data
                )

    @unittest_run_loop
    async def test_exchange_token_to_euro_missing_token_amount(self):
        d_iban = "NL05 INGB 0XXX XXXX XX"
        self.si.initiate_destruction.return_value = ""
        resp = await self.client.post("/exchange/t2e", data={
            "destination_iban": d_iban
            })
        self.assertEqual(
                resp.status,
                400
                )

    @unittest_run_loop
    async def test_exchange_token_to_euro_missing_iban(self):
        self.si.initiate_destruction.return_value = ""
        resp = await self.client.post("/exchange/t2e", data={
            "token_amount_cent": 100,
            })
        self.assertEqual(
                resp.status,
                400
                )

