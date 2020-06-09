from stablecoin.bank.bank import Bank

import os

from requests_oauthlib import OAuth2Session

class ING(Bank):

    def __init__(self,
            client_id="", api_url="https://api.ing.com", cert_path="~/.ssh/ing"):
        self.api_url   = api_url
        self.client_id = client_id
        self.cert_path = os.path.abspath(os.path.expanduser(cert_path))

        self.setCertificates()

    def setCertificates(self):
        self.signing_cer = os.path.join(self.cert_path, 'httpCert.crt')
        self.signing_key = os.path.join(self.cert_path, 'httpCert.key')
        self.tls_cer     = os.path.join(self.cert_path, 'tlsCert.crt')
        self.tls_key     = os.path.join(self.cert_path, 'tlsCert.key')

    def authenticate(self):
        self.auth = OAuth2Session()

    def __str__(self):
        return "ing"

    def create_payment_request(self, amount):
        return "create request"

    def initiate_payment(self, account, amount):
        return "initiate payment"

