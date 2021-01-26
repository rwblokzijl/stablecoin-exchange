from stablecoin.blockchain.ipv8.trustchain.blocks.base import EuroTokenBlock, EuroTokenBlockListener
from ipv8.attestation.trustchain.block                 import ValidationResult

class EuroTokenDestructionBlock(EuroTokenBlock):
    def __init__(self, *args, **kwargs):
        super(EuroTokenDestructionBlock, self).__init__(*args, **kwargs)

    def validate_transaction(self, database):
        # result, errors =  super(EuroTokenDestructionBlock, self).validate_transaction(database)
        result, errors =  ValidationResult.valid, []

        if "amount" not in self.transaction:
            result = ValidationResult.invalid
            errors += ['amount missing from transaction']

        if "payment_id" not in self.transaction:
            result = ValidationResult.invalid
            errors += ['payment_id missing from transaction']

        if result != ValidationResult.valid:
            return result, errors

        return ValidationResult.valid, []

class EuroTokenDestructionBlockListener(EuroTokenBlockListener):
    BLOCK_CLASS = EuroTokenDestructionBlock

    def received_block(self, block):
        print("GOT DESTRUCTION!!!")

        self.community.eurotoken_blockchain.on_payment(
                block.transaction["payment_id"],
                block.transaction["amount"],
                "temp")
