from stablecoin.bank.bank import Bank
from stablecoin.bank.util.HttpSignatureAuth import HTTPSignatureAuth
from oauthlib.oauth2 import BackendApplicationClient

import os

from requests_oauthlib import OAuth2Session

class ING(Bank):

    def __init__(self,
            client_id, api_url="https://api.ing.com", cert_path="~/.ssh/ing"):

        self.api_url   = api_url
        self.client_id = client_id
        self.cert_path = os.path.abspath(os.path.expanduser(cert_path))
        self.oauth     = None

        self.setCertificate_paths()
        self.setCertificates()

    def setCertificate_paths(self):
        self.file_signing_cer = os.path.join(self.cert_path, 'httpCert.crt')
        self.file_signing_key = os.path.join(self.cert_path, 'httpCert.key')
        self.file_tls_cer     = os.path.join(self.cert_path, 'tlsCert.crt')
        self.file_tls_key     = os.path.join(self.cert_path, 'tlsCert.key')

    def setCertificates(self):
        with open(os.path.join(self.cert_path, 'httpCert.crt'), 'rb') as fh:
            self.signing_cer = fh.read()
        with open(os.path.join(self.cert_path, 'httpCert.key'), 'rb')as fh:
            self.signing_key = fh.read()
        with open(os.path.join(self.cert_path, 'tlsCert.crt'), 'rb') as fh:
            self.tls_cer     = fh.read()
        with open(os.path.join(self.cert_path, 'tlsCert.key'), 'rb') as fh:
            self.tls_key     = fh.read()

    def authenticate(self):
        auth   = HTTPSignatureAuth(
                algorithm="rsa-sha256",
                headers=[ '(request-target)', 'date', 'digest' ],
                key=self.signing_key,
                key_id=self.client_id)

        client = BackendApplicationClient(client_id=self.client_id, key=self.tls_key, cert=self.tls_cer)
        self.oauth = OAuth2Session(client=client)
        self.oauth.cert=(self.file_tls_cer, self.file_tls_key)
        self.oauth.fetch_token(token_url=self.api_url+"/oauth2/token",
                client_id=self.client_id,
                auth=auth,
                )

    def __str__(self):
        return "ing"

    def create_payment_request(self, amount):
        return "create request"

    def initiate_payment(self, account, amount):
        return "initiate payment"

