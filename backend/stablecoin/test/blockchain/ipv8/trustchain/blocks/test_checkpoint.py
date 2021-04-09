from test.blockchain.ipv8.trustchain.blocks.util import TestBlock, MockDatabase, TestWallet, getWalletBlockWithBalance

from pyipv8.ipv8.attestation.trustchain.block import EMPTY_SIG, GENESIS_HASH, GENESIS_SEQ, TrustChainBlock, ValidationResult, BlockRange

from blockchain.ipv8.trustchain.blocks.checkpoint  import EuroTokenCheckpointBlock
from blockchain.ipv8.trustchain.blocks.block_types import BlockTypes

import unittest

from binascii import hexlify

class TestEuroTokenCheckpoint(unittest.TestCase):

    def test_init(self):
        TestBlock(block_type=BlockTypes.CHECKPOINT)

    def test_checkpoint_transaction(self):
        """
        Test validating a block that points towards a previous block
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
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 0},
                previous=A1,
                links=G
                )
        db.add_block(A2)
        result, errors = A2.validate_transaction(db)
        self.assertEqual(result, ValidationResult.valid)
        self.assertEqual(errors, [])

    def test_checkpoint_missing_previous(self):
        """
        Test validating a block that points towards a previous block
        """
        db = MockDatabase()

        G = db.owner

        A1 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 0},
                links=G
                )
        # result, errors = A1.validate_transaction(db)
        # self.assertEqual(result, ValidationResult.valid)
        # self.assertEqual(errors, [])
        # db.add_block(A1)

        A2 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 0},
                previous=A1,
                links=G
                )
        result, errors = A2.validate_transaction(db)
        self.assertEqual(result, ValidationResult.missing)
        self.assertEqual(errors, [BlockRange(A1.public_key, A1.sequence_number, A1.sequence_number)])

    def test_checkpoint_missing_2_ago(self):
        """
        Test validating a block that points towards a previous block
        """
        db = MockDatabase()

        A1 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 0},
                )
        result, errors = A1.validate_transaction(db)
        self.assertEqual(result, ValidationResult.valid)
        self.assertEqual(errors, [])
        # db.add_block(A1)

        A2 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 0},
                previous=A1)
        result, errors = A2.validate_transaction(db)
        self.assertEqual(result, ValidationResult.valid)
        db.add_block(A2)

        A3 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 0},
                previous=A2)
        result, errors = A3.validate_transaction(db)
        self.assertEqual(result, ValidationResult.valid)

    def test_last_full_checkpoint_2_ago(self):
        """
        Test ending validation at a full checkpoint
        """
        db = MockDatabase()

        G = db.owner

        A1 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 0},
                links=G
                )
        # result, errors = A1.validate_transaction(db)
        # self.assertEqual(result, ValidationResult.valid)
        # self.assertEqual(errors, [])
        # db.add_block(A1) # would generate missing, unless G1 exists

        A2 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 0},
                previous=A1,
                links=G
                )
        # result, errors = A2.validate_transaction(db)
        db.add_block(A2)
        G1 = TestBlock(
                key=G,
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 0},
                linked=A2)
        # result, errors = G1.validate_transaction(db)
        # self.assertEqual(result, ValidationResult.valid)
        # self.assertEqual(errors, [])
        db.add_block(G1)

        A3 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 0},
                previous=A2,
                links=G)
        result, errors = A3.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)

    def test_recurse_into_send_with_crawl(self):
        """
        Test G verifying a transaction A got from B

        Bob(B) sends money to Alice(A)
        We ensure that
            - verification of Alice's received block fails when bob checkpoint is missing
            - we(G) crawl for alice's block
            - succeed when the crawl returns the missing block
        """

        db = MockDatabase()

        A = TestWallet()
        B = TestWallet()
        G = db.owner

        # B gets the money
        G1 = TestBlock(
                key = G,
                block_type=BlockTypes.CREATION,
                transaction={'amount': 10},
                links=B
                )
        # self.assertEqual(G1.validate_transaction(db), (ValidationResult.valid, []))
        # db.add_block(G1)

        B1 = TestBlock(
                block_type=BlockTypes.CREATION,
                transaction={'amount': 10},
                linked=G1
                )
        # self.assertEqual(B1.validate_transaction(db), (ValidationResult.valid, []))
        # db.add_block(B1)
        B2 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 10},
                previous=B1,
                links=G
                )
        # self.assertEqual(B2.validate_transaction(db), (ValidationResult.valid, []))
        # db.add_block(B2)
        G2 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 10},
                previous=G1,
                linked=B2
                )
        # self.assertEqual(G2.validate_transaction(db), (ValidationResult.valid, []))
        # db.add_block(G2)

        # B now has a balance of 10
        # self.assertEqual(B2.get_verified_balance(db), 10)

        # B does a useless checkpoint
        B3 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 10},
                previous = B2,
                links = G
                )
        # db.add_block(B3)

        # B sends to A
        B4 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'amount': 5, 'balance': 5},
                previous = B3,
                links = A
                )
        # self.assertEqual(B4.validate_transaction(db), (ValidationResult.valid, []))
        db.add_block(B4)

        A1 = TestBlock(
                key = A,
                block_type=BlockTypes.TRANSFER,
                transaction={'amount': 5, 'balance': 5},
                linked = B4
                )
        # self.assertEqual(A1.validate_transaction(db), (ValidationResult.valid, []))
        db.add_block(A1)

        # A verifies the balance
        A2 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 5},
                previous=A1,
                links=G
                )

        # Must be MISSING
        result, errors = A2.validate_transaction(db)
        self.assertEqual(result, ValidationResult.missing)
        self.assertEqual(errors, [BlockRange(B3.public_key, B3.sequence_number, B3.sequence_number)])
        db.add_block(B3) #add after crawl (half checkpoint)

        result, errors = A2.validate_transaction(db)
        self.assertEqual(result, ValidationResult.missing)
        self.assertEqual(errors, [BlockRange(B2.public_key, B2.sequence_number, B2.sequence_number)])
        db.add_block(B2) #add after crawl
        db.add_block(G2) #add after crawl

        # We validate the transaction
        result, errors = A2.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)

    def test_fake_creation(self):
        """
        Test that a creation without its linked is rejected
        """
        db = MockDatabase()

        G = db.owner

        G1 = TestBlock(
                key = G,
                block_type=BlockTypes.CREATION,
                transaction={'amount': 10},
                )
        A1 = TestBlock(
                block_type=BlockTypes.CREATION,
                transaction={'amount': 10},
                linked=G1
                )
        # A1.link_pk = G1.public_key
        # db.add_block(G1) PROPOSAL DOENST EXIST
        result, errors = A1.validate_transaction(db)
        self.assertEqual(result, ValidationResult.valid)
        db.add_block(A1)

        A2 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 10},
                previous=A1,
                links=G
                )

        result, errors = A2.validate_transaction(db)
        self.assertIsInstance(errors[0], EuroTokenCheckpointBlock.InvalidSend)
        self.assertEqual(result, ValidationResult.invalid)

