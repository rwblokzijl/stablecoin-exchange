from stablecoin.blockchain.ipv8.trustchain.blocks.base import EuroTokenBlock, EuroTokenBlockListener

class EuroTokenCreationBlock(EuroTokenBlock):
    def __init__(self, *args, **kwargs):
        super(EuroTokenCreationBlock, self).__init__(*args, **kwargs)
        # self.amount = self.transaction["amount"]

    def validate_transaction(self, database):
        result, errors =  super(EuroTokenDestructionBlock, self).validate_transaction(*args, **kwargs)

        if "amount" not in self.transaction:
            result = ValidationResult.invalid
            errors += ['amount missing from transaction']

        if "payment_id" not in self.transaction:
            result = ValidationResult.invalid
            errors += ['payment_id missing from transaction']

        if result != ValidationResult.valid:
            return result, errors

        return ValidationResult.valid, []

class EuroTokenCreationBlockListener(EuroTokenBlockListener):
    BLOCK_CLASS = EuroTokenCreationBlock
