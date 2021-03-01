from pyipv8.ipv8.attestation.trustchain.block import ValidationResult, GENESIS_SEQ
from pyipv8.ipv8.peer                         import Peer

from blockchain.ipv8.trustchain.blocks.base        import EuroTokenBlock, EuroTokenBlockListener
from blockchain.ipv8.trustchain.blocks.block_types import BlockTypes
from blockchain.ipv8.trustchain.db_helper          import get_verified_balance_for_block, isAgreement

import logging

class EuroTokenCheckpointBlock(EuroTokenBlock):
    "For now validation is the same as EuroTokenBlock"

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        return super(EuroTokenCheckpointBlock, self).__init__(*args, **kwargs)

    async def crawl_blocks_before(self, block, peer):
        return await self.community.send_crawl_request(peer, block.public_key,
                max(GENESIS_SEQ, (block.sequence_number - self.community.settings.validation_range)),
                max(GENESIS_SEQ, block.sequence_number - 1))

    def get_block_before_or_crawl(self, block, persistence, peer):
        self.logger.warning(f"crawling for block before")
        blockBefore = persistence.get_block_with_hash(block.previous_hash)
        if not blockBefore:
            self.crawl_blocks_before(block, peer) or None #attempt crawl
            blockBefore = persistence.get_block_with_hash(block.previous_hash)
        return blockBefore

    def ensure_money_sender_blocks(self, block, persistence, peer):
        if block == None: #end of chain or missing block because of connection issues
            return
        self.logger.warning(f"ensure peer {block.sequence_number} ")
        if block.type == BlockTypes.CHECKPOINT:
            linked = persistence.get_linked(block)
            if linked is not None and linked.public_key == persistence.my_pk:
                self.logger.warning("Found full checkpoint")
                return True #done
            else:
                self.logger.warning("Found half checkpoint")
                blockBefore = self.get_block_before_or_crawl(block, persistence, peer)
                return self.ensure_money_sender_blocks(blockBefore, persistence, peer) # recurse
        else:
            self.logger.warning("Found normal block")
            blockBefore = self.get_block_before_or_crawl(block, persistence, peer)
            return self.ensure_money_sender_blocks(blockBefore, persistence, peer) # recurse

    def ensure_receive_money_linked_blocks_available(self, block, persistence, peer):
        if block is None:
            self.logger.warning(f"Found genesis")
            return ValidationResult.valid, [] #genesis
        self.logger.warning(f"ensure {block.sequence_number}")
        blockBefore = persistence.get_block_with_hash(block.previous_hash) # must be available
        if not blockBefore and block.sequence_number != GENESIS_SEQ:
            return ValidationResult.partial_previous, []
        if block.type == BlockTypes.CHECKPOINT:
            linked = persistence.get_linked(block)
            if linked is not None and linked.public_key == persistence.my_pk:
                self.logger.warning("Found full checkpoint") #dont need more info
                return ValidationResult.valid, []
            else:
                self.logger.warning("Found half checkpoint")
                return self.ensure_receive_money_linked_blocks_available(blockBefore, persistence, peer) # recurse
        elif block.type == BlockTypes.TRANSFER and isAgreement(block):
            linked = persistence.get_linked(block)
            self.logger.warning("Found transaction")
            self.ensure_money_sender_blocks(linked, persistence, peer)
            return self.ensure_receive_money_linked_blocks_available(blockBefore, persistence, peer) # recurse
        else:
            return self.ensure_receive_money_linked_blocks_available(blockBefore, persistence, peer) # recurse

    def validate_receive_money_linked_blocks_available(self, block, persistence, rollbacks=[]):
        if block == None: # only when at start of chain
            return ValidationResult.valid, []
        self.logger.warning(f"validate {block.sequence_number}")
        blockBefore = persistence.get_block_with_hash(block.previous_hash) # always available
        if block.type == BlockTypes.CHECKPOINT:
            linked = persistence.get_linked(block)
            if linked is not None and linked.public_key == persistence.my_pk:
                self.logger.warning("Found full checkpoint")
                return ValidationResult.valid, []
            else:
                self.logger.warning("Found half checkpoint")
                return self.validate_receive_money_linked_blocks_available(blockBefore, persistence) # recurse
        elif block.type == BlockTypes.TRANSFER and isAgreement(block):
            linked = persistence.get_linked(block)
            senderBalance = get_verified_balance_for_block(block, persistence)
            if senderBalance is None:
                if persistence.did_double_spend(block.public_key):
                    #TODO: Neatly ask user to Roll back the block
                    return ValidationResult.invalid, ["Double spend", block]
                return ValidationResult.invalid, [f"Sender for seq: {block.sequence_number} has missing blocks"]
            if senderBalance < 0:
                return ValidationResult.invalid, [f"Sender for seq: {block.sequence_number} has insufficient balance"]
            return self.validate_receive_money_linked_blocks_available(blockBefore, persistence) # recurse
        else:
            return self.validate_receive_money_linked_blocks_available(blockBefore, persistence) # recurse

    def validate_transaction(self, persistence):
        print("VALIDATE CHECKPOINT")
        result, errors =  super(EuroTokenCheckpointBlock, self).validate_transaction(persistence)

        if result != ValidationResult.valid: #make sure main chain is present
            return result, errors

        if self.link_public_key == persistence.my_pk and not persistence.get_linked(self): #for me, and not signed
            peer = Peer(self.public_key)
            result, errors = self.ensure_receive_money_linked_blocks_available(self, persistence, peer)

            if result != ValidationResult.valid or ValidationResult.partial_next: #make sure to crawl for partial_previous
                return result, errors

        return ValidationResult.valid, []


class EuroTokenCheckpointBlockListener(EuroTokenBlockListener):
    BLOCK_CLASS = EuroTokenCheckpointBlock

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        return super(EuroTokenCheckpointBlockListener, self).__init__(*args, **kwargs)

    def received_block(self, block):
        pass

    def should_sign(self, block):
        return True
