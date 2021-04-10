from pyipv8.ipv8.attestation.trustchain.database import TrustChainDB

class EvalTrustChainDB(TrustChainDB):

    def __init__(self, working_directory, db_name, my_pk=None):
        self.counter = 0
        return super(EvalTrustChainDB, self).__init__(working_directory, db_name, my_pk)

    def reset_counter(self):
        self.counter = 0

    def count_block_access(self):
        self.counter += 1

    def get_block_with_hash(self, block_hash):
        self.count_block_access()
        return super(EvalTrustChainDB, self).get_block_with_hash(block_hash)

    def get_linked(self, block):
        self.count_block_access()
        return super(EvalTrustChainDB, self).get_linked(block)
