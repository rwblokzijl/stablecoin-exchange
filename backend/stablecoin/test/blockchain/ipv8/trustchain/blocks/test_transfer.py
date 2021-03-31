from test.blockchain.ipv8.trustchain.blocks.util import TestBlock, MockDatabase, getWalletBlockWithBalance

from pyipv8.ipv8.attestation.trustchain.block import EMPTY_SIG, GENESIS_HASH, GENESIS_SEQ, TrustChainBlock, ValidationResult

from blockchain.ipv8.trustchain.blocks.transfer  import EuroTokenTransferBlock
from blockchain.ipv8.trustchain.blocks.block_types import BlockTypes

import unittest

class TestEuroTokenTransfer(unittest.TestCase):

    def test_init(self):
        TestBlock(block_type=BlockTypes.TRANSFER)

    def test_valid_send(self):
        """
        Test Valid send after receiving
        """
        db = MockDatabase()

        A2 = getWalletBlockWithBalance(10, db)

        A3 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'balance': 0, 'amount': 10},
                previous = A2)

        result, errors = A3.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)

    def test_missing_amount(self):
        """
        Test missing amount
        """
        db = MockDatabase()

        A2 = getWalletBlockWithBalance(10, db)

        A3 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'balance': 0},
                previous = A2)

        result, errors = A3.validate_transaction(db)
        self.assertEqual(result, ValidationResult.invalid)
        self.assertIsInstance(errors[0], EuroTokenTransferBlock.MissingAmount)

    def test_invalid_send(self):
        "Balance is not deducted on transfer"
        db = MockDatabase()

        A2 = getWalletBlockWithBalance(10, db)

        A3 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'balance': 10, 'amount':10},
                previous = A2)

        result, errors = A3.validate_transaction(db)
        self.assertEqual(result, ValidationResult.invalid)
        self.assertIsInstance(errors[0], EuroTokenTransferBlock.InvalidBalance)

    def test_invalid_send2(self):
        "Balance is not available on transfer"
        db = MockDatabase()
        A1 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'balance': -10, 'amount': 10},)
        result, errors = A1.validate_transaction(db)
        self.assertEqual(result, ValidationResult.invalid)
        self.assertIsInstance(errors[0], EuroTokenTransferBlock.InsufficientBalance)
