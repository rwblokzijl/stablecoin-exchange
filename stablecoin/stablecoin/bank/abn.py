from stablecoin.bank.bank import Bank

class ABN(Bank):

    def __str__(self):
        return "abn"

    def create_payment_request(self, amount):
        return "create request"

    def initiate_payment(self, account, amount):
        return "initiate payment"

    def payment_request_status(self):
        pass

    def list_transactions(self):
        pass

    def get_available_balance(self):
        pass
