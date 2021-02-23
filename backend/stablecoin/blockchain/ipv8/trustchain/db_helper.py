from pyipv8.ipv8.attestation.trustchain.block                       import EMPTY_PK, UNKNOWN_SEQ, GENESIS_SEQ
from blockchain.ipv8.trustchain.blocks.block_types import BlockTypes

def isProposal(block):
    if block.link_sequence_number == UNKNOWN_SEQ:
        return True
    else:
        return False

def isAgreement(block):
    return not isProposal(block)

def get_verified_balance_for_block(block, persistence):
    if not block: # base 1
        return None
    if block.sequence_number == GENESIS_SEQ: # base 2
        return get_negative_block_balance_change(block)

    if block.type not in BlockTypes.EUROTOKEN_TYPES:
        return get_verified_balance_for_block( persistence.get_block_with_hash(block.previous_hash), persistence)

    if block.type == BlockTypes.CHECKPOINT and isProposal(block): #base 3
        linked = persistence.get_linked(block)
        if linked is not None and linked.public_key == persistence.my_pk: #Found full checkpoint
            return block.transaction["balance"]
        else: #Found half checkpoint
            return self.get_verified_balance_for_block(persistence.get_block_with_hash(block.previous_hash), persistence) # recurse
    else:
        balanceBefore = self.get_verified_balance_for_block(persistence.get_block_with_hash(block.previous_hash), persistence) # recurse
        if balanceBefore == None:
            return None
        return balanceBefore - get_negative_block_balance_change(block)

def get_negative_block_balance_change(block):
    return min(0, get_block_balance_change(block))

def get_block_balance_change(block):
    if not block:
        return 0
    if  block.type in [ BlockTypes.TRANSFER, BlockTypes.DESTRUCTION, BlockTypes.ROLLBACK ] and isProposal(block):# block is sending money
        return -block.transaction["amount"]
    elif block.type in [ BlockTypes.TRANSFER, BlockTypes.CREATION ] and isAgreement(block): # block is receiving money
        return block.transaction["amount"]
    else: #block does nothing
        # print(f"Does nothing ({block.type})" )
        return 0

def get_balance_for_block(block, persistence):
    "Gets balance for a block from all previous blocks"
    if not block:
        return None
    if block.sequence_number == GENESIS_SEQ:
        return get_block_balance_change(block)

    #if this block is not a ET block get return balance of block before
    if block.type not in BlockTypes.EUROTOKEN_TYPES:
        return get_balance_for_block( persistence.get_block_with_hash(block.previous_hash), persistence)

    if  block.type in [ BlockTypes.TRANSFER, BlockTypes.DESTRUCTION, BlockTypes.CHECKPOINT ] and isProposal(block):
        # block contains balance (base case)
        return block.transaction["balance"]
    elif block.type in [BlockTypes.TRANSFER, BlockTypes.CREATION] and isAgreement(block):
        # block is receiving money add it and recurse
        balanceBefore = get_balance_for_block(persistence.get_block_with_hash(block.previous_hash), persistence)
        if balanceBefore == None:
            return None
        return balanceBefore + get_block_balance_change(block)
    else:
        #bad type that shouldn't exist, for now just ignore and return for next
        return get_balance_for_block(persistence.get_block_with_hash(block.previous_hash), persistence)
