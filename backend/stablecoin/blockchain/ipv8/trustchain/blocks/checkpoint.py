from pyipv8.ipv8.attestation.trustchain.block import ValidationResult, GENESIS_SEQ
from pyipv8.ipv8.peer                         import Peer

from blockchain.ipv8.trustchain.blocks.base        import EuroTokenBlock, EuroTokenBlockListener
from blockchain.ipv8.trustchain.blocks.block_types import BlockTypes

import logging

class EuroTokenCheckpointBlock(EuroTokenBlock):
    "For now validation is the same as EuroTokenBlock"

    async def crawl_blocks_before(self, block, peer):
        return await self.community.send_crawl_request(peer, block.public_key,
                max(GENESIS_SEQ, (block.sequence_number - self.community.settings.validation_range)),
                max(GENESIS_SEQ, block.sequence_number - 1))

    def get_block_before_or_crawl(self, block, persistence, peer):
        self._logger.debug(f"crawling for block before")
        blockBefore = persistence.get_block_with_hash(block.previous_hash)
        if not blockBefore:
            self.crawl_blocks_before(block, peer) or None #attempt crawl
            blockBefore = persistence.get_block_with_hash(block.previous_hash)
        return blockBefore

    def ensure_money_sender_blocks(self, block, persistence, peer):
        if block == None: #end of chain or missing block because of connection issues
            return
        self._logger.debug(f"ensure peer {block.sequence_number} ")
        if block.type == BlockTypes.CHECKPOINT:
            linked = persistence.get_linked(block)
            if linked is not None and self.is_valid_gateway():
                self._logger.debug("Found full checkpoint")
                return True #done
            else:
                self._logger.debug("Found half checkpoint")
                blockBefore = self.get_block_before_or_crawl(block, persistence, peer)
                return self.ensure_money_sender_blocks(blockBefore, persistence, peer) # recurse
        else:
            self._logger.debug("Found normal block")
            blockBefore = self.get_block_before_or_crawl(block, persistence, peer)
            return self.ensure_money_sender_blocks(blockBefore, persistence, peer) # recurse

    def ensure_receive_money_linked_blocks_available(self, block, persistence, peer):
        if block is None:
            self._logger.debug(f"Found genesis")
            return ValidationResult.valid, [] #genesis
        if block.type == BlockTypes.CHECKPOINT:
            linked = persistence.get_linked(block)
            if linked is not None:
                if not linked.is_valid_gateway():
                    raise self.UnsanctionedGateway("unsanctioned gateway")
                self._logger.debug("Found full checkpoint") #dont need more info
                return ValidationResult.valid, []
            else:
                self._logger.debug("Found half checkpoint")

        blockBefore = block.get_block_before_or_raise(persistence) # must be available

        if block.type == BlockTypes.TRANSFER and block.isAgreement():
            self._logger.debug("Found transaction")
            linked = persistence.get_linked(block)
            self.ensure_money_sender_blocks(linked, persistence, peer)
            return self.ensure_receive_money_linked_blocks_available(blockBefore, persistence, peer) # recurse
        else:
            return self.ensure_receive_money_linked_blocks_available(blockBefore, persistence, peer) # recurse

    def sender_invalid(self, block, rollbacks):
        if block.hash in rollbacks:
            return
        else:
            #TODO: Neatly ask user to Roll back the block
            raise self.InvalidSend(str(block))

    def validate_receive_money_linked_blocks(self, block, persistence, rollbacks=None):
        if rollbacks is None:
            rollbacks = {}
        if block == None: # only when at start of chain
            return ValidationResult.valid, []
        self._logger.debug(f"validate {block.sequence_number}")
        blockBefore = persistence.get_block_with_hash(block.previous_hash) # always available
        if block.type == BlockTypes.CHECKPOINT:
            linked = persistence.get_linked(block)
            if linked is not None and linked.is_valid_gateway():
                self._logger.debug("Found full checkpoint")
                return ValidationResult.valid, []
            else:
                self._logger.debug("Found half checkpoint")
                return self.validate_receive_money_linked_blocks(blockBefore, persistence, rollbacks) # recurse
        elif block.type == BlockTypes.ROLLBACK and block.isProposal():
            rollbacks[block.transaction["transaction_hash"]] = block
        elif block.type == BlockTypes.TRANSFER and block.isAgreement():
            linked = persistence.get_linked(block)
            senderBalance = linked.get_verified_balance(persistence)
            if senderBalance is None:
                if persistence.did_double_spend(block.public_key):
                    sender_invalid(block, rollbacks)
                else:
                    raise MissingBlocks(f"Sender blocks missing while verifying {block}")
            if senderBalance < 0:
                sender_invalid(block)
            return self.validate_receive_money_linked_blocks(blockBefore, persistence, rollbacks) # recurse
        else:
            return self.validate_receive_money_linked_blocks(blockBefore, persistence, rollbacks) # recurse

    def validate_eurotoken_transaction(self, persistence):
        super(EuroTokenCheckpointBlock, self).validate_eurotoken_transaction(persistence)

        if (self.isProposal() and
                self.link_public_key == persistence.my_pk and # for me
                not persistence.get_linked(self)): #not signed
            peer = Peer(self.public_key)
            result, errors = self.ensure_receive_money_linked_blocks_available(self, persistence, peer)

            if result != ValidationResult.valid: #make sure to crawl for partial_previous
                return result, errors

            result, errors = self.validate_receive_money_linked_blocks(self, persistence)

            if result != ValidationResult.valid: #make sure to crawl for partial_previous
                return result, errors

        return ValidationResult.valid, []

class EuroTokenCheckpointBlockListener(EuroTokenBlockListener):
    BLOCK_CLASS = EuroTokenCheckpointBlock

    def __init__(self, *args, **kwargs):
        self._logger = logging.getLogger(self.__class__.__name__)
        return super(EuroTokenCheckpointBlockListener, self).__init__(*args, **kwargs)
