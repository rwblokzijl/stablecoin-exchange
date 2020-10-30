from stablecoin.bank.ing import ING

import os

class INGSandbox(ING):
    def __init__(self):
        api_url = "https://api.sandbox.ing.com"
        client_id = "e77d776b-90af-4684-bebc-521e5b2614dd"
        cert_path = os.path.join(os.getcwd(), "stablecoin/bank/ing_certs")

        super().__init__(client_id=client_id, api_url=api_url, cert_path=cert_path)

    def __str__(self):
        return "ing sandbox"

