import hashlib
import json
import requests
from urllib.parse import urlparse
from time import time


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        self.nodes = set()

        # Genesis block
        self.new_block(previous_hash=1, proof=100)

    def register_node(self, address):
        """Add a new node to the list of nodes

        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """Determine if a given blockchain is valid

        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n----------------\n")

            # Check the block's hash
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check the proof
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """Consensus algorithm, it resolves conflicts by replacing the chain
        with the longest valid one in the network

        """

        neighbors = self.nodes
        new_chain = None

        # Look for chains longer than ours
        max_length = len(self.chain)

        for node in neighbors:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we found a new one
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash=None):
        """Create a new block and add it to the chain

        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the list of transactions
        self.current_transactions = []

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

    def valid_proof(self, last_proof, proof, difficulty):
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
