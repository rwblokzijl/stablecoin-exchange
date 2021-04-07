from blockchain.ipv8.trustchain.blocks.base   import EuroTokenBlock, EuroTokenBlockListener
from pyipv8.ipv8.attestation.trustchain.block import ValidationResult

class EuroTokenCreationBlock(EuroTokenBlock):
    def validate_eurotoken_transaction_proposal(self, database):
        if "amount" not in self.transaction:
            raise self.MissingAmount('amount missing from transaction')

        # if "payment_id" not in self.transaction:
        #     result = ValidationResult.invalid
        #     errors += ['payment_id missing from transaction']

        return ValidationResult.valid, []

    class MissingAmount(EuroTokenBlock.Invalid):
        pass

class EuroTokenCreationBlockListener(EuroTokenBlockListener):
    BLOCK_CLASS = EuroTokenCreationBlock
