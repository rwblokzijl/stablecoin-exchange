import unittest
from unittest.mock import Mock, MagicMock

from stablecoin                import StablecoinInteractor
from transaction               import Transaction

from persistence.inmemorypersistence      import InMemoryPersistence
from test.util.captured_output import captured_output
from test.util.dict_ops        import extractDictAFromB

from test.util.MockPersistence import MockPersistence
from test.util.MockBank        import MockBank
from test.util.MockBlockchain  import MockBlockchain

class TestStablecoinBusinessLogic(unittest.TestCase):

    """Testing the business logic"""

    def getInteractor(self,
            name        = "Test interactor",
            bank        = None,
            persistence = None,
            blockchain  = None,
            rateE2T     = 1.00,
            rateT2E     = 1.00
            ):
        if bank is None:
            bank = MockBank()
        if persistence is None:
            persistence = InMemoryPersistence()
        if blockchain is None:
            blockchain = MockBlockchain()
        return StablecoinInteractor( name, bank, persistence, blockchain, rateE2T, rateT2E)

    def setUp(self):
        self.bank        = MockBank()
        self.persistence = Mock()
        self.blockchain  = MockBlockchain()
        self.si = self.getInteractor()

class TestStablecoinBusinessLogicCreation(TestStablecoinBusinessLogic):

    def test_verify_exchange_rate_success(self):
        si = self.getInteractor(rateE2T=0.99)
        collatoral_amount_cent = 100
        token_amount_cent      = 99

        verify = si.CREATE_initiate( collatoral_amount_cent )

        self.assertEqual(verify["payout_amount"], token_amount_cent)

    def test_verify_exchange_rate_rounding(self):
        si = self.getInteractor(rateE2T=0.99)
        collatoral_amount_cent = 101
        token_amount_cent      = 99

        verify = si.CREATE_initiate( collatoral_amount_cent)

        self.assertEqual(verify["payout_amount"], token_amount_cent)

    def test_wrong_exchange_rate_types(self):
        collatoral_amount_cent = 100.1

        with self.assertRaises(StablecoinInteractor.VerificationError):
            self.si.CREATE_initiate( collatoral_amount_cent)

    def test_start_transaction(self):
        #setup
        payment_data = {
                "link"   : "https://pay.moeneyyys.shrnarf/payment/<id>",
                "payment_id": "TESTID"
                }

        persistence = Mock()

        si = self.getInteractor(persistence=persistence)

        # excecute
        trans = si.CREATE_initiate(collatoral_amount_cent=100)

        # asserts
        persistence.create_transaction.assert_called

    def test_paymentIdInTransaction(self):
        #setup
        collatoral_amount_cent = 100

        # excecute
        payment_data = self.si.CREATE_initiate(collatoral_amount_cent=collatoral_amount_cent)

        # assert
        self.assertIn("payment_id", payment_data)

    # def test_forDifferentTransactionWithSameData_IdIsDifferent(self):
    def test_forDifferentTransactionWithDifferentData_IdIsDifferent(self):

        # excecute
        payment_id1   = self.si.CREATE_initiate(100)["payment_id"]
        payment_id2   = self.si.CREATE_initiate(200)["payment_id"]

        # assert
        self.assertNotEqual(payment_id1, payment_id2)

    def test_forDifferentTransactionWithSameData_IdIsDifferent(self):
        collatoral_amount_cent = 100

        # excecute
        payment_id1   = self.si.CREATE_initiate(collatoral_amount_cent)["payment_id"]
        payment_id2   = self.si.CREATE_initiate(collatoral_amount_cent)["payment_id"]

        # assert
        self.assertNotEqual(payment_id1, payment_id2)

    def test_normalProgressionUntilPayout(self):
        blockchain = Mock()
        si = self.getInteractor(blockchain=blockchain)

        trans = transaction_data1 = si.CREATE_initiate(100)

        pid = trans["payment_id"]

        self.assertEqual(trans["status"], Transaction.Status.CREATED)

        # excecute
        trans = si.CREATE_connect(transaction_data1["payment_id"], "KEY", "IP", "PORT")
        self.assertEqual(trans["status"], Transaction.Status.PAYMENT_READY)
        trans = si.CREATE_start_payment(transaction_data1["payment_id"])
        self.assertEqual(trans["status"], Transaction.Status.PAYMENT_PENDING)
        trans = si.CREATE_finish_payment(transaction_data1["payment_id"])
        self.assertEqual(trans["status"], Transaction.Status.PAYOUT_DONE)

        blockchain.initiate_payment.assert_called_with({'pubkey': 'KEY', 'ip': 'IP', 'port': 'PORT'}, 100, pid)

    def test_finishingTransactionWithoutPaymentFinished_Fails(self):
        #setup
        payment_data = {
                "link"   : "https://pay.moeneyyys.shrnarf/payment/<id>",
                "payment_id" : "TESTID",
                }
        bank = Mock()
        bank.create_payment_request.return_value = payment_data
        bank.check_payment_status.return_value = "pending"
        blockchain = Mock()
        si = self.getInteractor(bank=bank, blockchain=blockchain)

        transaction_data1 = si.CREATE_initiate(100)

        # excecute
        trans = si.CREATE_finish_payment(transaction_data1["payment_id"])

        self.assertFalse(blockchain.transfer.called)

    def test_wrong_id_connect(self):
        ans = self.si.CREATE_connect("MISSING", "KEY", "IP", "PORT")
        self.assertEqual(ans, None)

    def test_wrong_id_start_payment(self):
        ans = self.si.CREATE_start_payment("MISSING")
        self.assertEqual(ans, None)

    def test_wrong_id_finish_payment(self):
        ans = self.si.CREATE_finish_payment("MISSING")
        self.assertEqual(ans, None)

    def test_wrong_state_connect(self):
        data = self.si.CREATE_initiate(100)
        self.si.CREATE_connect(data["payment_id"], "KEY", "IP", "PORT")
        self.si.CREATE_start_payment(data["payment_id"])
        self.si.CREATE_finish_payment(data["payment_id"])

        ans = self.si.CREATE_connect(data["payment_id"], "KEY", "IP", "PORT")
        self.assertEqual(ans, None)

    def test_wrong_state_payment(self):
        data = self.si.CREATE_initiate(100)
        ans = self.si.CREATE_start_payment(data["payment_id"])
        self.assertEqual(ans, None)

    def test_wrong_state_finish(self):
        data = self.si.CREATE_initiate(100)
        ans = self.si.CREATE_finish_payment(data["payment_id"])
        self.assertEqual(ans, None)

