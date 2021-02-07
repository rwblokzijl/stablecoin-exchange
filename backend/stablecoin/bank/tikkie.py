from stablecoin.bank.bank import Bank
import requests
from pathlib import Path

class Tikkie(Bank):

    def create_payment_request(self, amount, payment_id):
        "Returns payment destiation if successful"

        ans = self.create_request(amount=amount, description="EuroToken Exchange", referenceId=payment_id.replace("=", "_"))
        return {v:ans[k] for k, v in { 'url': 'url', 'paymentRequestToken': 'payment_id'}.items()}

    def initiate_payment(self, account, amount, payment_id):
        return None

    def attempt_payment_done(self, paymentRequestToken):
        status = self.payment_request_status(paymentRequestToken)
        if status and status["numberOfPayments"] > 0:
            return paymentRequestToken
        else:
            return None

    def payment_request_status(self, paymentRequestToken):
        url = self.get_url('paymentrequests') + f"/{paymentRequestToken}"
        x = requests.get(url, headers=self.get_headers())
        return x.json()

    def list_transactions(self):
        pass

    def get_available_balance(self):
        pass

    def get_transactions(self):
        url = self.get_url('paymentrequests')
        data = {
                "pageNumber": 0,
                "pageSize": 50
                }
        x = requests.get(url, headers=self.get_headers(), params=data)
        return x.json()

    def create_request(self, amount, description, referenceId, expiryDate="2999-12-31"):
        url = self.get_url('paymentrequests')
        data = {
                "amountInCents": amount, #empty is open req
                "description": description, #required, string <= 35 characters
                "expiryDate": expiryDate, #string Format yyyy-mm-dd, empty allowed, effect not tested
                "referenceId": referenceId #ID for the reference of the API consumer.
                }
        x = requests.post(url, headers=self.get_headers(), json=data)
        return x.json()

    def get_post_callback_routes(self):
        return {self.url : self.callback}

    def get_post_callback_url(self):
        return self.global_url + self.url

    def callback(self, post_json):
        if post_json['notificationType'] == 'PAYMENT':
            status = self.payment_request_status( post_json['paymentRequestToken'] )
            payment_id = status['referenceId'].replace('_', '=')
            self.stablecoin.CREATE_finish_payment(payment_id)

    def register_payment_listener(self):
        url = self.get_url('paymentrequestssubscription')
        data = {
                "url": self.get_post_callback_url()
                }
        x = requests.post(url, headers=self.get_headers(), json=data)
        return x

    def __init__(self, abn_api_path, sandbox_key_path, global_url, url="/api/exchange/e2t/tikkie_callback", production=False, production_key_path=None):
        if production and not production_key_path:
            raise

        self.production          = production
        self.sandbox_key_path    = sandbox_key_path
        self.production_key_path = production_key_path
        self.abn_api_path        = abn_api_path
        self.url                 = url
        self.global_url          = global_url

        self.abn_api_key        = self.get_key(abn_api_path)
        if self.production:
            self.production_key = self.get_key(production_key_path)
            if not self.production_key:
                raise
        else:
            self.sandbox_key    = self.get_key(sandbox_key_path) or self.generate_new_sandbox_key()
        self.register_payment_listener()

    def generate_new_sandbox_key(self):
        url = self.get_url("sandboxapps")
        x = requests.post(url, headers={'API-Key': self.abn_api_key})
        if x.status_code != 201:
            raise
        else:
            key = x.json()["appToken"]
            with open(Path(self.sandbox_key_path).expanduser(), 'w') as filetowrite:
                filetowrite.write(key)
            return key

    def get_key(self, key):
        # try:
        with open(Path(key).expanduser(), 'rb') as stream:
            api_key = stream.read()
        return api_key.decode('utf-8').strip()
        # except:
        #     return None

    def get_headers(self):
        if self.production:
            app_token=self.production_key
        else:
            app_token=self.sandbox_key
        return {'X-App-Token': app_token, "API-Key": self.abn_api_key}

    def get_url(self, endpoint):
        if self.production:
            return "https://api.abnamro.com/v2/tikkie/"+endpoint
        else:
            return "https://api-sandbox.abnamro.com/v2/tikkie/"+endpoint

    def __str__(self):
        return "tikkie"

