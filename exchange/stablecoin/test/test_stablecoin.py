import unittest
from unittest import mock

from stablecoin.stablecoin import StabecoinInteractor
from test.util.captured_output import captured_output
from test.util.dict_ops import extractDictAFromB

from stablecoin.bank.bank               import Bank
from stablecoin.persistence.persistence import Persistence
from stablecoin.blockchain.blockchain   import Blockchain

# from stablecoin.ui.ui                   import UI

class TestStablecoinBusinessLogic(unittest.TestCase):

    class TestPersistence:
        payment_data = {
                }
        def create_transaction(self, payment_data):
            self.payment_data[payment_data["payment_id"]] = payment_data

        def get_payment_by_id(self, transaction_id):
            return self.payment_data[transaction_id]

    """Testing the business logic"""

    def setUp(self):
        self.bank        = mock.MagicMock(name="bank")
        self.persistence = mock.MagicMock(name="persistence")
        self.blockchain  = mock.MagicMock(name="blockchain")
        self.si = StabecoinInteractor(
                bank        = self.bank,
                persistence = self.persistence,
                blockchain  = self.blockchain,
                )
        pass

    def test_verify_exchange_rate_success(self):
        collatoral_amount_cent = 100
        token_amount_cent      = 99

        verify = self.si.get_exchange_rate( collatoral_amount_cent)

        self.assertEqual(verify, token_amount_cent)

    def test_verify_exchange_rate_ceil(self):
        collatoral_amount_cent = 101
        token_amount_cent      = 100

        verify = self.si.get_exchange_rate( collatoral_amount_cent)

        self.assertEqual(verify, token_amount_cent)

    def test_wrong_exchange_rate_types(self):
        collatoral_amount_cent = 100.1

        with self.assertRaises(StabecoinInteractor.VerificationError):
            self.si.get_exchange_rate( collatoral_amount_cent )

    def test_start_transaction(self):
        #setup
        collatoral_amount_cent = 100
        payment_data = {
                "link"   : "https://pay.moeneyyys.shrnarf/payment/<id>",
                "collatoral_amount_cent" : collatoral_amount_cent,
                "provider" : "bank",
                "timeout" : 3000,
                }
        self.bank.initiate_payment.return_value = payment_data

        # excecute
        rv = self.si.start_transaction(collatoral_amount_cent=collatoral_amount_cent, destination_wallet="ASDFASDF")

        # asserts
        self.persistence.create_transaction.assert_called_with(payment_data)
        self.assertDictEqual(payment_data, extractDictAFromB(payment_data, rv))

    def test_paymentIdInTransaction(self):
        #setup
        collatoral_amount_cent = 100
        payment_data = {
                "link"   : "https://pay.moeneyyys.shrnarf/payment/<id>",
                "collatoral_amount_cent" : collatoral_amount_cent,
                "provider" : "bank",
                "timeout" : 3000,
                }
        self.bank.initiate_payment.return_value = payment_data

        # excecute
        payment_data = self.si.start_transaction(collatoral_amount_cent=collatoral_amount_cent,
                destination_wallet="ASDFASDF")

        # assert
        self.assertIn("payment_id", payment_data)

    # def test_forDifferentTransactionWithSameData_IdIsDifferent(self):
    def test_forDifferentTransactionWithDifferentData_IdIsDifferent(self):
        payment_data1  = {
                "link"   : "https://pay.moeneyyys.shrnarf/payment/<id>",
                "collatoral_amount_cent" : 100,
                "provider" : "bank",
                "timeout" : 3000,
                }
        payment_data2  = {
                "link"   : "https://pay.moeneyyys.shrnarf/payment/<id>",
                "collatoral_amount_cent" : 200,
                "provider" : "bank",
                "timeout" : 3000,
                }

        # excecute
        self.bank.initiate_payment.return_value = payment_data1
        payment_id1   = self.si.start_transaction(100, "ASDFASDF")["payment_id"]
        self.bank.initiate_payment.return_value = payment_data2
        payment_id2   = self.si.start_transaction(200, "ASDFASDF")["payment_id"]

        # assert
        self.assertNotEqual(payment_id1, payment_id2)

    def test_forDifferentTransactionWithSameData_IdIsDifferent(self):
        collatoral_amount_cent = 100
        payment_data1  = {
                "link"   : "https://pay.moeneyyys.shrnarf/payment/<id>",
                "collatoral_amount_cent" : collatoral_amount_cent,
                "provider" : "bank",
                "timeout" : 3000,
                }
        payment_data2  = {
                "link"   : "https://pay.moeneyyys.shrnarf/payment/<id>",
                "collatoral_amount_cent" : collatoral_amount_cent,
                "provider" : "bank",
                "timeout" : 3000,
                }

        # excecute
        self.bank.initiate_payment.return_value = payment_data1
        payment_id1   = self.si.start_transaction(collatoral_amount_cent, "ASDFASDF")["payment_id"]
        self.bank.initiate_payment.return_value = payment_data2
        payment_id2   = self.si.start_transaction(collatoral_amount_cent, "ASDFASDF")["payment_id"]

        # assert
        self.assertNotEqual(payment_id1, payment_id2)

    def test_finishTransaction_returnsSameTransaction(self):
        #setup
        collatoral_amount_cent = 100
        payment_data = {
                "link"   : "https://pay.moeneyyys.shrnarf/payment/<id>",
                "collatoral_amount_cent" : collatoral_amount_cent,
                "provider" : "bank",
                "timeout" : 3000,
                }
        bank = mock.Mock()
        bank.initiate_payment.return_value = payment_data
        bank.check_payment_status.return_value = "done"
        si = StabecoinInteractor(bank=bank, persistence=self.TestPersistence(), blockchain=mock.Mock() )

        # excecute
        transaction_data1 = si.start_transaction(collatoral_amount_cent, "ASDFASDF")
        transaction_data2 = si.finish_transaction(transaction_data1["payment_id"])

        # assert
        self.assertEqual(transaction_data1, transaction_data2)
        return transaction_data1["payment_id"]

    def test_finishTransactionRegistersOnBlockChain(self):
        #setup
        collatoral_amount_cent = 100
        token_amount_cent      = 99
        payment_data = {
                "link"   : "https://pay.moeneyyys.shrnarf/payment/<id>",
                "collatoral_amount_cent" : collatoral_amount_cent,
                "provider" : "bank",
                "timeout" : 3000,
                }
        bank = mock.Mock()
        bank.initiate_payment.return_value = payment_data
        bank.check_payment_status.return_value = "done"
        blockchain = mock.Mock()
        si = StabecoinInteractor(bank=bank, persistence=self.TestPersistence(), blockchain=blockchain)

        transaction_data1 = si.start_transaction(collatoral_amount_cent, "ASDFASDF")

        # excecute
        transaction_data2 = si.finish_transaction(transaction_data1["payment_id"])

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
        bank = mock.Mock()
        bank.initiate_payment.return_value = payment_data
        bank.check_payment_status.return_value = "pending"
        blockchain = mock.Mock()
        si = StabecoinInteractor(bank=bank, persistence=self.TestPersistence(), blockchain=blockchain)

        transaction_data1 = si.start_transaction(collatoral_amount_cent, "ASDFASDF")

        # excecute
        transaction_data2 = si.finish_transaction(transaction_data1["payment_id"])

        self.assertFalse(blockchain.transfer.called)


