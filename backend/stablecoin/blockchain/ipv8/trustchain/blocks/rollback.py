from blockchain.ipv8.trustchain.blocks.base import EuroTokenBlock, EuroTokenBlockListener
from pyipv8.ipv8.attestation.trustchain.block     import ValidationResult

class EuroTokenRollBackBlock(EuroTokenBlock):
    def __init__(self, *args, **kwargs):
        super(EuroTokenRollBackBlock, self).__init__(*args, **kwargs)

    def validate_transaction(self, database):
        result, errors =  super(EuroTokenRollBackBlock, self).validate_transaction(database)

        if "amount" not in self.transaction:
            return ValidationResult.invalid, errors + ['amount missing from transaction']

        if "transaction_hash" not in self.transaction:
            return ValidationResult.invalid, errors + ['transaction_hash missing from transaction']

        if result != ValidationResult.valid: #partial is not allowed after this point
            return result, errors

        rolled_back = database.get_block_with_hash(self.transaction["transaction_hash"])
        if rolled_back is None: #the balance verification makes sure the chain is full
            return ValidationResult.invalid, ["associated transaction not found"]

        if rolled_back.transaction["amount"] != -self.transaction["amount"]:
            return ValidationResult.invalid, ["associated transaction amount does not match"]

        return ValidationResult.valid, []

class EuroTokenRollBackBlockListener(EuroTokenBlockListener):
    BLOCK_CLASS = EuroTokenRollBackBlock
