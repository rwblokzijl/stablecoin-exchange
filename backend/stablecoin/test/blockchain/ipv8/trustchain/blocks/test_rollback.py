from test.blockchain.ipv8.trustchain.blocks.util import TestBlock, MockDatabase

from pyipv8.ipv8.attestation.trustchain.block import EMPTY_SIG, GENESIS_HASH, GENESIS_SEQ, TrustChainBlock, ValidationResult

from blockchain.ipv8.trustchain.blocks.rollback  import EuroTokenRollBackBlock
from blockchain.ipv8.trustchain.blocks.block_types import BlockTypes

from binascii import hexlify

import unittest

class TestEuroTokenRollBack(unittest.TestCase):

    def test_init(self):
        TestBlock(block_type=BlockTypes.ROLLBACK)

    def test_valid_rollback(self):
        """
        Test Valid rollback after receiving
        """
        db = MockDatabase()

        # Receive money
        B1 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'balance': 0, 'amount': 10},
                )
        A1 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'balance': 0, 'amount': 10},
                linked=B1
                )
        # db.add_block(G1) #TODO: G1 should really exist or be crawled for (isnt right now)
        db.add_block(A1)

        result, errors = A1.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)

        # roll back the transaction
        A2 = TestBlock(
                block_type=BlockTypes.ROLLBACK,
                transaction={'balance': 0, 'amount': 10, 'transaction_hash': hexlify(A1.hash)},
                previous = A1)

        result, errors = A2.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)

    def test_missing_amount(self):
        """
        Test Valid send after receiving
        """
        db = MockDatabase()

        # Receive money
        B1 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'balance': 0, 'amount': 10},
                )
        A1 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'balance': 0, 'amount': 10},
                linked=B1
                )
        # db.add_block(G1) #TODO: G1 should really exist or be crawled for (isnt right now)
        db.add_block(A1)

        result, errors = A1.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)

        # roll back the transaction
        A2 = TestBlock(
                block_type=BlockTypes.ROLLBACK,
                transaction={'balance': 0, 'transaction_hash': hexlify(A1.hash)},
                previous = A1)

        result, errors = A2.validate_transaction(db)
        self.assertEqual(result, ValidationResult.invalid)
        self.assertIsInstance(errors[0], EuroTokenRollBackBlock.MissingAmount)

    def test_missing_hash(self):
        """
        Test Valid rollback after receiving
        """
        db = MockDatabase()

        # Receive money
        B1 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'balance': 0, 'amount': 10},
                )
        A1 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'balance': 0, 'amount': 10},
                linked=B1
                )
        # db.add_block(G1) #TODO: G1 should really exist or be crawled for (isnt right now)
        db.add_block(A1)

        result, errors = A1.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)

        # roll back the transaction
        A2 = TestBlock(
                block_type=BlockTypes.ROLLBACK,
                transaction={'balance': 0, 'amount': 10},
                previous = A1)

        result, errors = A2.validate_transaction(db)
        self.assertEqual(result, ValidationResult.invalid)
        self.assertIsInstance(errors[0], EuroTokenRollBackBlock.MissingTransactionHash)

    def test_missing_previous(self):
        """
        Test Valid rollback after receiving
        """
        db = MockDatabase()

        # Receive money
        B1 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'balance': 0, 'amount': 10},
                )
        A1 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'balance': 0, 'amount': 10},
                linked=B1
                )
        # db.add_block(G1) #TODO: G1 should really exist or be crawled for (isnt right now)
        # db.add_block(A1)

        result, errors = A1.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)

        # roll back the transaction
        A2 = TestBlock(
                block_type=BlockTypes.ROLLBACK,
                transaction={'balance': 0, 'amount': 10, 'transaction_hash': hexlify(A1.hash)},
                previous = A1)

        result, errors = A2.validate_transaction(db)
        self.assertEqual(result, ValidationResult.partial_previous)

    def test_invalid_amount(self):
        """
        Test amount doesnt match rolled back transaction
        """
        db = MockDatabase()

        # Receive money
        B1 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'balance': 0, 'amount': 10},
                )
        A1 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'balance': 0, 'amount': 10},
                linked=B1
                )
        # db.add_block(G1) #TODO: G1 should really exist or be crawled for (isnt right now)
        db.add_block(A1)

        result, errors = A1.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)

        # roll back the transaction
        A2 = TestBlock(
                block_type=BlockTypes.ROLLBACK,
                transaction={'balance': 5, 'amount': 5, 'transaction_hash': hexlify(A1.hash)},
                previous = A1)

        result, errors = A2.validate_transaction(db)
        self.assertEqual(result, ValidationResult.invalid)
        self.assertIsInstance(errors[0], EuroTokenRollBackBlock.InvalidTransaction)

