# import asynctest
from pyipv8.ipv8.test.base import TestBase

from pyipv8.ipv8.test.attestation.trustchain.test_block import TestBlock, MockDatabase, TestTrustChainBlock


class TestBalance(TestBase):

    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_validation_level_next_block_no_gap(self):
        """
        Test the validation level for next block without gap.
        """
        result = ValidationResult()
        block = TestBlock()
        block.sequence_number = 2
        next_block = TestBlock()
        next_block.sequence_number = 3
        block.update_validation_level(None, next_block, result)

        self.assertEqual(result.state, ValidationResult.partial_previous)


