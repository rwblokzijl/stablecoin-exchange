from stablecoin.blockchain.ipv8.trustchain.blocks.base import EuroTokenBlock, EuroTokenBlockListener
from ipv8.attestation.trustchain.block                 import ValidationResult

class EuroTokenCreationBlock(EuroTokenBlock):
    def __init__(self, *args, **kwargs):
        super(EuroTokenCreationBlock, self).__init__(*args, **kwargs)

    def validate_transaction(self, database):
        # DO NOT CHECK BALANCE FOR CREATE, GATEWAYS DONT KNOW WHERE THE RECIEVERS CHAIN IS
        # result, errors =  super(EuroTokenCreationBlock, self).validate_transaction(database)
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

class EuroTokenCreationBlockListener(EuroTokenBlockListener):
    BLOCK_CLASS = EuroTokenCreationBlock

    def received_block(self, block):
        print("GOT CREATION!!!")
