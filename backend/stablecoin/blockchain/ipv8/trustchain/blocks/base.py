from ipv8.attestation.trustchain.block     import TrustChainBlock, ValidationResult
from ipv8.attestation.trustchain.listener  import BlockListener

from stablecoin.blockchain.ipv8.trustchain.db_helper import get_balance_for_block, get_block_balance_change

from binascii import hexlify, unhexlify

class EuroTokenBlock(TrustChainBlock):
    def __init__(self, *args, **kwargs):
        super(EuroTokenBlock, self).__init__(*args, **kwargs)
        # self.balance = self.transaction["balance"]

    def validate_transaction(self, database):
        return self.validate_balance(database)

    def validate_acceptance(self, database):
        result, errors =  ValidationResult.valid, []
        if self.isAgreement():
            if database.get_linked(self).transaction != self.transaction:
                return False
                # result = ValidationResult.invalid
                # errors += ['balance missing from transaction']
        # return result, errors
        return True


    def validate_balance(self, database):
        print("validating")
        result, errors =  ValidationResult.valid, []
        if "balance" not in self.transaction:
            result = ValidationResult.invalid
            errors += ['balance missing from transaction']

        if result != ValidationResult.valid:
            return result, errors

        balanceBefore = get_balance_for_block(database.get_block_before(self), database)
        balanceChange = get_block_balance_change(self)
        if self.transaction["balance"] != balanceBefore + balanceChange:
            result = ValidationResult.invalid
            errors += [f'block balance: {self.transaction["balance"]} does not match calculated balance: {balanceBefore} + {balanceChange} ']

        if result != ValidationResult.valid:
            return result, errors

        return ValidationResult.valid, []

    def __str__(self):
        # This makes debugging and logging easier
        trans = self.transaction
        trans['sender'] = trans['sender'][-8:]
        trans['receiver'] = trans['receiver'][-8:]
        return "Block {0} from ...{1}:{2} links ...{3}:{4} for {5} type {6}".format(
                hexlify(self.hash)[-8:],
                hexlify(self.public_key)[-8:],
                self.sequence_number,
                hexlify(self.link_public_key)[-8:],
                self.link_sequence_number,
                trans,
                self.type)


class EuroTokenBlockOld(TrustChainBlock):
    def balance(self, database):
        if self.transaction['sender'] == self.public_key:
            return self.transaction['balance']
        else:
            return self.get_sender_balance_from_chain_before_block(database) + self.transaction['amount']

    def get_sender_balance_from_chain_before_block(self, database):

        # TODO: This can be made more efficient
        # 1. include the receiver balance in the agreement somehow, else
        # 2. get the blocks in 1 query and loop over them
        " Get the balance of self.transaction[sender] at the point before this block "
        sender = self.transaction['sender']

        # self is first
        if self.sequence_number == 1:
            return INITIAL_BALANCE

        #add up all balances until last verified balance
        known_balance = 0
        check_block = database.get_block_before(self)
        while (check_block is not None and
                check_block.sequence_number != 1 and
                check_block.transaction['receiver'] != sender):
            # sender revieved money this block
            if check_block.type == b'transfer': #ignore wrong blocks
                known_balance += check_block.transaction['amount']
            check_block = database.get_block_before(check_block)
        if check_block is None:
            return None
        if check_block.sequence_number == 1:
            # We are at the genesis block
            known_balance += INITIAL_BALANCE
        else:
            # check_block is the last verified block
            known_balance += check_block.transaction['balance']

        return known_balance

    def validate_transaction(self, database):
        return ValidationResult.valid, []
    # link = database.get_linked(self)

        sender_trans_pub = unhexlify(self.transaction['sender'])
        receiv_trans_pub = unhexlify(self.transaction['receiver'])

        # Check if transaction ids matches block ids
        if (sender_trans_pub == self.public_key) and (receiv_trans_pub == self.link_public_key):
            # This is a proposal block
            pass
        elif (sender_trans_pub == self.link_public_key) and(receiv_trans_pub == self.public_key):
            # This is an agreement block
            pass
        else:
            # print("sender_trans_pub     ", sender_trans_pub)
            # print("receiv_trans_pub     ", receiv_trans_pub)

            # print("self.public_key      ", self.public_key)
            # print("self.link_public_key ", self.link_public_key)
            return ValidationResult.invalid, ["Transaction keys do not match block keys"]

        # Get senders balance
        sender_balance = self.get_sender_balance_from_chain_before_block(database)
        if sender_balance is None:
            return ValidationResult.partial_previous, ["Missing blocks"]

        if self.transaction['balance'] != sender_balance - self.transaction['amount']:
            return ValidationResult.invalid, [f"Inconsistent balance, block: ({self}), known_balance: ({sender_balance})"]
        if self.transaction['balance'] < 0:
            return ValidationResult.invalid, ["Insufficient funds"]
        return ValidationResult.valid, []

class EuroTokenBlockListener(BlockListener):
    BLOCK_CLASS = EuroTokenBlock

    def __init__(self, my_peer, community):
        super(EuroTokenBlockListener, self).__init__()
        self.my_peer = my_peer
        self.community = community

    def should_sign(self, block):
        return True

    def received_block(self, block):
        print("GOT A BLOCK")

