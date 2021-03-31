from blockchain.ipv8.trustchain.blocks.base import EuroTokenBlock, EuroTokenBlockListener
from pyipv8.ipv8.attestation.trustchain.block     import ValidationResult

class EuroTokenRollBackBlock(EuroTokenBlock):

    def get_valid_balance_change(self):
        return 0

    def validate_eurotoken_transaction(self, database):
        if "amount" not in self.transaction:
            raise self.MissingAmount('amount missing from transaction')

        if "transaction_hash" not in self.transaction:
            raise self.MissingTransactionHash('transaction_hash missing from transaction')

        super(EuroTokenRollBackBlock, self).validate_eurotoken_transaction(database)


        rolled_back = database.get_block_with_hash(self.transaction["transaction_hash"])
        if rolled_back is None: #the balance verification makes sure the chain is full
            raise self.MissingTransaction("associated transaction not found")

        if rolled_back.transaction["amount"] != self.transaction["amount"]:
            raise self.InvalidTransaction("associated transaction amount does not match")

    class MissingTransactionHash(EuroTokenBlock.Invalid):
        pass

    class MissingTransaction(EuroTokenBlock.Invalid):
        pass

    class InvalidTransaction(EuroTokenBlock.Invalid):
        pass

    class MissingAmount(EuroTokenBlock.Invalid):
        pass

class EuroTokenRollBackBlockListener(EuroTokenBlockListener):
    BLOCK_CLASS = EuroTokenRollBackBlock
