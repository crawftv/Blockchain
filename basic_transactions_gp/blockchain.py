# Paste your version of blockchain.py from the client_mining_p
# folder here
import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

DIFFICULTY = 6


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash="===============", proof=100, id=0)

    def new_block(self, proof, id, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1]),
            "miner": id,
        }

        # Reset the current list of transactions
        self.current_transactions = []
        # Append the chain to the block
        self.chain.append(block)
        # Return the new block
        return block

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string
        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It convertes the string to bytes.
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        # Create the block_string
        block_string = json.dumps(block, sort_keys=True).encode()

        # Hash this string using sha256
        hash = hashlib.sha256(block_string).hexdigest()

        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand

        # Return the hashed block string in hexadecimal format

        return hash

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        guess = f"{block_string}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:DIFFICULTY] == "0" * DIFFICULTY

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append(
            {"sender": sender, "recipient": recipient, "amount": amount,}
        )


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace("-", "")

# Instantiate the Blockchain
blockchain = Blockchain()


@app.errorhandler(Exception)
@app.route("/mine", methods=["POST"])
def mine():
    try:
        data = request.get_json()
        if ("proof" in data.keys()) and ("id" in data.keys()):
            submitted_proof = data["proof"]
            id = data["id"]

            # Determine if proof is valid
            last_block = blockchain.last_block
            last_blockstring = json.dumps(last_block, sort_keys=True)

            if blockchain.valid_proof(last_blockstring, submitted_proof):

                previous_hash = blockchain.hash(blockchain.last_block)
                new_block = blockchain.new_block(submitted_proof, previous_hash)

                blockchain.new_transaction("0", id, 1)
                r = {
                    "mesasage": "New Block Forged",
                    "block": new_block,
                }
                blockchain.current_transactions = []
                return jsonify(r), 200
            else:
                return jsonify("Error: Proof not valid"), 400
        else:
            return jsonify("Error: missing keys"), 400
    except Exception:
        return jsonify("Error: invalid request"), 400


@app.route("/transaction/new", methods=["POST"])
def transaction():
    # try:

    data = request.get_json()
    required = ["sender", "recipient", "amount"]
    if all(k in data.keys() for k in required):
        blockchain.new_transaction(
            data["sender"], data["recipient"], data["amount"],
        )
        message = {
            "block_index": blockchain.last_block["index"],
            "block": blockchain.last_block,
        }
        return jsonify(message), 200
    else:
        return jsonify("Error: missing keys"), 400


# except Exception:
#     return jsonify("Error: invalid request"), 400


@app.route("/last_block", methods=["GET"])
def last_block():
    last_block = blockchain.last_block
    return jsonify({"last_block": last_block}), 200


@app.route("/chain", methods=["GET"])
def full_chain():
    response = {
        "length": len(blockchain.chain),
        "chain": blockchain.chain,
    }
    return jsonify(response), 200


# Run the program on port 5000
if __name__ == "__main__":
    app.run()
