from pyipv8.ipv8.attestation.trustchain.block     import GENESIS_HASH, UNKNOWN_SEQ, GENESIS_SEQ
from pyipv8.ipv8.attestation.trustchain.block     import TrustChainBlock, ValidationResult
from pyipv8.ipv8.attestation.trustchain.listener  import BlockListener

from blockchain.ipv8.trustchain.blocks.block_types import BlockTypes

from binascii import hexlify, unhexlify
from enum import Enum

import logging

class EuroTokenBlock(TrustChainBlock):

    def isProposal(self):
        if self.link_sequence_number == UNKNOWN_SEQ:
            return True
        else:
            return False

    def isAgreement(self):
        return not self.isProposal()

    def get_verified_balance(self, persistence):
        if self.sequence_number == GENESIS_SEQ: # base
            return self.get_valid_balance_change()

        if self.type == BlockTypes.CHECKPOINT and self.isProposal(): #base 2
            linked = persistence.get_linked(self)
            if linked is not None and linked.is_valid_gateway(): #Found full checkpoint
                return self.transaction["balance"]
            else: #Found half checkpoint ignore and recurse
                blockBefore = self.get_block_before_or_raise(persistence)
                return blockBefore.get_verified_balance(persistence) # recurse

        blockBefore = self.get_block_before_or_raise(persistence)
        if self.type in BlockTypes.EUROTOKEN_TYPES:
            # Remove money spent this block from verified balance of block before
            return blockBefore.get_verified_balance(persistence) + self.get_valid_balance_change()
        else: #Not eurotoken
            return blockBefore.get_verified_balance(persistence)

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

    def get_block_before(self, persistence):
        return persistence.get_block_with_hash(self.previous_hash)

    def get_block_before_or_raise(self, persistence):
        if self.sequence_number == GENESIS_SEQ: #first block in chain
            # Dont raise, just return None
            return None
        blockBefore = self.get_block_before(persistence)
        if not blockBefore:
            raise self.PartialPrevious(f"Missing block {hexlify(self.public_key)}:{self.sequence_number-1}")
        return blockBefore

    def get_balance(self, persistence):
        "Gets balance from all previous blocks"
        if self.sequence_number == GENESIS_SEQ: #first block in chain
            return self.get_balance_change()

        if  self.type in [ BlockTypes.TRANSFER, BlockTypes.DESTRUCTION, BlockTypes.CHECKPOINT ] and self.isProposal():
            # block contains balance (base case)
            return self.transaction["balance"]

        blockBefore = self.get_block_before_or_raise(persistence)
        if self.type not in BlockTypes.EUROTOKEN_TYPES:
            return blockBefore.get_balance(persistence)
        if self.type in [BlockTypes.TRANSFER, BlockTypes.CREATION] and self.isAgreement():
            # block is receiving money add it and recurse
            return blockBefore.get_balance(persistence) + self.get_balance_change()
        else:
            #bad type that shouldn't exist, for now just ignore and return for next
            return blockBefore.get_balance(persistence)

    def is_valid_gateway(self):
        return True # For now all gateways are trusted, later this is a very important check

    def validate_eurotoken_transaction(self, persistence):
        return self.validate_balance(persistence)

    def validate_transaction(self, persistence):
        try:
            self.validate_eurotoken_transaction(persistence)
            return ValidationResult.valid, []
        except self.PartialPrevious as e:
            return ValidationResult.partial_previous, [e]

        except self.Invalid as e:
            return ValidationResult.invalid, [e]

    def validate_balance(self, persistence):
        if "balance" not in self.transaction:
            raise self.MissingBalance('balance missing from transaction')
        if self.isProposal():
            blockBefore  = self.get_block_before_or_raise(persistence)
            if blockBefore is None: # genesis
                balanceBefore = 0
            else:
                balanceBefore = blockBefore.get_balance(persistence)
            balanceChange = self.get_balance_change()
            verifiedBalance = self.get_verified_balance(persistence)
            if self.transaction["balance"] < 0:
                raise self.InsufficientBalance(f'block balance ({self.sequence_number}): {self.transaction["balance"]} is negative')
            if self.transaction["balance"] != balanceBefore + balanceChange:
                raise self.InvalidBalance(f'block balance ({self.sequence_number}): {self.transaction["balance"]} does not match calculated balance: {balanceBefore} + {balanceChange} ')
            if verifiedBalance < 0:
                raise self.InsufficientValidatedBalance(f'block verifiedBalance balance ({self.sequence_number}): {verifiedBalance} is not sufficient')

        return ValidationResult.valid, []

    class ValidationResult(Exception):
        pass

    class PartialPrevious(ValidationResult):
        pass

    class Invalid(ValidationResult):
        pass

    class InvalidBalance(Invalid):
        pass

    class InsufficientBalance(Invalid):
        pass

    class InsufficientValidatedBalance(Invalid):
        pass

    class MissingBalance(Invalid):
        pass

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
        return True

