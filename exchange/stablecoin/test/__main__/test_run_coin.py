from stablecoin.stablecoin import StablecoinInteractor
from stablecoin.ui.rest               import REST
from run_coin import buildSI

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
        self.si = StablecoinInteractor(
                bank        = self.bank,
                blockchain  = self.blockchain,
                persistence = self.persistence,
                )
        super().setUp()

    @unittest.skip("idk")
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

    @unittest.skip("idk")
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

class V1AcceptanceTests(AioHTTPTestCase):

    async def get_application(self):
        import warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        return REST(self.si).app

    def setUp(self):
        self.si = buildSI()
        super().setUp()

    @unittest_run_loop
    async def test_get_exchange_rate_e2t(self):
        resp = await self.client.get("/exchange/e2t/rate", params={'base':200})
        data = await resp.json()
        self.assertDictEqual(
                {'eur': 200, 'token': 198},
                data
                )

    @unittest_run_loop
    async def test_get_exchange_rate_t2e(self):
        resp = await self.client.get("/exchange/t2e/rate", params={'base':200})
        data = await resp.json()
        self.assertDictEqual(
                {'token': 200, 'eur': 198},
                data
                )

    async def complete_payment(self, payment_id, counterparty):
        resp3 = await self.client.post("/exchange/complete", data={'payment_id':payment_id, 'counterparty':counterparty})

        self.assertEqual(
                resp3.status,
                200)

    async def create_transaction(self, amount, wallet):
        resp1 = await self.client.post("/exchange/e2t", data={'collatoral_cent':amount, 'dest_wallet':wallet})
        data1 = await resp1.json()
        return data1

    async def destroy_transaction(self, amount, iban):
        resp1 = await self.client.post("/exchange/t2e", data={'token_amount_cent':amount, 'destination_iban':iban})
        data1 = await resp1.json()
        return data1

    async def get_status(self, payment_id):
        resp2 = await self.client.get("/exchange/payment", params={'payment_id':payment_id})
        data2 = await resp2.json()
        return data2

    async def get_balance(self, wallet):
        respb1 = await self.client.get("/transactions/balance", params={'wallet':wallet})
        datab1 = await respb1.json()
        return datab1

    async def create_money(self, amount, wallet, iban):
        data1 = await self.create_transaction(100, wallet)
        await self.complete_payment(data1["payment_id"], iban)
        await self.get_status(data1["payment_id"])

    async def destroy_money(self, amount, wallet, iban):
        data1 = await self.destroy_transaction(99, iban)
        await self.complete_payment(data1["payment_id"], wallet)
        await self.get_status(data1["payment_id"])

    async def get_wallet_transactions(self, wallet):
        resp = await self.client.get("/transactions/wallet", params={'wallet':wallet})
        data = await resp.json()
        return data

    async def get_iban_transactions(self, iban):
        resp = await self.client.get("/transactions/iban", params={'iban':iban})
        data = await resp.json()
        return data

    @unittest_run_loop
    async def test_creation_loop(self):
        wallet="ABC123"
        iban="COUTERP1"

        #create
        data1 = await self.create_transaction(100, wallet)
        self.assertIn(
                "payment_id",
                data1
                )

        #status
        data2 = await self.get_status(data1["payment_id"])
        self.assertEqual(
                data2["status"],
                "Waiting for payment"
                )

        #balance
        data3 = await self.get_balance(wallet)
        self.assertEqual(
                data3["balance"],
                0
                )

        # finish assert
        await self.complete_payment(data1["payment_id"], iban)

        #status
        data4 = await self.get_status(data1["payment_id"])
        self.assertEqual(
                data4["status"],
                "Payout Done")

        #balance
        data3 = await self.get_balance(wallet)
        self.assertEqual(
                data3["balance"],
                99
                )

    @unittest_run_loop
    async def test_destruction_loop(self):
        wallet="ABC123"
        iban="COUTERP1"

        #create
        data1 = await self.destroy_transaction(99, wallet)
        self.assertIn(
                "payment_id",
                data1
                )

        #status
        data2 = await self.get_status(data1["payment_id"])
        self.assertEqual(
                data2["status"],
                "Waiting for payment"
                )

        #balance
        data3 = await self.get_balance(wallet)
        self.assertEqual(
                data3["balance"],
                0
                )

        # finish assert
        await self.complete_payment(data1["payment_id"], wallet)

        #status
        data4 = await self.get_status(data1["payment_id"])
        self.assertEqual(
                data4["status"],
                "Payout Done")

        #balance
        data5 = await self.get_balance(wallet)
        self.assertEqual(
                data5["balance"],
                -99
                )

    @unittest_run_loop
    async def test_create_thrice_destroy_twice(self):
        wallet="ABC123"
        iban="COUTERP1"

        await self.create_money(100, wallet, iban)
        balance = await self.get_balance(wallet)
        self.assertEqual(
                balance["balance"],
                99
                )

        import time
        await self.create_money(100, wallet, iban)
        await self.create_money(100, wallet, iban)
        balance = await self.get_balance(wallet)
        self.assertEqual(
                balance["balance"],
                297
                )

        await self.destroy_money(99, wallet, iban)
        await self.destroy_money(99, wallet, iban)
        balance = await self.get_balance(wallet)
        self.assertEqual(
                balance["balance"],
                99
                )

    @unittest_run_loop
    async def test_create_loop_with_multiple_complete_and_status(self):
        wallet="ABC123"
        iban="COUTERP1"

        #create
        data1 = await self.create_transaction(100, wallet)
        self.assertIn(
                "payment_id",
                data1
                )

        #status
        await self.get_status(data1["payment_id"])
        await self.get_status(data1["payment_id"])
        data2 = await self.get_status(data1["payment_id"])
        self.assertEqual(
                data2["status"],
                "Waiting for payment"
                )

        #balance
        data3 = await self.get_balance(wallet)
        self.assertEqual(
                data3["balance"],
                0
                )

        # finish assert
        await self.complete_payment(data1["payment_id"], iban)
        await self.get_status(data1["payment_id"])
        await self.complete_payment(data1["payment_id"], iban)
        await self.get_status(data1["payment_id"])
        await self.complete_payment(data1["payment_id"], iban)
        await self.get_status(data1["payment_id"])
        await self.complete_payment(data1["payment_id"], iban)

        #status
        await self.get_status(data1["payment_id"])
        await self.get_status(data1["payment_id"])
        data4 = await self.get_status(data1["payment_id"])
        self.assertEqual(
                data4["status"],
                "Payout Done")

        #balance
        data5 = await self.get_balance(wallet)
        self.assertEqual(
                data5["balance"],
                99
                )

    @unittest_run_loop
    async def test_get_transactions(self):
        wallet="ABC123"
        iban="COUTERP1"

        await self.create_money(100, wallet, iban)
        await self.create_money(100, wallet, iban)
        await self.create_money(100, wallet, iban)
        await self.create_money(100, wallet, iban)
        await self.destroy_money(99, wallet, iban)
        await self.destroy_money(99, wallet, iban)
        await self.destroy_money(99, wallet, iban)

        transactions = await self.get_wallet_transactions(wallet)
        self.assertEqual(
                len(transactions),
                7
                )

        transactions = await self.get_iban_transactions(iban)
        self.assertEqual(
                len(transactions),
                7
                )

