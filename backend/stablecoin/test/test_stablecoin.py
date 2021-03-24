import unittest
from unittest.mock import Mock

from stablecoin     import StablecoinInteractor
from test.util.captured_output import captured_output
from test.util.dict_ops        import extractDictAFromB
from test.util.TestPersistence import TestPersistence
from test.util.TestBank        import TestBank
from test.util.TestBlockchain  import TestBlockChain

class TestStablecoinBusinessLogic(unittest.TestCase):

    """Testing the business logic"""

    def setUp(self):
        self.bank        = TestBank()
        self.persistence = Mock()
        self.blockchain  = TestBlockChain()
        self.si = StablecoinInteractor(
                bank        = self.bank,
                persistence = self.persistence,
                blockchain  = self.blockchain,
                )

class TestStablecoinBusinessLogicCreation(TestStablecoinBusinessLogic):

    def test_verify_exchange_rate_success(self):
        collatoral_amount_cent = 100
        token_amount_cent      = 99

        verify = self.si.initiate_creation( collatoral_amount_cent, "ASDFASDF")

        self.assertEqual(verify["token_amount_cent"], token_amount_cent)

    def test_verify_exchange_rate_rounding(self):
        collatoral_amount_cent = 101
        token_amount_cent      = 99

        verify = self.si.initiate_creation( collatoral_amount_cent, "ASDFASDF")

        self.assertEqual(verify["token_amount_cent"], token_amount_cent)

    def test_wrong_exchange_rate_types(self):
        collatoral_amount_cent = 100.1

        with self.assertRaises(StablecoinInteractor.VerificationError):
            self.si.initiate_creation( collatoral_amount_cent, "ASDFASDF")

    def test_start_transaction(self):
        #setup
        collatoral_amount_cent = 100
        payment_data = {
                "link"   : "https://pay.moeneyyys.shrnarf/payment/<id>",
                "collatoral_amount_cent" : collatoral_amount_cent,
                "provider" : "bank",
                "timeout" : 3000,
                }

        # excecute
        rv = self.si.initiate_creation(collatoral_amount_cent=collatoral_amount_cent, destination_wallet="ASDFASDF")

        # asserts
        self.persistence.create_transaction.assert_called
        self.assertDictEqual(payment_data, extractDictAFromB(payment_data, rv))

    def test_paymentIdInTransaction(self):
        #setup
        collatoral_amount_cent = 100

        # excecute
        payment_data = self.si.initiate_creation(collatoral_amount_cent=collatoral_amount_cent,
                destination_wallet="ASDFASDF")

        # assert
        self.assertIn("payment_id", payment_data)

    # def test_forDifferentTransactionWithSameData_IdIsDifferent(self):
    def test_forDifferentTransactionWithDifferentData_IdIsDifferent(self):

        # excecute
        payment_id1   = self.si.initiate_creation(100, "ASDFASDF")["payment_id"]
        payment_id2   = self.si.initiate_creation(200, "ASDFASDF")["payment_id"]

        # assert
        self.assertNotEqual(payment_id1, payment_id2)

    def test_forDifferentTransactionWithSameData_IdIsDifferent(self):
        collatoral_amount_cent = 100

        # excecute
        payment_id1   = self.si.initiate_creation(collatoral_amount_cent, "ASDFASDF")["payment_id"]
        payment_id2   = self.si.initiate_creation(collatoral_amount_cent, "ASDFASDF")["payment_id"]

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
    #    transaction_data1 = si.initiate_creation(collatoral_amount_cent, "ASDFASDF")
    #    transaction_data2 = si.attempt_finish_creation_payment(transaction_data1["payment_id"])

    #    # assert
    #    self.assertEqual(transaction_data1, transaction_data2)
    #    return transaction_data1["payment_id"]

    def test_finishTransactionRegistersOnBlockChain(self):
        #setup
        collatoral_amount_cent = 100
        token_amount_cent      = 99
        blockchain = Mock()
        si = StablecoinInteractor(bank=TestBank(), persistence=TestPersistence(), blockchain=blockchain)

        transaction_data1 = si.initiate_creation(collatoral_amount_cent, "ASDFASDF")

        # excecute
        transaction_data2 = si.finish_creation_payment(transaction_data1["payment_id"])

        blockchain.transfer.assert_called_with("ASDFASDF", token_amount_cent)

    def test_finishingTransactionWithoutPaymentFinished_Fails(self):
        #setup
        collatoral_amount_cent = 100
        token_amount_cent      = 99
        payment_data = {
                "link"   : "https://pay.moeneyyys.shrnarf/payment/<id>",
                "collatoral_amount_cent" : collatoral_amount_cent,
                "provider" : "bank",
                "timeout" : 3000,
                }
        bank = Mock()
        bank.create_payment_request.return_value = payment_data
        bank.check_payment_status.return_value = "pending"
        blockchain = Mock()
        si = StablecoinInteractor(bank=bank, persistence=TestPersistence(), blockchain=blockchain)

        transaction_data1 = si.initiate_creation(collatoral_amount_cent, "ASDFASDF")

        # excecute
        transaction_data2 = si.finish_creation_payment(transaction_data1["payment_id"])

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

    #    verify = self.si.initiate_creation( collatoral_amount_cent, "ASDFASDF")

    #    self.assertEqual(verify["token_amount_cent"], token_amount_cent)

    #def test_wrong_exchange_rate_types(self):
    #    collatoral_amount_cent = 100.1

    #    with self.assertRaises(StablecoinInteractor.VerificationError):
    #        self.si.initiate_creation( collatoral_amount_cent, "ASDFASDF")

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
    #    rv = self.si.initiate_creation(collatoral_amount_cent=collatoral_amount_cent, destination_wallet="ASDFASDF")

    #    # asserts
    #    self.persistence.create_transaction.assert_called
    #    self.assertDictEqual(payment_data, extractDictAFromB(payment_data, rv))

    #def test_paymentIdInTransaction(self):
    #    #setup
    #    collatoral_amount_cent = 100

    #    # excecute
    #    payment_data = self.si.initiate_creation(collatoral_amount_cent=collatoral_amount_cent,
    #            destination_wallet="ASDFASDF")

    #    # assert
    #    self.assertIn("payment_id", payment_data)

    ## def test_forDifferentTransactionWithSameData_IdIsDifferent(self):
    #def test_forDifferentTransactionWithDifferentData_IdIsDifferent(self):

    #    # excecute
    #    payment_id1   = self.si.initiate_creation(100, "ASDFASDF")["payment_id"]
    #    payment_id2   = self.si.initiate_creation(200, "ASDFASDF")["payment_id"]

    #    # assert
    #    self.assertNotEqual(payment_id1, payment_id2)

    #def test_forDifferentTransactionWithSameData_IdIsDifferent(self):
    #    collatoral_amount_cent = 100

    #    # excecute
    #    payment_id1   = self.si.initiate_creation(collatoral_amount_cent, "ASDFASDF")["payment_id"]
    #    payment_id2   = self.si.initiate_creation(collatoral_amount_cent, "ASDFASDF")["payment_id"]

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
    #    transaction_data1 = si.initiate_creation(collatoral_amount_cent, "ASDFASDF")
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

    #    transaction_data1 = si.initiate_creation(collatoral_amount_cent, "ASDFASDF")

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

    #    transaction_data1 = si.initiate_creation(collatoral_amount_cent, "ASDFASDF")

    #    # excecute
    #    transaction_data2 = si.finish_creation_payment(transaction_data1["payment_id"])

    #    self.assertFalse(blockchain.transfer.called)
