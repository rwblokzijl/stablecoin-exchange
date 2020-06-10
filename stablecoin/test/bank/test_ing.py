from stablecoin.bank.ing import ING

import unittest
import os

class TestING(unittest.TestCase):

    def setUp(self):
        with open("/home/bloodyfool/.ssh/ing/id", 'rb') as fh:
            client_id = fh.read().strip().decode("utf-8")
        self.instance = ING(client_id=client_id)
        self.cert_path = os.path.expanduser("~/.ssh/ing")

    def tearDown(self):
        if self.instance.oauth:
            self.instance.oauth.close()

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

    def test_key_paths(self):
        signing_cer = os.path.join(self.instance.cert_path, 'httpCert.crt')
        signing_key = os.path.join(self.instance.cert_path, 'httpCert.key')
        tls_cer     = os.path.join(self.instance.cert_path, 'tlsCert.crt')
        tls_key     = os.path.join(self.instance.cert_path, 'tlsCert.key')

        self.assertTrue(  self.instance.file_signing_cer , signing_cer )
        self.assertTrue(  self.instance.file_signing_key , signing_key )
        self.assertTrue(  self.instance.file_tls_cer     , tls_cer     )
        self.assertTrue(  self.instance.file_tls_key     , tls_key     )

    def test_keyfile_exist(self):

        self.assertTrue(  os.path.isfile( self.instance.file_signing_cer )  )
        self.assertTrue(  os.path.isfile( self.instance.file_signing_key )  )
        self.assertTrue(  os.path.isfile( self.instance.file_tls_cer     )  )
        self.assertTrue(  os.path.isfile( self.instance.file_tls_key     )  )

    def test_get_certs(self):
        with open(os.path.join(self.instance.cert_path, 'httpCert.crt'), 'rb') as fh:
            signing_cer = fh.read()
        with open(os.path.join(self.instance.cert_path, 'httpCert.key'), 'rb')as fh:
            signing_key = fh.read()
        with open(os.path.join(self.instance.cert_path, 'tlsCert.crt'), 'rb') as fh:
            tls_cer     = fh.read()
        with open(os.path.join(self.instance.cert_path, 'tlsCert.key'), 'rb') as fh:
            tls_key     = fh.read()

        self.assertEqual( signing_cer  , self.instance.signing_cer  )
        self.assertEqual( signing_key  , self.instance.signing_key  )
        self.assertEqual( tls_cer      , self.instance.tls_cer      )
        self.assertEqual( tls_key      , self.instance.tls_key      )

    def test__str__(self):
        self.assertEqual(str(self.instance), "ing")

    def test_create_payment_request(self):
        self.assertEqual(self.instance.create_payment_request(100), "create request")

    def test_initiate_payment(self):
        self.assertEqual(self.instance.initiate_payment("INGB", 100), "initiate payment")

    def test_authenticate(self):
        self.instance.authenticate()
        self.assertTrue("access_token" in self.instance.oauth.token)

