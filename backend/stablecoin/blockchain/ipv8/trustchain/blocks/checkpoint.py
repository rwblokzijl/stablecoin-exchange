from pyipv8.ipv8.attestation.trustchain.block import ValidationResult, GENESIS_SEQ, GENESIS_HASH
from pyipv8.ipv8.peer                         import Peer

from blockchain.ipv8.trustchain.blocks.base        import EuroTokenBlock, EuroTokenBlockListener
from blockchain.ipv8.trustchain.blocks.block_types import BlockTypes

import logging

from binascii import hexlify, unhexlify

class EuroTokenCheckpointBlock(EuroTokenBlock):
    "For now validation is the same as EuroTokenBlock"

    async def crawl_blocks_before(self, block, peer):
        return await self.community.send_crawl_request(peer, block.public_key,
                max(GENESIS_SEQ, (block.sequence_number - self.community.settings.validation_range)),
                max(GENESIS_SEQ, block.sequence_number - 1))

    def get_block_before_or_crawl(self, block, persistence, peer):
        self._logger.debug(f"crawling for block before")
        if block.previous_hash == GENESIS_HASH:
            return None
        blockBefore = persistence.get_block_with_hash(block.previous_hash)
        if not blockBefore:
            # print(f"NOT {block.sequence_number-1}")
            self.crawl_blocks_before(block, peer) #attempt crawl
        blockBefore = persistence.get_block_with_hash(block.previous_hash) #get again
        if not blockBefore:
            raise self.MissingSenderBlocks(f"Missing {hexlify(block.public_key)[-8:]}:{block.sequence_number-1} while verifying {block}")
        return blockBefore

    def ensure_money_sender_blocks(self, block, persistence, peer):
        # print()
        # print(block)
        self._logger.debug(f"ensure peer {block.sequence_number} ")
        if block.type == BlockTypes.CHECKPOINT:
            linked = persistence.get_linked(block)
            if linked is not None and self.is_valid_gateway():
                self._logger.debug("Found full checkpoint")
                # print("full")
                return # got everything we needed
            else:
                # print("half")
                self._logger.debug("Found half checkpoint")
        else:
            self._logger.debug("Found normal block")

        # recurse
        # print("recurse")
        blockBefore = self.get_block_before_or_crawl(block, persistence, peer)
        if block == None: # genesis
            return # done crawling
        return self.ensure_money_sender_blocks(blockBefore, persistence, peer) # recurse

    def validate_receive_money_linked_blocks(self, block, persistence, peer, rollbacks=None):
        if rollbacks is None:
            rollbacks = {}

        # print()
        # print(block)
        if block is None: # base case 1
            # print("genesis")
            return # we validated all receives without errors, we are valid!
        if block.type == BlockTypes.CHECKPOINT: # Base case 2 or continue
            linked = persistence.get_linked(block)
            if linked is not None: #Base case 2
                if linked.is_valid_gateway():
                    # print("full")
                    return #valid
            else: # if linked doesnt exist, the checkpoint is not good enough, recurse
                # print("half")
                pass

        if block.type == BlockTypes.CREATION and block.isAgreement():
            # print("creation")
            self._logger.debug("Found creation")
            linked = persistence.get_linked(block)
            if not linked:
                self.rollback_or_raise( block, rollbacks,
                        self.MissingSenderBlocks("Missing creation proposal") #linked would have been delivered with the acceptance
                        )
            elif not linked.is_valid_gateway():
                self.rollback_or_raise( block, rollbacks,
                        self.InvalidSender("UnsanctionedGateway creation")
                        )
        if block.type == BlockTypes.TRANSFER and block.isAgreement():
            # print("transfer")
            self._logger.debug("Found transaction")

            linked = persistence.get_linked(block)
            #TODO: crawl linked????

            try:
                # crawl for their block until their next checkpoint
                self.ensure_money_sender_blocks(linked, persistence, peer)

                # Compute the balance
                senderBalance = linked.get_verified_balance(persistence)
                if senderBalance < 0:
                    raise self.InvalidSender(f'Sender verifiedBalance balance ({block.sequence_number}): {verifiedBalance} is not sufficient')
            except Exception as e:
                # if persistence.did_double_spend(block.public_key):
                self.rollback_or_raise(block, rollbacks, e)
                # else:
                #     raise self.MissingSenderBlocks(f"Missing blocks while verifying {block}")

        if block.type == BlockTypes.ROLLBACK and block.isProposal(): # maintain rollbacks for later/deeper lookup
            # print("rollback")
            rollbacks[unhexlify(block.transaction["transaction_hash"])] = block

        # validate this block done, move on to next block
        blockBefore = block.get_block_before_or_raise(block, persistence) # must be available
        return self.validate_receive_money_linked_blocks(blockBefore, persistence, peer, rollbacks) # recurse

    def rollback_or_raise(self, block, rollbacks, exception=None):
        if (block.hash in rollbacks and
                rollbacks[block.hash].transaction["amount"] == block.transaction.get("amount", None)):
            return #block has been rolled back
        else:
            #TODO: Neatly ask user to Roll back the block
            raise (exception or self.InvalidSender(str(block)))

    def validate_eurotoken_transaction(self, persistence):
        super(EuroTokenCheckpointBlock, self).validate_eurotoken_transaction(persistence)

        if (self.isProposal() and
                self.link_public_key == persistence.my_pk and # for me
                not persistence.get_linked(self)): #not signed

            # Ensure the existance and validity of all linked blocks
            peer = Peer(self.public_key)
            self.validate_receive_money_linked_blocks(self, persistence, peer)

        return ValidationResult.valid, []

    class MissingSenderBlocks(EuroTokenBlock.ValidNoSign):
        pass

    class InvalidSender(EuroTokenBlock.ValidNoSign):
        pass

class EuroTokenCheckpointBlockListener(EuroTokenBlockListener):
    BLOCK_CLASS = EuroTokenCheckpointBlock

    # def __init__(self, *args, **kwargs):
    #     self._logger = logging.getLogger(self.__class__.__name__)
    #     return super(EuroTokenCheckpointBlockListener, self).__init__(*args, **kwargs)