class TestStablecoinBusinessLogicDestruction(TestStablecoinBusinessLogic):

    def test_destroy_flow(self):
        data = self.si.DESTROY_initiate(100, "IBAN")
        self.assertEqual(data['status'], Transaction.Status.PAYMENT_PENDING)
        ans =  self.si.DESTROY_pay(data["payment_id"], None, 100, "KEY")
        self.assertEqual(data['status'], Transaction.Status.PAYOUT_DONE)

    def test_destroy_instant_flow(self):
        data = self.si.DESTROY_pay(None, "IBAN", 100, "KEY")
        self.assertEqual(data['status'], Transaction.Status.PAYOUT_DONE)

    def test_destroy_flow_wrong_amount(self):
        data = self.si.DESTROY_initiate(101, "iban")
        self.assertEqual(data['status'], Transaction.Status.PAYMENT_PENDING)
        ans =  self.si.DESTROY_pay(data["payment_id"], None, 100, "KEY")
        self.assertEqual(ans, None)

    def test_destroy_flow_wrong_state(self):
        data = self.si.DESTROY_initiate(100, "IBAN")
        self.assertEqual(data['status'], Transaction.Status.PAYMENT_PENDING)
        ans =  self.si.DESTROY_pay(data["payment_id"], None, 100, "KEY")
        self.assertEqual(data['status'], Transaction.Status.PAYOUT_DONE)
        ans =  self.si.DESTROY_pay(data["payment_id"], None, 100, "KEY")
        self.assertEqual(ans, None)

    def test_destroy_flow_wrong_payment_id(self):
        ans =  self.si.DESTROY_pay("MISSING", None, 100, "KEY")
        self.assertEqual(ans, None)
