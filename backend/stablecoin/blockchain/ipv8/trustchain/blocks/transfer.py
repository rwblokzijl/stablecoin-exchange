from blockchain.ipv8.trustchain.blocks.base import EuroTokenBlock, EuroTokenBlockListener
from pyipv8.ipv8.attestation.trustchain.block     import ValidationResult

class EuroTokenTransferBlock(EuroTokenBlock):

    def validate_eurotoken_transaction(self, database):
        if "amount" not in self.transaction:
            raise self.MissingAmount('amount missing from transaction')

        return super(EuroTokenTransferBlock, self).validate_eurotoken_transaction(database)

    class MissingAmount(EuroTokenBlock.Invalid):
        pass

class EuroTokenTransferBlockListener(EuroTokenBlockListener):
    BLOCK_CLASS = EuroTokenTransferBlock
