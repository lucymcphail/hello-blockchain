import hashlib
import json
from time import time


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """Create a new block and add it to the chain

        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'content': None,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """Creates a new transaction for the next mined block

        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    def proof_of_work(self, last_proof):
        """Simple Proof of Work (PoW) algorithm: Find a number p' such that
        hash(pp') contains four leading zeroes (p is the previous
        proof, p' is the new proof)

        """

        proof = 0

        while self.valid_proof(last_proof, proof, 4) is False:
            proof += 1

        return proof

    def valid_proof(last_proof, proof, difficulty):
        """Validates the proof; does hash(last_proof, proof) contain
        `difficulty' leading zeroes?

        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == "0" * difficulty

    @staticmethod
    def hash(block):
        """Creates a SHA256 hash of a block

        """

        # Make sure the dict is ordered, to avoid inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        """Returns the last block in the chain

        """

        return self.chain[-1]
