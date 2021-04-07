from blockchain.ipv8.trustchain.blocks.base   import EuroTokenBlock, EuroTokenBlockListener
from pyipv8.ipv8.attestation.trustchain.block import ValidationResult

from binascii import unhexlify

class EuroTokenRollBackBlock(EuroTokenBlock):

    def get_valid_balance_change(self):
        return 0

    def validate_eurotoken_transaction_agreement(self, database):
        raise Invalid("Meaningless block")

    def validate_eurotoken_transaction_proposal(self, database):
        if "amount" not in self.transaction:
            raise self.MissingAmount('amount missing from transaction')

        if "transaction_hash" not in self.transaction:
            raise self.MissingTransactionHash('transaction_hash missing from transaction')

        rolled_back = database.get_block_with_hash(unhexlify(self.transaction["transaction_hash"]))
        if rolled_back is not None: #if we can reject an incorrect block now, thats better than later
            if rolled_back.transaction["amount"] != self.transaction["amount"]:
                raise self.InvalidRollback("associated transaction amount does not match")

        super(EuroTokenRollBackBlock, self).validate_eurotoken_transaction_proposal(database)


    class MissingTransactionHash(EuroTokenBlock.Invalid):
        pass

    class MissingAmount(EuroTokenBlock.Invalid):
        pass

class EuroTokenRollBackBlockListener(EuroTokenBlockListener):
    BLOCK_CLASS = EuroTokenRollBackBlock
