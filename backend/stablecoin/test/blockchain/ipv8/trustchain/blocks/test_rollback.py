from test.blockchain.ipv8.trustchain.blocks.util import TestBlock, MockDatabase, TestWallet, getWalletBlockWithBalance

from pyipv8.ipv8.attestation.trustchain.block import EMPTY_SIG, GENESIS_HASH, GENESIS_SEQ, TrustChainBlock, ValidationResult

from blockchain.ipv8.trustchain.blocks.base        import EuroTokenBlock
from blockchain.ipv8.trustchain.blocks.rollback    import EuroTokenRollBackBlock
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
        # db.add_block(B1) #TODO: B1 should really exist or be crawled for (isnt right now)
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
        # db.add_block(B1) #TODO: B1 should really exist or be crawled for (isnt right now)
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
        # db.add_block(B1) #TODO: B1 should really exist or be crawled for (isnt right now)
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
        # db.add_block(B1, True) #TODO: B1 should really exist or be crawled for (isnt right now)
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
        self.assertEqual(result, ValidationResult.valid)
        # self.assertEqual(errors, [EuroTokenRollBackBlock.BlockRange(A1.public_key, A1.sequence_number, A1.sequence_number)])

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
        # db.add_block(B1)
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
        self.assertIsInstance(errors[0], EuroTokenRollBackBlock.InvalidRollback)

    def test_fake_creation_rollback(self):
        """
        Test that a creation without its linked is rejected
        """
        db = MockDatabase()

        G = db.owner
        A = TestWallet()

        G1 = TestBlock(
                key = G,
                block_type=BlockTypes.CREATION,
                transaction={'amount': 10},
                )
        A1 = TestBlock(
                key=A,
                block_type=BlockTypes.CREATION,
                transaction={'amount': 10},
                linked=G1
                )
        # A1.link_pk = G1.public_key
        # db.add_block(G1) SEND DOENST EXIST
        db.add_block(A1)

        result, errors = A1.validate_transaction(db)
        self.assertEqual(result, ValidationResult.valid)

        A2 = TestBlock(
                block_type=BlockTypes.ROLLBACK,
                transaction={'balance': 0, 'amount': 10, 'transaction_hash': hexlify(A1.hash)},
                previous=A1,
                links=A
                )
        result, errors = A2.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)
        db.add_block(A2)

        A3 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 0},
                previous=A2,
                links=G
                )

        result, errors = A3.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)

    def test_invalid_transaction_and_rollback(self):
        db = MockDatabase()

        G = db.owner
        A = TestWallet()
        B = TestWallet()

        # B receives money and does not verify
        X2 = getWalletBlockWithBalance(10, db)
        X3 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'amount': 5, 'balance': 5},
                links = B,
                previous=X2
                )
        result, errors = X3.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)
        db.add_block(X3)

        B1 = TestBlock(
                key = B,
                block_type=BlockTypes.TRANSFER,
                transaction={'amount': 5, 'balance': 5},
                linked = X3
                )
        result, errors = B1.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)
        # db.add_block(B1) #we dont have B1

        # B sends the money to A and A accepts (A shouldn't have)

        B2 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'amount': 5, 'balance': 0},
                previous=B1,
                links=A
                )

        result, errors = B2.validate_transaction(db)
        self.assertEqual(result, ValidationResult.missing)
        self.assertEqual(errors, [EuroTokenBlock.BlockRange(B1.public_key, B1.sequence_number, B1.sequence_number)])
        db.add_block(B2)

        A1 = TestBlock(
                key = A,
                block_type=BlockTypes.TRANSFER,
                transaction={'amount': 5, 'balance': 0},
                linked = B2
                )
        result, errors = A1.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)
        db.add_block(A1)

        # A tries to verify and fails

        A2 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 5},
                previous=A1,
                links=G
                )
        result, errors = A2.validate_transaction(db)
        self.assertEqual(result, ValidationResult.missing)
        self.assertEqual(errors, [EuroTokenBlock.BlockRange(B1.public_key, B1.sequence_number, B1.sequence_number)])
        db.add_block(A2)

        # A adds a rollback block
        A3 = TestBlock(
                block_type=BlockTypes.ROLLBACK,
                transaction={'balance': 0, 'amount': 5, 'transaction_hash': hexlify(A1.hash)},
                previous=A2,
                links=A
                )
        result, errors = A3.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)
        db.add_block(A3)

        # A tries to verify and succeeds

        A4 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 0},
                previous=A3,
                links=G
                )
        result, errors = A4.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)
        self.assertEqual(A4.should_sign(db), True)
        db.add_block(A4)

    def test_invalid_transaction_and_incorrect_rollback(self):
        db = MockDatabase()

        G = db.owner
        A = TestWallet()
        B = TestWallet()

        # B receives money and does not verify
        X2 = getWalletBlockWithBalance(10, db)
        X3 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'amount': 5, 'balance': 5},
                links = B,
                previous=X2
                )
        result, errors = X3.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)
        db.add_block(X3)

        B1 = TestBlock(
                key = B,
                block_type=BlockTypes.TRANSFER,
                transaction={'amount': 5, 'balance': 5},
                linked = X3
                )
        result, errors = B1.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)
        # db.add_block(B1) we dont have B1

        # B sends the money to A and A accepts (A shouldn't have)

        B2 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'amount': 5, 'balance': 0},
                previous=B1,
                links=A
                )

        result, errors = B2.validate_transaction(db)
        self.assertEqual(result, ValidationResult.missing) #Note send is invalid
        self.assertEqual(errors, [EuroTokenBlock.BlockRange(B1.public_key, B1.sequence_number, B1.sequence_number)])
        db.add_block(B2) #added without crawl, because provided by A

        A1 = TestBlock(
                key = A,
                block_type=BlockTypes.TRANSFER,
                transaction={'amount': 5, 'balance': 0},
                linked = B2
                )
        result, errors = A1.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)
        db.add_block(A1)

        # A tries to verify and fails

        A2 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 5},
                previous=A1,
                links=G
                )
        result, errors = A2.validate_transaction(db)
        self.assertEqual(result, ValidationResult.missing)
        self.assertEqual(errors, [EuroTokenBlock.BlockRange(B1.public_key, B1.sequence_number, B1.sequence_number)])
        self.assertEqual(A2.should_sign(db), False)
        db.add_block(A2)

        # A adds an incorrect rollback block
        A3 = TestBlock(
                block_type=BlockTypes.ROLLBACK,
                transaction={'balance': 1, 'amount': 4, 'transaction_hash': hexlify(A1.hash)},
                previous=A2,
                links=A
                )
        result, errors = A3.validate_transaction(db)
        self.assertEqual(result, ValidationResult.invalid)
        self.assertIsInstance(errors[0], EuroTokenBlock.InvalidRollback)
        db.add_block(A3, True) # force in, this could happen if the linked block was missing at the time of arrival

        # A tries to verify and fails

        A4 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 1},
                previous=A3,
                links=G
                )
        result, errors = A4.validate_transaction(db)
        self.assertEqual(result, ValidationResult.invalid)
        self.assertIsInstance(errors[0], EuroTokenBlock.InvalidRollback)
        self.assertEqual(A4.should_sign(db), False)
