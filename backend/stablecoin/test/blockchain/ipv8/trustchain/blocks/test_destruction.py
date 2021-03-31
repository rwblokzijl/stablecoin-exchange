from test.blockchain.ipv8.trustchain.blocks.util import TestBlock, MockDatabase, getWalletBlockWithBalance

from pyipv8.ipv8.attestation.trustchain.block import EMPTY_SIG, GENESIS_HASH, GENESIS_SEQ, TrustChainBlock, ValidationResult

from blockchain.ipv8.trustchain.blocks.destruction  import EuroTokenDestructionBlockListener, EuroTokenDestructionBlock
from blockchain.ipv8.trustchain.blocks.block_types import BlockTypes

from unittest.mock import Mock

import unittest

class TestEuroTokenDestruction(unittest.TestCase):

    def test_init(self):
        TestBlock(block_type=BlockTypes.DESTRUCTION)

    def test_valid_send_id(self):
        """
        Test Valid send after receiving
        """
        db = MockDatabase()

        A2 = getWalletBlockWithBalance(10, db)

        A3 = TestBlock(
                block_type=BlockTypes.DESTRUCTION,
                transaction={'balance': 0, 'amount': 10, 'payment_id': "ID"},
                previous = A2)

        result, errors = A3.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)

    def test_valid_send_iban(self):
        """
        Test Valid send after receiving
        """
        db = MockDatabase()

        A2 = getWalletBlockWithBalance(10, db)

        A3 = TestBlock(
                block_type=BlockTypes.DESTRUCTION,
                transaction={'balance': 0, 'amount': 10, 'iban': "IBAN"},
                previous = A2)

        result, errors = A3.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)

    def test_missing_amount(self):
        """
        Test Valid send after receiving
        """
        db = MockDatabase()

        A2 = getWalletBlockWithBalance(10, db)

        A3 = TestBlock(
                block_type=BlockTypes.DESTRUCTION,
                transaction={'balance': 0, 'payment_id': "ID"},
                previous = A2)

        result, errors = A3.validate_transaction(db)
        self.assertEqual(result, ValidationResult.invalid)
        self.assertIsInstance(errors[0], EuroTokenDestructionBlock.MissingAmount)

    def test_missing_payment_id_and_iban(self):
        """
        Test Valid send after receiving
        """
        db = MockDatabase()

        A2 = getWalletBlockWithBalance(10, db)

        A3 = TestBlock(
                block_type=BlockTypes.DESTRUCTION,
                transaction={'balance': 0, 'amount': 10},
                previous = A2)

        result, errors = A3.validate_transaction(db)
        self.assertEqual(result, ValidationResult.invalid)
        self.assertIsInstance(errors[0], EuroTokenDestructionBlock.MissingPaymentIDorIBAN)

    def test_invalid_send(self):
        """
        Test balance not deducted
        """
        db = MockDatabase()

        A2 = getWalletBlockWithBalance(10, db)

        A3 = TestBlock(
                block_type=BlockTypes.DESTRUCTION,
                transaction={'balance': 10, 'amount': 10, 'payment_id': "ID"},
                previous = A2)

        result, errors = A3.validate_transaction(db)
        self.assertEqual(result, ValidationResult.invalid)
        self.assertIsInstance(errors[0], EuroTokenDestructionBlock.InvalidBalance)

    def test_invalid_send2(self):
        "Balance is not available on transfer"
        db = MockDatabase()

        A1 = TestBlock(
                block_type=BlockTypes.DESTRUCTION,
                transaction={'balance': -10, 'amount': 10, 'payment_id':"ID"})
        result, errors = A1.validate_transaction(db)
        self.assertEqual(result, ValidationResult.invalid)
        self.assertIsInstance(errors[0], EuroTokenDestructionBlock.InsufficientBalance)

class TestEuroTokenDestructionBlockListener(unittest.TestCase):
    def test_init(self):
        class Comm():
            def __init__(self):
                self.eurotoken_blockchain = Mock()
                self.persistence = MockDatabase()
        c = Comm()
        l = EuroTokenDestructionBlockListener("peer", c)
        A2 = TestBlock(
                block_type=BlockTypes.DESTRUCTION,
                transaction={'balance': 0, 'amount': 10, 'iban': "IBAN"},
                )
        c.persistence.my_pk = A2.public_key
        l.should_sign(A2)
        l.received_block(A2)
