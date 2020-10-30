from stablecoin.bank.payment_system import PaymentSystem

class TrustChain(PaymentSystem):

    def __str__(self):
        return "trustchain"

    "Payment end"

    "Step 0: Creation"
    #TODO
    def create_payment_request(self, amount):
        "Returns payment identifier string if succesful"
        "does nothing, simply"

    "Step 1: Waiting"
    #TODO
    def payment_request_status(self, identifier):
        "Returns status of transaction???, will include payee when payment successful"

    "Payout End"

    "Step 2: Start the payout"
    #TODO
    def initiate_payment(self, account, amount):
        "Returns true if succesful"
        pass

    "Bookkeeping functions"

    #TODO
    def list_transactions(self, account):
        pass

    #TODO
    def get_available_balance(self):
        pass

    "Blockchain Specific"

    def get_identity(self):
        return self.identity

    def get_available_balance(self):
        pass

    def create_payment_request(self):
        pass

    def initiate_payment(self):
        pass

    def list_transactions(self):
        return list()

    def payment_request_status(self, payment_id):
        pass

    def register_with_identity(self, identity):
        self.identity = identity
