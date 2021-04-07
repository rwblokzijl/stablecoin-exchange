from blockchain.ipv8.trustchain.blocks.base import EuroTokenBlock, EuroTokenBlockListener
from pyipv8.ipv8.attestation.trustchain.block                 import ValidationResult

class EuroTokenDestructionBlock(EuroTokenBlock):
    def validate_eurotoken_transaction_proposal(self, database):
        if "amount" not in self.transaction:
            raise self.MissingAmount('amount missing from transaction')

        if "payment_id" not in self.transaction and "iban" not in self.transaction:
            result = ValidationResult.invalid
            raise self.MissingPaymentIDorIBAN( 'payment_id and iban missing from transaction')

        return super(EuroTokenDestructionBlock, self).validate_eurotoken_transaction_proposal(database)

    class MissingPaymentIDorIBAN(EuroTokenBlock.Invalid):
        pass

    class MissingAmount(EuroTokenBlock.Invalid):
        pass


class EuroTokenDestructionBlockListener(EuroTokenBlockListener):
    BLOCK_CLASS = EuroTokenDestructionBlock

    def received_block(self, block):
        persistence = self.community.persistence

        if block.public_key == persistence.my_pk: # only once i accepted the transaction
            self.community.eurotoken_blockchain.on_payment(
                    block.transaction.get("payment_id", None),
                    block.transaction.get("iban", None),
                    block.transaction["amount"],
                    block.public_key)

    def should_sign(self, block):
        return True
