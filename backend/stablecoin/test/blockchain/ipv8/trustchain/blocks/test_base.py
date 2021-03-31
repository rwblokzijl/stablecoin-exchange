from test.blockchain.ipv8.trustchain.blocks.util import TestBlock, MockDatabase

from pyipv8.ipv8.attestation.trustchain.block import EMPTY_SIG, GENESIS_HASH, GENESIS_SEQ, TrustChainBlock, ValidationResult

from blockchain.ipv8.trustchain.blocks.base       import EuroTokenBlockListener, EuroTokenBlock
from blockchain.ipv8.trustchain.blocks.block_types import BlockTypes

import unittest

class TestEuroTokenBlock(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        "Test the creation of a block"
        block = TestBlock(block_type=BlockTypes.CHECKPOINT)
        block.hash

    def test_str(self):
        "Test the string call on a block"
        block = TestBlock(block_type=BlockTypes.CHECKPOINT)
        str(block)

    def test_valid_balance_genesis(self):
        """
        Test validating a genesis block with 0 balance
        """
        db = MockDatabase()
        prev = TestBlock(block_type=BlockTypes.CHECKPOINT, transaction={'balance': 0})
        result, errors = prev.validate_transaction(db)
        self.assertEqual(result, ValidationResult.valid)
        self.assertEqual(errors, [])
        db.add_block(prev)

    def test_invalid_balance_genesis(self):
        """
        Test validating a genesis block with an unearned balance
        """
        db = MockDatabase()
        prev = TestBlock(block_type=BlockTypes.CHECKPOINT, transaction={'balance': 1})
        result, errors = prev.validate_transaction(db)
        self.assertEqual(result, ValidationResult.invalid)
        self.assertIsInstance(errors[0], EuroTokenBlock.InvalidBalance)

    def test_missing_balance(self):
        """
        Test validating a genesis block without a balance
        """
        db = MockDatabase()

        prev = TestBlock(block_type=BlockTypes.CHECKPOINT, transaction={})
        result, errors = prev.validate_transaction(db)
        self.assertEqual(result, ValidationResult.invalid)
        self.assertIsInstance(errors[0], EuroTokenBlock.MissingBalance)

    def test_double_validate(self):
        """
        Test validating a block that points towards a previous block
        """
        db = MockDatabase()

        prev = TestBlock(block_type=BlockTypes.CHECKPOINT, transaction={'balance': 0})
        result, errors = prev.validate_transaction(db)
        self.assertEqual(result, ValidationResult.valid)
        self.assertEqual(errors, [])
        db.add_block(prev)

        block = TestBlock(block_type=BlockTypes.CHECKPOINT, transaction={'balance': 0}, previous=prev)
        result, errors = block.validate_transaction(db)
        self.assertEqual(result, ValidationResult.valid)
        self.assertEqual(errors, [])

    def test_missing_previous(self):
        """
        Test validating a block that points towards a missing previous block
        """
        db = MockDatabase()

        prev = TestBlock(block_type=BlockTypes.CHECKPOINT, transaction={'balance': 0})
        result, errors = prev.validate_transaction(db)
        self.assertEqual(result, ValidationResult.valid)
        self.assertEqual(errors, [])

        block = TestBlock(block_type=BlockTypes.CHECKPOINT, transaction={'balance': 0}, previous=prev)
        result, errors = block.validate_transaction(db)
        self.assertEqual(result, ValidationResult.partial_previous)

class TestEuroTokenBlockListener(unittest.TestCase):
    def test_init(self):
        l = EuroTokenBlockListener("peer", "community")
        l.should_sign("b")
        l.received_block("b")
