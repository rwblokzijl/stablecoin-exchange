from stablecoin.bank.bank import Bank

class TestBank(Bank):

    def __str__(self):
        return "TestBank"

    def create_payment_request(self, amount):
        return {
                "link"   : "https://pay.moeneyyys.shrnarf/payment/<id>",
                "collatoral_amount_cent" : amount,
                "provider" : "bank",
                "timeout" : 3000,
                }

    def initiate_payment(self, account, amount):
        pass

    def check_payment_status(self, tid):
        return "done"

    def get_available_balance(self):
        return 100

    def list_transactions(self):
        return list()

    def payment_request_status(self, id):
        return "done"
