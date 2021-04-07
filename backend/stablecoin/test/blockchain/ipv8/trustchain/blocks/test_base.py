from test.blockchain.ipv8.trustchain.blocks.util import TestBlock, MockDatabase, TestWallet, getWalletBlockWithBalance

from blockchain.ipv8.trustchain.community import MyTrustChainCommunity

from pyipv8.ipv8.attestation.trustchain.block import EMPTY_SIG, GENESIS_HASH, GENESIS_SEQ, TrustChainBlock, ValidationResult

from blockchain.ipv8.trustchain.blocks.base        import EuroTokenBlockListener, EuroTokenBlock
from blockchain.ipv8.trustchain.blocks.block_types import BlockTypes

import unittest

from unittest.mock import Mock

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

    def test_missing_validated_balance(self):
        """
        Test validating a genesis block without a balance
        """
        db = MockDatabase()

        G = db.owner
        A = TestWallet()

        G1 = TestBlock(
                key = G,
                block_type=BlockTypes.CREATION,
                transaction={'amount': 10},
                links=A
                )
        result, errors = G1.validate_transaction(db)
        self.assertEqual(result, ValidationResult.valid)
        self.assertEqual(errors, [])
        db.add_block(G1)

        A1 = TestBlock(
                key=A,
                block_type=BlockTypes.CREATION,
                transaction={'amount': 10},
                linked = G1
                )
        result, errors = A1.validate_transaction(db)
        self.assertEqual(result, ValidationResult.valid)
        self.assertEqual(errors, [])
        db.add_block(A1)

        A2 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'balance':5, 'amount': 5},
                previous=A1
                )
        result, errors = A2.validate_transaction(db)
        self.assertEqual(result, ValidationResult.invalid)
        self.assertIsInstance(errors[0], EuroTokenBlock.InsufficientValidatedBalance)

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

    def test_double_validate_skip_non_eurotoken(self):
        """
        Test validating a block that points towards a previous block with a non eurotoken block in between
        """
        db = MockDatabase()

        G = db.owner

        A1 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 0},
                links=G
                )
        result, errors = A1.validate_transaction(db)
        self.assertEqual(result, ValidationResult.valid)
        self.assertEqual(errors, [])
        db.add_block(A1)

        A2 = TestBlock(
                block_type="NonEurotoken",
                transaction={},
                previous=A1
                )
        db.add_block(A2)

        A3 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 0},
                previous=A2,
                links=G
                )
        result, errors = A3.validate_transaction(db)
        self.assertEqual(result, ValidationResult.valid)
        self.assertEqual(errors, [])

    def test_missing_previous(self):
        """
        Test validating a block that points towards a missing block
        """
        db = MockDatabase()

        G = db.owner

        A1 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 0},
                links=G
                )
        result, errors = A1.validate_transaction(db)
        self.assertEqual(result, ValidationResult.valid)
        self.assertEqual(errors, [])
        # db.add_block(A1) MISSING!!!

        A2 = TestBlock(
                block_type="NonEurotoken",
                transaction={},
                previous=A1
                )
        db.add_block(A2)

        A3 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 0},
                previous=A2,
                links=G
                )
        result, errors = A3.validate_transaction(db)
        self.assertEqual(result, ValidationResult.partial_previous)
        self.assertIsInstance(errors[0], EuroTokenBlock.PartialPrevious)

    def test_get_balance_receive_block_with_crawl(self):
        db = MockDatabase()

        A = TestWallet()

        A1 = TestBlock(
                key = A,
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 0})
        result, errors = A1.validate_transaction(db)
        self.assertEqual(result, ValidationResult.valid)
        self.assertEqual(errors, [])
        db.add_block(A1)

        B2 = getWalletBlockWithBalance(10, db)

        B3 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'balance': 5, 'amount': 5},
                previous = B2,
                links=A
                )
        result, errors = B3.validate_transaction(db)
        self.assertEqual(result, ValidationResult.valid)
        self.assertEqual(errors, [])
        db.add_block(B3)

        A2 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'balance': 5, 'amount': 5},
                previous = A1,
                linked=B3
                )
        balance = A2.get_balance(db)
        self.assertEqual(balance, 5)

class TestEuroTokenBlockListener(unittest.TestCase):
    def test_init(self):
        community = Mock()
        community.persistence = MockDatabase()
        l = EuroTokenBlockListener("peer", community)
        l.should_sign(TestBlock(
            block_type=BlockTypes.CHECKPOINT,
            transaction={'balance':0}
            ))
        l.received_block("b")
