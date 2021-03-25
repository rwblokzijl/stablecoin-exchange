from bank.tikkie import Tikkie

from pathlib import Path

import unittest
from unittest.mock import Mock
import os

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from aiohttp import web

doAllTests = False

class TestTikkie(unittest.TestCase):

    """Test case docstring."""

    SLOW = bool(int(os.environ.get('SLOW', 0))) or doAllTests

    def __init__(self, *args, **kwargs):
        self.abn_api_path = '~/.ssh/eurotoken/tikkie/abn_stablecoin_key'
        self.sandbox_key_path = '~/.ssh/eurotoken/tikkie/tikkie_key_sandbox'

        self.skipclass = not Path(self.abn_api_path).expanduser().is_file()
        return super(TestTikkie, self).__init__(*args, **kwargs)

    def get_tikkie(self, testing):
        return Tikkie(
                production=False, url="/", global_url="",
                abn_api_path=self.abn_api_path,
                sandbox_key_path=self.sandbox_key_path, testing=testing)

    def set_registered_tikkie(self):
        self.tikkie = self.get_tikkie(testing=False)

    def setUp(self):
        if self.skipclass:
            raise unittest.SkipTest("No api key found at " + self.abn_api_path)
        self.tikkie = self.get_tikkie(testing=True)

    def tearDown(self):
        pass

    def new_env(self):
        self.tikkie.sandbox_key = self.tikkie.generate_new_sandbox_key()

    def test_str(self):
        str(self.tikkie)

    def test_initiate_payment(self):
        self.tikkie.initiate_payment("account", "amount", "payment_id")

    def test_missing_prod_key(self):
        with self.assertRaises(Tikkie.MissingKeyError):
            Tikkie(
                    production=True, url="/", global_url="",
                    abn_api_path=self.abn_api_path,
                    sandbox_key_path=self.sandbox_key_path, testing=True)

    def test_invalid_prod_key(self):
        with self.assertRaises(Tikkie.InvalidKeyError):
            Tikkie( production=True, url="/", global_url="",
                    abn_api_path=self.abn_api_path,
                    sandbox_key_path=self.sandbox_key_path,
                    production_key_path="NON EXISTANT PATH", testing=True)

    def test_instantiate_prod(self):
        tikkie = Tikkie( production=True, url="/", global_url="",
                abn_api_path=self.abn_api_path,
                sandbox_key_path=self.sandbox_key_path,
                production_key_path=self.sandbox_key_path, testing=True)
        tikkie.get_url("")
        tikkie.get_headers()

    @unittest.skipUnless(SLOW, "Slow test")
    def test_invalid_api_key(self):
        with self.assertRaises(Tikkie.InvalidKeyError):
            Tikkie( production=False, url="/", global_url="",
                    abn_api_path=self.sandbox_key_path,
                    sandbox_key_path=self.sandbox_key_path,
                    testing=False).generate_new_sandbox_key()

    @unittest.skipUnless(SLOW, "Slow test")
    def test_register_listener(self):
        self.set_registered_tikkie()

    @unittest.skipUnless(SLOW, "Slow test")
    def test_sandbox_apps(self):
        self.assertEqual(
                self.tikkie.generate_new_sandbox_key(),
                self.tikkie.get_key(self.tikkie.sandbox_key_path)
                )

    def test_header(self):
        headers = self.tikkie.get_headers()
        self.assertIn("API-Key", headers)
        self.assertIn("X-App-Token", headers)

    @unittest.skipUnless(SLOW, "Slow test")
    def test_create(self):
        # Create new env
        self.new_env()

        #amount of open tikkies should be 0
        trans = self.tikkie.get_transactions()
        self.assertEqual(
                len(trans['paymentRequests']),
                0
                )

        #create new tikkie
        ans = self.tikkie.create_request(10, "hi", "acb123")
        self.assertIn("paymentRequestToken", ans)

        #amount of open tikkies should be 1
        trans = self.tikkie.get_transactions()
        self.assertEqual(
                len(trans['paymentRequests']),
                1
                )

    @unittest.skipUnless(SLOW, "Slow test")
    def test_create_payment_request(self):
        ans = self.tikkie.create_payment_request(123, "PAYID")
        self.assertTrue(
                ans['url'].startswith("https://")
                )
        return ans

    @unittest.skipUnless(SLOW, "Slow test")
    def test_get_transaction_status(self):
        ans = self.tikkie.create_payment_request(123, "PAYID")
        status =  self.tikkie.payment_request_status(ans["payment_id"])

    @unittest.skipUnless(SLOW, "Slow test")
    def test_attempt_transaction_done(self):
        ans = self.tikkie.create_payment_request(123, "PAYID")
        status = self.tikkie.attempt_payment_done(ans["payment_id"])
        self.assertEqual(status, None)

    @unittest.skipUnless(SLOW, "Slow test")
    def test_callback(self):
        self.tikkie.set_callback_instance(Mock())
        self.tikkie.get_post_callback_routes()
        ans = self.tikkie.create_payment_request(123, "PAYID")
        status =  self.tikkie.payment_request_status(ans["payment_id"])
        self.tikkie.callback({'notificationType': 'PAYMENT', 'paymentRequestToken': status['paymentRequestToken']})

# class MyAppTestCase(AioHTTPTestCase):

#     async def get_application(self):
#         """
#         Override the get_app method to return your application.
#         """
#         import warnings
#         warnings.filterwarnings("ignore", category=DeprecationWarning)
#         app = web.Application()
#         self.abn_api_path = abn_api_path
#         self.tikkie = Tikkie(production=False, global_url="", url="/api/exchange/e2t/tikkie_callback",
#                 abn_api_path=self.abn_api_path, sandbox_key_path='~/.ssh/eurotoken/tikkie/tikkie_key_sandbox')

#     # @unittest_run_loop
#     # def test_register_listnener(self):
#     #     self.tikkie.register_payment_listener()
#     #     self.tikkie.create_request(10, "hi", "acb123")

