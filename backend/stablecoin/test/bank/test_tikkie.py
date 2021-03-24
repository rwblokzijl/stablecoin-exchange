from bank.tikkie import Tikkie

from pathlib import Path

import unittest

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from aiohttp import web

allTests = False

class TestTikkie(unittest.TestCase):

    """Test case docstring."""

    def __init__(self, *args, **kwargs):
        self.abn_api_path = '~/.ssh/abn_stablecoin_key'
        self.skipclass = not Path(self.abn_api_path).expanduser().is_file()
        return super(TestTikkie, self).__init__(*args, **kwargs)

    def setUp(self):
        if self.skipclass:
            raise unittest.SkipTest("No api key found at " + self.abn_api_path)
        self.tikkie = Tikkie(production=False, url="/", abn_api_path=self.abn_api_path, sandbox_key_path='~/.ssh/tikkie_key_sandbox')

    def tearDown(self):
        pass

    def new_env(self):
        self.tikkie.sandbox_key = self.tikkie.generate_new_sandbox_key()

    @unittest.skipIf(not allTests, "Too slow")
    def test_sandbox_apps(self):
        self.assertEqual(
                self.tikkie.generate_new_sandbox_key(),
                self.tikkie.get_key(self.tikkie.sandbox_key_path)
                )

    def test_header(self):
        headers = self.tikkie.get_headers()
        self.assertIn("API-Key", headers)
        self.assertIn("X-App-Token", headers)

    @unittest.skipIf(not allTests, "Too slow")
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
        self.assertIn("paymentRequestToken", ans.json())

        #amount of open tikkies should be 1
        trans = self.tikkie.get_transactions()
        self.assertEqual(
                len(trans['paymentRequests']),
                1
                )

    @unittest.skipIf(not allTests, "Too slow")
    def test_create_payment_request(self):
        ans = self.tikkie.create_payment_request(123, "PAYID")
        self.assertTrue(
                ans['url'].startswith("https://")
                )
        return ans

    @unittest.skipIf(not allTests, "Too slow")
    def test_get_transaction_status(self):
        ans = self.tikkie.create_payment_request(123, "PAYID")
        status =  self.tikkie.payment_request_status(ans["payment_id"])
        print(status)

class MyAppTestCase(AioHTTPTestCase):

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        import warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        app = web.Application()
        self.abn_api_path = '~/.ssh/abn_stablecoin_key'
        self.tikkie = Tikkie(production=False, global_url="http://bagn.blokzijl.family", url="/api/exchange/e2t/tikkie_callback", abn_api_path=self.abn_api_path, sandbox_key_path='~/.ssh/tikkie_key_sandbox')

    # @unittest_run_loop
    # def test_register_listnener(self):
    #     self.tikkie.register_payment_listener()
    #     self.tikkie.create_request(10, "hi", "acb123")

