from pyipv8.ipv8.test.attestation.trustchain.test_block import MockDatabase as TrustChainMockDatabase

from blockchain.ipv8.trustchain.blocks.base       import EuroTokenBlockListener
from blockchain.ipv8.trustchain.blocks.creation   import EuroTokenCreationBlock
from blockchain.ipv8.trustchain.blocks.destruction import EuroTokenDestructionBlock
from blockchain.ipv8.trustchain.blocks.rollback   import EuroTokenRollBackBlock
from blockchain.ipv8.trustchain.blocks.transfer   import EuroTokenTransferBlock
from blockchain.ipv8.trustchain.blocks.checkpoint import EuroTokenCheckpointBlock

from pyipv8.ipv8.keyvault.crypto import default_eccrypto

import unittest
from unittest.mock import Mock

from pyipv8.ipv8.test.attestation.trustchain.test_block import TestBlock as TrustChainTestBlock
from pyipv8.ipv8.attestation.trustchain.block import EMPTY_SIG, GENESIS_HASH, GENESIS_SEQ, TrustChainBlock, ValidationResult, UNKNOWN_SEQ
from blockchain.ipv8.trustchain.blocks.block_types import BlockTypes


class TestEuroTokenCreationBlock   (EuroTokenCreationBlock, TrustChainTestBlock):
    pass
class TestEuroTokenDestructionBlock(EuroTokenDestructionBlock, TrustChainTestBlock):
    pass
class TestEuroTokenRollBackBlock   (EuroTokenRollBackBlock, TrustChainTestBlock):
    pass
class TestEuroTokenTransferBlock   (EuroTokenTransferBlock, TrustChainTestBlock):
    pass
class TestEuroTokenCheckpointBlock (EuroTokenCheckpointBlock, TrustChainTestBlock):
    def __init__(self, *args, **kwargs):
        self.community = Mock()
        super(TestEuroTokenCheckpointBlock, self).__init__(*args, **kwargs)

    def crawl_blocks_before(self, block, peer):
        return self.community.send_crawl_request(peer, block.public_key,
                max(GENESIS_SEQ, (block.sequence_number - 5)),
                max(GENESIS_SEQ, block.sequence_number - 1))

def TestWallet():
    crypto = default_eccrypto
    return crypto.generate_key(u"curve25519")

class LinkData():
    def __init__(self, links):
        self.public_key = links.pub().key_to_bin()
        self.sequence_number = UNKNOWN_SEQ

def TestBlock(*args, **kwargs):
    btype = kwargs["block_type"]
    links = kwargs.pop("links", None)
    if links and not "linked" in kwargs:
        kwargs["linked"] = LinkData(links)

    if btype == BlockTypes.CHECKPOINT:
        return TestEuroTokenCheckpointBlock(*args, **kwargs)
    elif btype == BlockTypes.CREATION:
        return TestEuroTokenCreationBlock(*args, **kwargs)
    elif btype == BlockTypes.DESTRUCTION:
        return TestEuroTokenDestructionBlock(*args, **kwargs)
    elif btype == BlockTypes.TRANSFER:
        return TestEuroTokenTransferBlock(*args, **kwargs)
    elif btype == BlockTypes.ROLLBACK:
        return TestEuroTokenRollBackBlock(*args, **kwargs)
    else:
        return None

class MockDatabase(TrustChainMockDatabase):
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop("owner", None) or TestWallet()
        self.my_pk = self.owner.pub().key_to_bin()
        self.hash_map = {}
        return super(MockDatabase, self).__init__(*args, **kwargs)

    def add_block(self, block):
        self.hash_map[block.hash] = block
        return super(MockDatabase, self).add_block(block)

    def did_double_spend(self, public_key):
        """
        Return whether a specific user did a double spend in the past.
        """
        count = len([ "¯\\_(ツ)_/¯" for block1, block2 in self.double_spends if block1.public_key == public_key ])
        return count > 0

    def get_linked(self, blk):
        if self.data.get(blk.link_public_key) is None:
            return None
        item = [i for i in self.data[blk.link_public_key] if
                (i.sequence_number == blk.link_sequence_number and i.public_key == blk.link_public_key) or
                (i.link_sequence_number == blk.sequence_number and i.link_public_key == blk.public_key)]
        return item[0] if item else None

    def get_block_with_hash(self, block_hash):
        return self.hash_map.get(block_hash, None)

def getWalletBlockWithBalance(balance, db, gateway=None):
    if gateway is None:
        gateway = db.owner or TestWallet()
    new = TestWallet()
    before = TestBlock( #not really verified or added to DB, the checkpoint should "hide" it
            key=new,
            block_type=BlockTypes.TRANSFER,
            transaction={ 'balance':0, 'amount':balance},
            linked = TestBlock(
                key=gateway,
                block_type=BlockTypes.TRANSFER,
                transaction={
                    'balance':0,
                    'amount':balance}
                )
            )
    req = TestBlock(
            key=new,
            block_type=BlockTypes.CHECKPOINT,
            transaction={'balance': balance},
            previous=before,
            links=gateway
            )
    db.add_block(req)
    db.add_block(
            TestBlock(
                key=gateway,
                block_type=BlockTypes.CHECKPOINT,
                transaction={'balance': balance},
                linked=req
                )
            )
    return req

