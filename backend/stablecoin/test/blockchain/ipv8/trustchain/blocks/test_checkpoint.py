from test.blockchain.ipv8.trustchain.blocks.util import TestBlock, MockDatabase, TestWallet, getWalletBlockWithBalance

from pyipv8.ipv8.attestation.trustchain.block import EMPTY_SIG, GENESIS_HASH, GENESIS_SEQ, TrustChainBlock, ValidationResult

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
        self.assertEqual(result, ValidationResult.partial_previous)

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
        self.assertEqual(result, ValidationResult.partial_previous)
        db.add_block(A2)

        A3 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 0},
                previous=A2)
        result, errors = A3.validate_transaction(db)
        self.assertEqual(result, ValidationResult.partial_previous)

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
        # db.add_block(A1) # would generate partial_previous, unless G1 exists

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
        self.assertEqual(result, ValidationResult.valid)
        self.assertIsInstance(errors[0], EuroTokenCheckpointBlock.MissingSenderBlocks)

        to_crawl = [
                # [G1, B1],
                [G2, B2],
                [B3],
                ]

        def crawl_effect(*args, **kwargs):
            blocks = to_crawl.pop(-1)
            for block in blocks:
                db.add_block(block)

        A2.community.send_crawl_request.side_effect = crawl_effect

        # We validate the transaction
        result, errors = A2.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)

        # assert all blocks in "to_crawl" have been requested
        self.assertEqual(len(to_crawl), 0)

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
        # db.add_block(G1) SEND DOENST EXIST
        db.add_block(A1)

        result, errors = A1.validate_transaction(db)
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)

        A2 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 10},
                previous=A1,
                links=G
                )

        result, errors = A2.validate_transaction(db)
        self.assertIsInstance(errors[0], EuroTokenCheckpointBlock.MissingSenderBlocks)
        self.assertEqual(result, ValidationResult.valid)

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
        self.assertEqual(errors, [])
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
        # db.add_block(B1) we dont have B1

        # B sends the money to A and A accepts (A shouldn't have)

        B2 = TestBlock(
                block_type=BlockTypes.TRANSFER,
                transaction={'amount': 5, 'balance': 0},
                previous=B1,
                links=A
                )

        result, errors = B2.validate_transaction(db)
        self.assertEqual(result, ValidationResult.partial_previous) #Note invalid
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
        self.assertIsInstance(errors[0], EuroTokenCheckpointBlock.MissingSenderBlocks)
        self.assertEqual(result, ValidationResult.valid)
        self.assertEqual(A2.should_sign(db), False)
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
        self.assertEqual(result, ValidationResult.partial_previous) #Note invalid
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
        self.assertIsInstance(errors[0], EuroTokenCheckpointBlock.MissingSenderBlocks)
        self.assertEqual(result, ValidationResult.valid)
        self.assertEqual(A2.should_sign(db), False)
        db.add_block(A2)

        # A adds a rollback block
        A3 = TestBlock(
                block_type=BlockTypes.ROLLBACK,
                transaction={'balance': 1, 'amount': 4, 'transaction_hash': hexlify(A1.hash)},
                previous=A2,
                links=A
                )
        result, errors = A3.validate_transaction(db)
        # self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.invalid)
        db.add_block(A3, force=True)

        # A tries to verify and succeeds

        A4 = TestBlock(
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': 1},
                previous=A3,
                links=G
                )
        result, errors = A4.validate_transaction(db)
        self.assertIsInstance(errors[0], EuroTokenCheckpointBlock.MissingSenderBlocks)
        self.assertEqual(result, ValidationResult.valid)
        self.assertEqual(A4.should_sign(db), False)
        db.add_block(A4)
