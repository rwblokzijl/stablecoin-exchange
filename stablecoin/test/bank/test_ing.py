from stablecoin.bank.ing import ING

import unittest
import os

class TestING(unittest.TestCase):

    def setUp(self):
        self.instance = ING()
        self.cert_path = os.path.expanduser("~/.ssh/ing")

    def test_init(self):
        self.assertEqual(
                self.instance.api_url,
                "https://api.ing.com"
                )
        self.assertNotEqual(
                self.instance.client_id,
                # sandbox id
                "e77d776b-90af-4684-bebc-521e5b2614dd"
                )
        self.assertIsNotNone(
                self.instance.client_id
                )

    def test_cert_path(self):
        self.assertEqual(
                self.instance.cert_path,
                self.cert_path
                )
        self.assertTrue(os.path.isdir(self.instance.cert_path))

    def test_paths(self):
        signing_cer = os.path.join(self.cert_path, 'httpCert.crt')
        signing_key = os.path.join(self.cert_path, 'httpCert.key')
        tls_cer     = os.path.join(self.cert_path, 'tlsCert.crt')
        tls_key     = os.path.join(self.cert_path, 'tlsCert.key')

        self.assertTrue(  os.path.isfile( signing_cer )  )
        self.assertTrue(  os.path.isfile( signing_key )  )
        self.assertTrue(  os.path.isfile( tls_cer     )  )
        self.assertTrue(  os.path.isfile( tls_key     )  )

    def test__str__(self):
        raise
        self.assertEqual(str(self.instance), "ing")

    def test_create_payment_request(self):
        self.assertEqual(self.instance.create_payment_request(100), "create request")

    def test_initiate_payment(self):
        self.assertEqual(self.instance.initiate_payment("INGB", 100), "initiate payment")

    def test_authenticate(self):
        self.instance.authenticate()
        self.instance.auth.token

