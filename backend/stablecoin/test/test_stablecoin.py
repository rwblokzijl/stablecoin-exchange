import unittest
from unittest.mock import Mock, MagicMock

from stablecoin                import StablecoinInteractor
from transaction               import Transaction

from persistence.inmemorypersistence      import InMemoryPersistence
from test.util.captured_output import captured_output
from test.util.dict_ops        import extractDictAFromB
from test.util.TestPersistence import TestPersistence
from test.util.TestBank        import TestBank
from test.util.TestBlockchain  import TestBlockChain

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
            bank = TestBank()
        if persistence is None:
            persistence = InMemoryPersistence()
        if blockchain is None:
            blockchain = TestBlockChain()
        return StablecoinInteractor( name, bank, persistence, blockchain, rateE2T, rateT2E)

    def setUp(self):
        self.bank        = TestBank()
        self.persistence = Mock()
        self.blockchain  = TestBlockChain()
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

    #def test_finishTransaction_returnsSameTransaction(self):
    #    #setup
    #    collatoral_amount_cent = 100
    #    transaction = {
    #            "status" : 3000,
    #            }
    #    si = StablecoinInteractor(bank=TestBank(), persistence=TestPersistence(), blockchain=Mock() )

    #    # excecute
    #    transaction_data1 = si.CREATE_initiate(collatoral_amount_cent")
    #    transaction_data2 = si.attempt_finish_creation_payment(transaction_data1["payment_id"])
        #setup

    #    # assert
    #    self.assertEqual(transaction_data1, transaction_data2)
    #    return transaction_data1["payment_id"]

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

class TestStablecoinBusinessLogicDestruction(TestStablecoinBusinessLogic):
    pass

    # def test_verify_exchange_rate_success(self):
    #     token_amount_cent      = 100
    #     collatoral_amount_cent = 99

    #     verify = self.si.initiate_destruction( token_amount_cent, "IBAN")

    #     self.assertEqual(verify["collatoral_amount_cent"], collatoral_amount_cent)

    #def test_verify_exchange_rate_rounding(self):
    #    collatoral_amount_cent = 101
    #    token_amount_cent      = 99

    #    verify = self.si.CREATE_initiate( collatoral_amount_cent)

    #    self.assertEqual(verify["token_amount_cent"], token_amount_cent)

    #def test_wrong_exchange_rate_types(self):
    #    collatoral_amount_cent = 100.1

    #    with self.assertRaises(StablecoinInteractor.VerificationError):
    #        self.si.CREATE_initiate( collatoral_amount_cent)

    #def test_start_transaction(self):
    #    #setup
    #    collatoral_amount_cent = 100
    #    payment_data = {
    #            "link"   : "https://pay.moeneyyys.shrnarf/payment/<id>",
    #            "collatoral_amount_cent" : collatoral_amount_cent,
    #            "provider" : "bank",
    #            "timeout" : 3000,
    #            }

    #    # excecute
    #    rv = self.si.CREATE_initiate(collatoral_amount_cent=collatoral_amount_cent)

    #    # asserts
    #    self.persistence.create_transaction.assert_called
    #    self.assertDictEqual(payment_data, extractDictAFromB(payment_data, rv))

    #def test_paymentIdInTransaction(self):
    #    #setup
    #    collatoral_amount_cent = 100

    #    # excecute
    #    payment_data = self.si.CREATE_initiate(collatoral_amount_cent=collatoral_amount_cent)
    #    # assert
    #    self.assertIn("payment_id", payment_data)

    ## def test_forDifferentTransactionWithSameData_IdIsDifferent(self):
    #def test_forDifferentTransactionWithDifferentData_IdIsDifferent(self):

    #    # excecute
    #    payment_id1   = self.si.CREATE_initiate(100)["payment_id"]
    #    payment_id2   = self.si.CREATE_initiate(200)["payment_id"]

    #    # assert
    #    self.assertNotEqual(payment_id1, payment_id2)

    #def test_forDifferentTransactionWithSameData_IdIsDifferent(self):
    #    collatoral_amount_cent = 100

    #    # excecute
    #    payment_id1   = self.si.CREATE_initiate(collatoral_amount_cent)["payment_id"]
    #    payment_id2   = self.si.CREATE_initiate(collatoral_amount_cent)["payment_id"]

    #    # assert
    #    self.assertNotEqual(payment_id1, payment_id2)

    #def test_finishTransaction_returnsSameTransaction(self):
    #    #setup
    #    collatoral_amount_cent = 100
    #    payment_data = {
    #            "link"   : "https://pay.moeneyyys.shrnarf/payment/<id>",
    #            "collatoral_amount_cent" : collatoral_amount_cent,
    #            "provider" : "bank",
    #            "timeout" : 3000,
    #            }
    #    si = StablecoinInteractor(bank=TestBank(), persistence=TestPersistence(), blockchain=Mock() )

    #    # excecute
    #    transaction_data1 = si.CREATE_initiate(collatoral_amount_cent)
    #    transaction_data2 = si.finish_creation_payment(transaction_data1["payment_id"])

    #    # assert
    #    self.assertEqual(transaction_data1, transaction_data2)
    #    return transaction_data1["payment_id"]

    #def test_finishTransactionRegistersOnBlockChain(self):
    #    #setup
    #    collatoral_amount_cent = 100
    #    token_amount_cent      = 99
    #    blockchain = Mock()
    #    si = StablecoinInteractor(bank=TestBank(), persistence=TestPersistence(), blockchain=blockchain)

    #    transaction_data1 = si.CREATE_initiate(collatoral_amount_cent)

    #    # excecute
    #    transaction_data2 = si.finish_creation_payment(transaction_data1["payment_id"])

    #    blockchain.transfer.assert_called_with("ASDFASDF", token_amount_cent)

    #def test_finishingTransactionWithoutPaymentFinished_Fails(self):
    #    #setup
    #    collatoral_amount_cent = 100
    #    token_amount_cent      = 99
    #    payment_data = {
    #            "link"   : "https://pay.moeneyyys.shrnarf/payment/<id>",
    #            "collatoral_amount_cent" : collatoral_amount_cent,
    #            "provider" : "bank",
    #            "timeout" : 3000,
    #            }
    #    bank = Mock()
    #    bank.create_payment_request.return_value = payment_data
    #    bank.check_payment_status.return_value = "pending"
    #    blockchain = Mock()
    #    si = StablecoinInteractor(bank=bank, persistence=TestPersistence(), blockchain=blockchain)

    #    transaction_data1 = si.CREATE_initiate(collatoral_amount_cent)

    #    # excecute
    #    transaction_data2 = si.finish_creation_payment(transaction_data1["payment_id"])

    #    self.assertFalse(blockchain.transfer.called)
