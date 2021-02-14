from blockchain.ipv8.trustchain.blocks.base import EuroTokenBlock, EuroTokenBlockListener
from pyipv8.ipv8.attestation.trustchain.block                 import ValidationResult

class EuroTokenDestructionBlock(EuroTokenBlock):
    def __init__(self, *args, **kwargs):
        return super(EuroTokenDestructionBlock, self).__init__(*args, **kwargs)

    def validate_transaction(self, database):
        # print("VALIDATE DESTRUCTION")
        result, errors =  super(EuroTokenDestructionBlock, self).validate_transaction(database)
        # print("VALIDATE DESTRUCTION PARENT DONE")
        # result, errors =  ValidationResult.valid, []

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
                block.public_key)

    def should_sign(self, block):
        print("SHOULD SIGN")
        return True
