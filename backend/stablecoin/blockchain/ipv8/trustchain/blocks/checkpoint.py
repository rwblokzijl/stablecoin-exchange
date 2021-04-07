from pyipv8.ipv8.attestation.trustchain.block import ValidationResult, GENESIS_SEQ, GENESIS_HASH

from blockchain.ipv8.trustchain.blocks.base        import EuroTokenBlock, EuroTokenBlockListener
from blockchain.ipv8.trustchain.blocks.block_types import BlockTypes

import logging

from binascii import hexlify, unhexlify

class EuroTokenCheckpointBlock(EuroTokenBlock):
    "For now validation is the same as EuroTokenBlock"

    def validate_receive_money_linked_blocks(self, block, persistence, rollbacks=None):
        if rollbacks is None:
            rollbacks = {}

        if block is None: # base case 1
            return # we validated all receives without errors, we are valid!
        if block.type == BlockTypes.CHECKPOINT: # Base case 2 or continue
            linked = persistence.get_linked(block)
            if linked is not None: #Base case 2
                if linked.is_valid_gateway():
                    return #valid
            else: # if linked doesnt exist, the checkpoint is not good enough, recurse
                pass

        if block.type == BlockTypes.CREATION and block.isAgreement():
            # print("creation")
            self._logger.debug("Found creation")
            linked = persistence.get_linked(block)
            if not linked:
                self.rollback_or_raise( block, rollbacks,
                        #linked would have been delivered with the acceptance
                        self.InvalidSend("Missing creation proposal")
                        )
            elif not linked.is_valid_gateway():
                self.rollback_or_raise( block, rollbacks,
                        self.InvalidSend("UnsanctionedGateway creation")
                        )
        if block.type == BlockTypes.TRANSFER and block.isAgreement():
            # print("transfer")
            self._logger.debug("Found transaction")

            linked = block.get_linked_or_crawl(persistence)

            try:
                # crawl for their block until their next checkpoint
                self.verify_balance_available_for_block(linked, persistence)

                # # Compute the balance
                # senderBalance = linked.get_verified_balance(persistence)
                # if senderBalance < 0:
                #     raise self.InvalidSend(f'Sender verifiedBalance balance ({block.sequence_number}): {verifiedBalance} is not sufficient')
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
        return self.validate_receive_money_linked_blocks(blockBefore, persistence, rollbacks) # recurse

    def rollback_or_raise(self, block, rollbacks, exception=None):
        if block.hash in rollbacks:
            if rollbacks[block.hash].transaction["amount"] == block.transaction.get("amount", None):
                return #block has been rolled back
            else:
                raise self.InvalidRollback(f"Rolback {rollbacks[block.hash]} doens't match")
        else:
            #TODO: Neatly ask user to Roll back the block
            raise (exception or self.InvalidSend(str(block)))

    def validate_eurotoken_transaction_proposal(self, persistence):
        # if not self.is_valid_gateway(): # maybe verify this somehow
            # raise self.InvalidSend("UnsanctionedGateway checkpoint")
        if ( self.link_public_key == persistence.my_pk and # for me
                not persistence.get_linked(self)): #not signed

            # Ensure balance
            super(EuroTokenCheckpointBlock, self).validate_eurotoken_transaction_proposal(persistence)

            # Ensure the existance and validity of all linked blocks
            self.validate_receive_money_linked_blocks(self, persistence)
        else:
            self.assert_transaction_balance()

        return ValidationResult.valid, []

    class MissingSenderBlocks(EuroTokenBlock.MissingBlocks):
        pass

    class InvalidSend(EuroTokenBlock.Invalid):
        pass

    class InvalidGateway(EuroTokenBlock.Invalid):
        pass

class EuroTokenCheckpointBlockListener(EuroTokenBlockListener):
    BLOCK_CLASS = EuroTokenCheckpointBlock

    # def __init__(self, *args, **kwargs):
    #     self._logger = logging.getLogger(self.__class__.__name__)
    #     return super(EuroTokenCheckpointBlockListener, self).__init__(*args, **kwargs)
