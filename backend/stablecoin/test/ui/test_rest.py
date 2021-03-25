from stablecoin  import StablecoinInteractor
from transaction import Transaction
from ui.rest     import RootEndpoint

import unittest
from unittest.mock import MagicMock

from test.util.TestPersistence import TestPersistence
from test.util.TestBank        import TestBank
from test.util.TestBlockchain  import TestBlockChain
from persistence.inmemorypersistence      import InMemoryPersistence

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

import time

class TestREST(AioHTTPTestCase):
    async def get_application(self):
        import warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        endpoint = RootEndpoint()
        endpoint.initialize(self.si)
        return endpoint.app

    def getInteractor(self,
            name        = "Test interactor",
            bank        = None,
            persistence = None,
            blockchain  = None,
            rateE2T     = 0.99,
            rateT2E     = 0.99
            ):
        if bank is None:
            bank = TestBank()
        if persistence is None:
            persistence = InMemoryPersistence()
        if blockchain is None:
            blockchain = TestBlockChain()
        return StablecoinInteractor( name, bank, persistence, blockchain, rateE2T, rateT2E)

    async def request_status(self, payment_id):
        resp = await self.client.get("/api/exchange/status", params={'payment_id':payment_id})
        return (await resp.json())

    def setUp(self):
        self.si = self.getInteractor()
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
        resp = await self.client.get("/api/exchange/e2t/rate", params={'base':100})
        data = await resp.json()
        self.assertDictEqual(data, expected)
        self.assertEqual(
                resp.status,
                200
                )

    @unittest_run_loop
    async def test_exchange_rate_missing_base(self):
        resp = await self.client.get("/api/exchange/e2t/rate", params={})
        self.assertEqual(
                resp.status,
                400
                )

    @unittest_run_loop
    async def test_exchange_rate_wrong_base(self):
        resp = await self.client.get("/api/exchange/e2t/rate", params={'base':"NOTINT"})
        self.assertEqual(
                resp.status,
                400
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
        resp1 = await self.client.get("/api/exchange/e2t/rate", params={'base':100} )
        data1 = await resp1.json()

        resp2 = await self.client.get("/api/exchange/e2t/rate", params={'base':200})
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
    async def test_exchange_euro_to_token(self):
        # STEP 1
        resp = await self.client.post("/api/exchange/e2t/initiate", json={
            "collatoral_cent": 100
            })
        # assert
        self.assertEqual(
                resp.status,
                200
                )

        data = await resp.json()
        self.assertIn("payment_id", data)

        payment_id = data["payment_id"]

        self.assertEqual((await self.request_status(payment_id))["status"], 0)

        # STEP 2
        self.si.CREATE_connect(data["payment_id"], "KEY", "IP", "PORT")
        self.assertEqual((await self.request_status(payment_id))["status"], 1)

        # STEP 3
        resp = await self.client.post("/api/exchange/e2t/start_payment", json={
            "payment_id": data["payment_id"]
            })
        # assert
        self.assertEqual(
                resp.status,
                200
                )
        data = await resp.json()

        self.assertIn("payment_id", data)
        self.assertEqual((await self.request_status(payment_id))["status"], 2)

        # STEP 4
        resp = await self.client.post("/api/exchange/e2t/finish_payment", json={
            "payment_id": data["payment_id"]
            })

        # assert
        self.assertEqual(
                resp.status,
                200
                )

        data = await resp.json()
        self.assertIn("payment_id", data)
        self.assertEqual((await self.request_status(payment_id))["status"], 4)

    @unittest_run_loop
    async def test_missing_payment_id(self):
        resp = await self.client.post("/api/exchange/e2t/start_payment", json={ })
        # assert
        self.assertEqual(
                resp.status,
                400
                )

    @unittest_run_loop
    async def test_wrong_payment_id(self):
        resp = await self.client.post("/api/exchange/e2t/start_payment", json={
            "payment_id": "NON EXISTANT"
            })
        # assert
        self.assertEqual(
                resp.status,
                404
                )

    @unittest_run_loop
    async def test_wrong_amount(self):
        # STEP 1
        resp = await self.client.post("/api/exchange/e2t/initiate", json={
            "collatoral_cent": "not and int"
            })
        # assert
        self.assertEqual(
                resp.status,
                400
                )

    @unittest_run_loop
    async def test_missing_amount(self):
        # STEP 1
        resp = await self.client.post("/api/exchange/e2t/initiate", json={ })
        # assert
        self.assertEqual(
                resp.status,
                400
                )

    @unittest_run_loop
    async def test_wrong_state_3(self):
        # STEP 1
        resp = await self.client.post("/api/exchange/e2t/initiate", json={
            "collatoral_cent": 100
            })
        # assert
        self.assertEqual(
                resp.status,
                200
                )

        data = await resp.json()
        self.assertIn("payment_id", data)

        payment_id = data["payment_id"]

        self.assertEqual((await self.request_status(payment_id))["status"], 0)

        # STEP 3
        resp = await self.client.post("/api/exchange/e2t/start_payment", json={
            "payment_id": data["payment_id"]
            })
        # assert
        self.assertEqual(
                resp.status,
                400
                )

        self.assertEqual((await self.request_status(payment_id))["status"], 0)

    @unittest_run_loop
    async def test_wrong_state_4(self):
        # STEP 1
        resp = await self.client.post("/api/exchange/e2t/initiate", json={
            "collatoral_cent": 100
            })
        # assert
        self.assertEqual(
                resp.status,
                200
                )

        data = await resp.json()
        self.assertIn("payment_id", data)

        payment_id = data["payment_id"]

        self.assertEqual((await self.request_status(payment_id))["status"], 0)

        # STEP 2
        self.si.CREATE_connect(data["payment_id"], "KEY", "IP", "PORT")
        self.assertEqual((await self.request_status(payment_id))["status"], 1)

        # STEP 4
        resp = await self.client.post("/api/exchange/e2t/finish_payment", json={
            "payment_id": data["payment_id"]
            })

        # assert
        self.assertEqual(
                resp.status,
                400
                )

        self.assertEqual((await self.request_status(payment_id))["status"], 1)

class TestRESTDestroyLoop(TestREST):

    @unittest_run_loop
    async def test_exchange_rate_token_to_euro(self):
        expected = {
                "token": 100,
                "eur": 99
                }
        resp = await self.client.get("/api/exchange/t2e/rate", params={'base':100})
        self.assertEqual(
                resp.status,
                200
                )
        data = await resp.json()
        self.assertDictEqual(data, expected)

    @unittest_run_loop
    async def test_exchange_rate_missing_base(self):
        resp = await self.client.get("/api/exchange/t2e/rate", params={})
        self.assertEqual(
                resp.status,
                400
                )

    @unittest_run_loop
    async def test_exchange_rate_wrong_base(self):
        resp = await self.client.get("/api/exchange/t2e/rate", params={'base':"NOTINT"})
        self.assertEqual(
                resp.status,
                400
                )


    @unittest_run_loop
    async def test_exchange_rate_different_values_token_to_euro(self):
        expected1 = {
                "token": 100,
                "eur": 99
                }
        expected2 = {
                "token": 200,
                "eur": 198
                }
        resp1 = await self.client.get("/api/exchange/t2e/rate", params={'base':100})
        data1 = await resp1.json()

        resp2 = await self.client.get("/api/exchange/t2e/rate", params={'base':200})
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
    async def test_exchange_token_to_euro(self):
        # STEP 1
        resp = await self.client.post("/api/exchange/t2e/initiate", json={
            "token_amount_cent": 100,
            'destination_iban': "DEST IBAN"
            })

        # assert
        self.assertEqual(
                resp.status,
                200
                )

        data = await resp.json()

        self.assertIn("payment_id", data)

        payment_id = data["payment_id"]

        self.assertEqual((await self.request_status(payment_id))["status"], 2)

        # STEP 2
        ans = self.si.DESTROY_pay(data["payment_id"], None, 100, "PUBKEY")
        self.assertEqual((await self.request_status(payment_id))["status"], 4)

    @unittest_run_loop
    async def test_exchange_token_to_euro_missing_amount(self):
        # STEP 1
        resp = await self.client.post("/api/exchange/t2e/initiate", json={
            'destination_iban': "DEST IBAN"
            })

        # assert
        self.assertEqual(
                resp.status,
                400
                )

    @unittest_run_loop
    async def test_exchange_token_to_euro_wrong_amount(self):
        # STEP 1
        resp = await self.client.post("/api/exchange/t2e/initiate", json={
            "token_amount_cent": "NOTINT",
            'destination_iban': "DEST IBAN"
            })

        # assert
        self.assertEqual(
                resp.status,
                400
                )

    @unittest_run_loop
    async def test_exchange_token_to_euro_missing_iban(self):
        # STEP 1
        resp = await self.client.post("/api/exchange/t2e/initiate", json={
            "token_amount_cent": 100,
            })

        # assert
        self.assertEqual(
                resp.status,
                400
                )
