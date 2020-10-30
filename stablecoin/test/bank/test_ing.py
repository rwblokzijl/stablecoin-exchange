from stablecoin.bank.ing import ING
from stablecoin.settings import TestSettings

import unittest
import os

oauth = None
auth = None

def authenticate(instance):
    global oauth
    global auth

    if oauth is not None:
        instance.oauth  = oauth
        instance.auth   = auth
        # print(instance.oauth)
    else:
        # print("Authing once")
        instance.authenticate()

        oauth  = instance.oauth
        auth   = instance.auth
    pass

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

    @unittest.skipUnless(TestSettings.do_remote_tests, "Remote tests disabled")
    def test_create_payment_request(self):
        authenticate(self.instance)
        self.assertEqual(self.instance.create_payment_request(100), "create request")

    @unittest.skipUnless(TestSettings.do_remote_tests, "Remote tests disabled")
    def test_initiate_payment(self):
        authenticate(self.instance)
        self.assertEqual(self.instance.initiate_payment("INGB", 100), "initiate payment")

    @unittest.skipUnless(TestSettings.do_remote_tests, "Remote tests disabled")
    def test_authenticate(self):
        self.instance.authenticate()
        self.assertTrue("access_token" in self.instance.oauth.token)

    @unittest.skipUnless(TestSettings.do_remote_tests, "Remote tests disabled")
    def test_get_greeting(self):
        authenticate(self.instance)
        expected = {
            'message': 'Welcome to ING!',
            'id': 'SOME ID',
            'messageTimestamp': 'SOME TS'
        }
        # self.instance.authenticate()
        ans = self.instance.get(url="/greetings/single/").json()

        self.assertIn("message", ans)
        self.assertIn("id", ans)
        self.assertIn("messageTimestamp", ans)
        self.assertEqual(ans["message"], expected["message"])
