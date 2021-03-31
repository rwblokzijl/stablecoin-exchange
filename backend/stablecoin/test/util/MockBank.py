from bank.bank import Bank

class MockBank(Bank):

    def __str__(self):
        return "MockBank"

    def create_payment_request(self, amount, payment_id):
        return {
                "url"   : f"https://pay.moeneyyys.shrnarf/payment/{payment_id}>",
                "payment_id": payment_id
                }

    def initiate_payment(self, account, amount, payment_id):
        pass

    def check_payment_status(self, tid):
        return "done"

    def get_available_balance(self):
        return 100

    def list_transactions(self):
        return list()

    def payment_request_status(self, pid):
        return pid

    def attempt_payment_done(self, pid):
        return pid
