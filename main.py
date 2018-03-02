from uuid import uuid4

from flask import Flask, jsonify, request

from blockchain import Blockchain

# Instantiate a flask app
app = Flask(__name__)

# Create a unique identifier
identifier = str(uuid4()).replace('-', '')

# Instantiate the blockchain
blockchain = Blockchain()


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }

    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check the required fields have been included in the POST data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new transaction
    index = blockchain.new_transaction(
        values['sender'],
        values['recipient'],
        values['amount'],
    )

    response = {'message': f'Transaction will be added to block {index}'}
    return jsonify(response), 201


@app.route('/mine', methods=['GET'])
def mine():
    # Find the next proof
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Receive a reward for finding the proof
    blockchain.new_transaction(
        sender="0",
        recipient=identifier,
        amount=1,
    )

    # Add the new block to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }

    return jsonify(response), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
