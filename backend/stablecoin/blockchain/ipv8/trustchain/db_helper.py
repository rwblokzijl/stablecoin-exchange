from ipv8.attestation.trustchain.block     import EMPTY_PK

def isProposal(block):
    if block.link_public_key == EMPTY_PK:
        return True

def isAgreement(block):
    return not isProposal(block)


def get_block_balance_change(block):
    if not block:
        return 0
    if  block.type in [ MyTrustChainCommunity.BlockTypes.TRANSFER, MyTrustChainCommunity.BlockTypes.DESTRUCTION ] and isProposal(block):# block is sending money
        return -block.transaction["amount"]
    elif block.type in [ MyTrustChainCommunity.BlockTypes.TRANSFER, MyTrustChainCommunity.BlockTypes.CREATION ] and isAgreement(block): # block is receiving money
        return block.transaction["amount"]
    else: #block does nothing
        return 0

def get_balance_for_block(block, persistence):
    if not block:
        return 0
    if block.type not in MyTrustChainCommunity.BlockTypes.EUROTOKEN_TYPES:
        return getBalanceForBlock(persistence.get_block_before(block))
    if ( ( block.type in [ MyTrustChainCommunity.BlockTypes.TRANSFER, MyTrustChainCommunity.BlockTypes.DESTRUCTION, MyTrustChainCommunity.BlockTypes.CHECKPOINT ] and isProposal(block)) or
        (block.type == MyTrustChainCommunity.BlockTypes.CREATION and isAgreement(block))):
        # block contains balance (base case)
        return block.transaction["balance"]
    elif block.type == MyTrustChainCommunity.BlockTypes.TRANSFER and isAgreement(block):
        # block is receiving money add it and recurse
        return get_balance_for_block(persistence.get_block_before(block)) + get_block_balance_change(block)
    else:
        #bad type that shouldn't exist, for now just ignore and return for next
        return get_balance_for_block(persistence.get_block_before(block))
