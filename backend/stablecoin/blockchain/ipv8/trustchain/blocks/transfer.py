from stablecoin.blockchain.ipv8.trustchain.blocks.base import EuroTokenBlock, EuroTokenBlockListener
from ipv8.attestation.trustchain.block     import ValidationResult

class EuroTokenTransferBlock(EuroTokenBlock):
    def __init__(self, *args, **kwargs):
        super(EuroTokenTransferBlock, self).__init__(*args, **kwargs)
        # self.amount = self.transaction["amount"]

    def validate_transaction(self, database):
        result, errors =  super(EuroTokenTransferBlock, self).validate_transaction(*args, **kwargs)

        if result != ValidationResult.valid:
            return result, errors

        if "amount" not in self.transaction["amount"]:
            return ValidationResult.invalid, errors + ['amount missing from transaction']

        return ValidationResult.valid, []

class EuroTokenTransferBlockListener(EuroTokenBlockListener):
    BLOCK_CLASS = EuroTokenTransferBlock
