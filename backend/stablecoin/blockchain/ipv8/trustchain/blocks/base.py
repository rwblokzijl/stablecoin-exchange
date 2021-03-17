from pyipv8.ipv8.attestation.trustchain.block     import GENESIS_HASH
from pyipv8.ipv8.attestation.trustchain.block     import TrustChainBlock, ValidationResult
from pyipv8.ipv8.attestation.trustchain.listener  import BlockListener

from blockchain.ipv8.trustchain.db_helper import get_balance_for_block, get_block_balance_change, isProposal, isAgreement

from binascii import hexlify, unhexlify

import logging

class EuroTokenBlock(TrustChainBlock):
    def __init__(self, *args, **kwargs):
        return super(EuroTokenBlock, self).__init__(*args, **kwargs)
        # self.balance = self.transaction["balance"]

    def is_valid_gateway(self, pk):
        return True # For now all gateways are trusted, later this is a very important check

    def validate_transaction(self, persistence):
        # result, errors =  validate_receiving_money(persistence)
        # if result != ValidationResult.valid:
        #     return result, errors
        return self.validate_balance(persistence)

    def validate_receiving_money(self, persistence):
        return ValidationResult.valid, []

    def validate_balance(self, persistence):
        if "balance" not in self.transaction:
            return ValidationResult.invalid, ['balance missing from transaction']

        if isProposal(self):
            blockBefore  = persistence.get_block_with_hash(self.previous_hash)
            if blockBefore is None and self.previous_hash != GENESIS_HASH:
                return ValidationResult.partial_previous, [f'Missing block before']
            else:
                balanceBefore = get_balance_for_block(blockBefore, persistence) or 0
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
        self.logger = logging.getLogger(self.__class__.__name__)
        return s

    def received_block(self, block):
        self.logger.warning(f"Got block {block}")

    def should_sign(self, block):
        return True

