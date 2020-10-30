from stablecoin.bank.ing_sandbox import INGSandbox
from test.bank.test_ing import TestING

import os

class TestINGSandbox(TestING):

    def setUp(self):
        self.instance = INGSandbox()
        self.cert_path = os.path.join(os.getcwd(), "stablecoin/bank/ing_certs")

    def test_init(self):
        self.assertEqual(
                self.instance.api_url,
                "https://api.sandbox.ing.com"
                )
        self.assertEqual(
                self.instance.client_id,
                # client_id as provided in the documentation
                "e77d776b-90af-4684-bebc-521e5b2614dd"
                )

    def test__str__(self):
        self.assertEqual(str(self.instance), "ing sandbox")

    def test_get_greeting(self):
        "This api in not available for the sandbox"
        pass
