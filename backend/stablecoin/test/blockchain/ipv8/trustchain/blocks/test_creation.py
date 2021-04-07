from test.blockchain.ipv8.trustchain.blocks.util import TestBlock, MockDatabase

from pyipv8.ipv8.attestation.trustchain.block import EMPTY_SIG, GENESIS_HASH, GENESIS_SEQ, TrustChainBlock, ValidationResult

from blockchain.ipv8.trustchain.blocks.creation  import EuroTokenCreationBlock
from blockchain.ipv8.trustchain.blocks.block_types import BlockTypes

import unittest

class TestEuroTokenCreation(unittest.TestCase):

    def test_init(self):
        TestBlock(block_type=BlockTypes.CREATION)

    def test_missing_amount(self):
        db = MockDatabase()

        block = TestBlock(block_type=BlockTypes.CREATION, transaction={})

        result, errors = block.validate_transaction(db)
        self.assertEqual(result, ValidationResult.invalid)
        self.assertIsInstance(errors[0], EuroTokenCreationBlock.MissingAmount)

    def test_valid_creation(self):
        """
        Test Valid send after receiving
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
        db.add_block(G1)
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
        self.assertEqual(errors, [])
        self.assertEqual(result, ValidationResult.valid)

