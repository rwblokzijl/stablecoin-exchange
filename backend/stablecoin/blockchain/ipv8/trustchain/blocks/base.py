from pyipv8.ipv8.attestation.trustchain.block    import GENESIS_HASH, UNKNOWN_SEQ, GENESIS_SEQ
from pyipv8.ipv8.attestation.trustchain.block    import TrustChainBlock, ValidationResult
from pyipv8.ipv8.attestation.trustchain.listener import BlockListener
from blockchain.ipv8.trustchain.blocks.block_types import BlockTypes

from binascii import hexlify, unhexlify
from enum     import Enum

import logging
import traceback

from dataclasses import dataclass

class EuroTokenBlock(TrustChainBlock):

    def isProposal(self):
        if self.link_sequence_number == UNKNOWN_SEQ:
            return True
        else:
            return False

    def isAgreement(self):
        return not self.isProposal()

    def get_linked_or_crawl(self, persistence):
        linked = persistence.get_linked(self)
        if not linked:
            raise self.MissingBlocks([ # Crawl for self to get linked
                self.BlockRange( self.public_key, self.sequence_number, self.sequence_number
                    )])
        return linked

    def get_verified_balance(self, persistence):
        if self.sequence_number == GENESIS_SEQ: # base
            return self.get_valid_balance_change()

        if self.type == BlockTypes.CHECKPOINT and self.isProposal(): #base 2
            linked = persistence.get_linked(self)
            if linked is not None and linked.is_valid_gateway(): #Found full checkpoint
                return self.transaction["balance"]
            else: #Found half checkpoint ignore and recurse
                blockBefore = self.get_previous_block_or_raise(persistence)
                return blockBefore.get_verified_balance(persistence) # recurse
        else:
            blockBefore = self.get_previous_block_or_raise(persistence)
            return blockBefore.get_verified_balance(persistence) + self.get_valid_balance_change()

    def get_valid_balance_change(self):
        if  self.isProposal():# block is sending money
            return -self.transaction.get("amount", 0)
        else: # block is receiving money, dont add to validated total
            return 0

    def get_balance_change(self):
        if  self.isProposal():# block is sending money
            return -self.transaction.get("amount", 0)
        else: # block is receiving money
            return self.transaction.get("amount", 0)

    def get_block_before(self, block, persistence):
        return persistence.get_block_with_hash(block.previous_hash)

    def get_previous_block_or_raise(self, persistence):
        return self.get_block_before_or_raise(self, persistence)

    def get_block_before_or_raise(self, block, persistence):
        if block.sequence_number == GENESIS_SEQ: #first block in chain
            # Dont raise, just return None
            return None
        blockBefore = self.get_block_before(block, persistence)
        if not blockBefore:
            raise self.MissingBlocks([
                self.BlockRange(block.public_key, block.sequence_number-1, block.sequence_number-1
                    )])
        if blockBefore.type not in BlockTypes.EUROTOKEN_TYPES: #Go back one more block
            return self.get_block_before_or_raise(blockBefore, persistence)
        return blockBefore

    def get_balance(self, persistence):
        "Gets balance from all previous blocks"
        if self.isProposal(): # block contains balance (base case)
            return self.transaction["balance"]

        if self.sequence_number == GENESIS_SEQ: #first block in chain
            return self.get_balance_change() #use amount received instead

        # get balance of last block and add balance change
        blockBefore = self.get_previous_block_or_raise(persistence)
        return blockBefore.get_balance(persistence) + self.get_balance_change()

    def is_valid_gateway(self):
        return True # For now all gateways are trusted, later this is a very important check

    def assert_transaction_balance(self):
        if "balance" not in self.transaction:
            raise self.MissingBalance('balance missing from transaction')

    def get_unlinked_checkpoint_ranges(self, block, persistence):
        blockBefore = self.get_block_before_or_raise(block, persistence)
        if not blockBefore: #genesis
            return []
        if blockBefore.type == BlockTypes.CHECKPOINT:
            if persistence.get_linked(blockBefore) is not None:
                # Found last valid checkpoint
                return []
            else:
                #Found un-linked checkpoint, we should crawl it to ensure linked blocks, add to range and recurse
                return self.get_unlinked_checkpoint_ranges(blockBefore, persistence) + [self.BlockRange(
                    blockBefore.publicKey, blockBefore.sequence_number, blockBefore.sequence_number)]
        else:
            return self.get_unlinked_checkpoint_ranges(blockBefore, persistence)

    def verify_balance_available_for_block(self, block, persistence):
        verifiedBalance = block.get_verified_balance(persistence)
        if verifiedBalance < 0:
            # the validated balance is not enough, but it could be the case we're missing some
            # checkpoint links
            unconfirmed = self.get_unlinked_checkpoint_ranges(block, persistence)
            if unconfirmed: #There are some checkpoints without linked blocks
                # crawl these missing linked blocks
                raise self.MissingBlocks(unconfirmed)
            else: #last checkpoint is full, spendable balance is invalid
                raise self.InsufficientValidatedBalance(f'block verifiedBalance balance ({block.sequence_number}): {verifiedBalance} is not sufficient')
        return # Valid

    def validate_eurotoken_transaction_proposal(self, persistence):
        self.assert_transaction_balance()
        blockBefore  = self.get_previous_block_or_raise(persistence)
        if blockBefore is None: # genesis
            balanceBefore = 0
        else:
            balanceBefore = blockBefore.get_balance(persistence)
        balanceChange = self.get_balance_change()
        if self.transaction["balance"] < 0:
            raise self.InsufficientBalance(f'block balance ({self.sequence_number}): {self.transaction["balance"]} is negative')
        if self.transaction["balance"] != balanceBefore + balanceChange:
            raise self.InvalidBalance(f'block balance ({self.sequence_number}): {self.transaction["balance"]} does not match calculated balance: {balanceBefore} + {balanceChange} ')
        self.validate

        self.verify_balance_available_for_block(self, persistence)

        return ValidationResult.valid, []

    def validate_eurotoken_transaction_agreement(self, persistence):
        pass

    def validate_eurotoken_transaction(self, persistence):
        if self.isProposal():
            return self.validate_eurotoken_transaction_proposal(persistence)
        else:
            return self.validate_eurotoken_transaction_agreement(persistence)

    def validate_transaction(self, persistence):
        try:
            self.validate_eurotoken_transaction(persistence)
            return ValidationResult.valid, []
        # except self.PartialPrevious as e:
        #     return ValidationResult.partial_previous, [e]
        except self.Invalid as e:
            return ValidationResult.invalid, [e]
        except self.MissingBlocks as e:
            return ValidationResult.missing, e.block_range

    @dataclass
    class BlockRange:
        public_key: bytes
        first: int
        last: int

        def __repr__(self):
            return f"{hexlify(self.public_key)}:{self.first}-{self.last}"

        def __str__(self):
            return self.__repr__()

    class ValidationResultException(Exception):
        pass

    class PartialPrevious(ValidationResultException):
        pass

    class MissingBlocks(ValidationResultException):
        def __init__(self, block_range, last_chance=False):
            self.block_range = block_range
            return super().__init__("Missing blocks: " + ", ".join([str(b) for b in block_range]))

    class Invalid(ValidationResultException):
        pass

    class InvalidBalance(Invalid):
        pass

    class InsufficientBalance(Invalid):
        pass

    class InsufficientValidatedBalance(Invalid):
        pass

    class MissingBalance(Invalid):
        pass

    class MissingProposal(Invalid):
        pass

    class ProposalMismatch(Invalid):
        pass

    class InvalidRollback(Invalid):
        pass

    def should_sign(self, persistence):
        try:
            self.validate_eurotoken_transaction(persistence)
            return True
        except Exception as e:
            # print(e)
            # traceback.print_exc()
            # This happens if the block should be persisted, but NOT signed
            return False

    def __str__(self):
        # This makes debugging and logging easier
        trans = self.transaction
        return "Block {0} from ...{1}:{2} links ...{3}:{4} for {5} type {6}".format(
                hexlify(self.hash)[-8:],
                hexlify(self.public_key)[-8:],
                self.sequence_number,
                hexlify(self.link_public_key)[-8:],
                self.link_sequence_number,
                trans,
                self.type)

class EuroTokenBlockListener(BlockListener):
    BLOCK_CLASS = EuroTokenBlock

    def __init__(self, my_peer, community):
        s = super(EuroTokenBlockListener, self).__init__()
        self.my_peer = my_peer
        self.community = community
        self.logger = logging.getLogger(self.__class__.__name__)
        return s

    def received_block(self, block):
        self.logger.info(f"Got block {block}")

    def should_sign(self, block):
        return block.should_sign(self.community.persistence)

