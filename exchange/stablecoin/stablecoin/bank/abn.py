from stablecoin.bank.bank import Bank

class ABN(Bank):

    def __str__(self):
        return "abn"

    def create_payment_request(self, amount):
        return "create request"

    def initiate_payment(self, account, amount):
        return "initiate payment"

