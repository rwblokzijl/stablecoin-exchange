from ipv8.attestation.trustchain.block     import GENESIS_HASH
from ipv8.attestation.trustchain.block     import TrustChainBlock, ValidationResult
from ipv8.attestation.trustchain.listener  import BlockListener

from stablecoin.blockchain.ipv8.trustchain.db_helper import get_balance_for_block, get_block_balance_change, isProposal, isAgreement

from binascii import hexlify, unhexlify

class EuroTokenBlock(TrustChainBlock):
    def __init__(self, *args, **kwargs):
        return super(EuroTokenBlock, self).__init__(*args, **kwargs)
        # self.balance = self.transaction["balance"]

    def validate_transaction(self, database):
        # result, errors =  validate_receiving_money(database)
        # if result != ValidationResult.valid:
        #     return result, errors
        return self.validate_balance(database)

    def validate_acceptance(self, database):
        result, errors =  ValidationResult.valid, []
        if isAgreement(self):
            if database.get_linked(self).transaction != self.transaction:
                return False
                # result = ValidationResult.invalid
                # errors += ['balance missing from transaction']
        # return result, errors
        return True

    def validate_receiving_money(self, database):
        return ValidationResult.valid, []

    def validate_balance(self, database):
        if "balance" not in self.transaction:
            return ValidationResult.invalid, ['balance missing from transaction']

        if isProposal(self):
            blockBefore  = database.get_block_with_hash(self.previous_hash)
            if blockBefore is None and self.previous_hash != GENESIS_HASH:
                return ValidationResult.partial_previous, [f'Missing block before']
            else:
                balanceBefore = get_balance_for_block(blockBefore, database) or 0
                balanceChange = get_block_balance_change(self)
                if self.transaction["balance"] != balanceBefore + balanceChange:
                    return ValidationResult.invalid, [f'block balance ({self.sequence_number}): {self.transaction["balance"]} does not match calculated balance: {balanceBefore} + {balanceChange} ']

        return ValidationResult.valid, []

    def __str__(self):
        # This makes debugging and logging easier
        trans = self.transaction
        return "Block {0} from ...{1}:{2} links ...{3}:{4} for {5} type {6}".format(
                hexlify(self.hash)[-8:],
                hexlify(self.public_key)[-8:],
                self.sequence_number,
                hexlify(self.link_public_key)[-8:],
                self.link_sequence_number,
                trans,
                self.type)


class EuroTokenBlockListener(BlockListener):
    BLOCK_CLASS = EuroTokenBlock

    def __init__(self, my_peer, community):
        s = super(EuroTokenBlockListener, self).__init__()
        self.my_peer = my_peer
        self.community = community
        return s

    def received_block(self, block):
        pass

    def should_sign(self, block):
        return True

