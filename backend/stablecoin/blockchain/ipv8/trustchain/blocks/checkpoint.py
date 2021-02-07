from stablecoin.blockchain.ipv8.trustchain.blocks.base import EuroTokenBlock, EuroTokenBlockListener
from ipv8.attestation.trustchain.block                 import ValidationResult

class EuroTokenCheckpointBlock(EuroTokenBlock):
    "For now validation is the same as EuroTokenBlock"
    pass

class EuroTokenCheckpointBlockListener(EuroTokenBlockListener):
    BLOCK_CLASS = EuroTokenCheckpointBlock

    def received_block(self, block):
        pass

    def should_sign(self, block):
        return True
