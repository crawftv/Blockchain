import hashlib
import requests

import sys
import time
import json

DIFFICULTY = 3


def proof_of_work(last_block):
    """
    Simple Proof of Work Algorithm
    Stringify the block and look for a proof.
    Loop through possibilities, checking each one against `valid_proof`
    in an effort to find a number that is a valid proof
    :return: A valid proof for the provided block
    """

    block_string = json.dumps(last_block, sort_keys=True)
    proof = 0
    while valid_proof(block_string, proof) is False:
        proof += 1
    return proof


def valid_proof(block_string, proof):
    """
    Validates the Proof:  Does hash(block_string, proof) contain 6
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


if __name__ == "__main__":
    # What is the server address? IE `python3 miner.py https://server.com/api/`
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "http://localhost:5000"

    # Load ID
    f = open("my_id.txt", "r")
    id = f.read()
    print("ID is", id)
    f.close()

    # Run forever until interrupted
    while True:
        r = requests.get(url=node + "/last_block")
        # Handle non-json response
        try:
            data = r.json()
        except ValueError:
            print("Error:  Non-json response")
            print("Response returned:")
            print(r)
            break

        # TODO: Get the block from `data` and use it to look for a new proof
        last_block = data["last_block"]
        start = time.time()
        new_proof = proof_of_work(last_block)
        stop = time.time()
        print(f"Time to find proof: {stop-start} seconds")

        # When found, POST it to the server {"proof": new_proof, "id": id}
        post_data = {"proof": new_proof, "id": id}

        r = requests.post(url=node + "/mine", json=post_data)
        data = r.json()
        print(data)
        # TODO: If the server responds with a 'message' 'New Block Forged'
        # r = requests.get(url=node + "/chain")
        # chain = r.json()["chain"]
        # coins = [i["miner"] for i in chain if i["miner"] == id]
        # coins = len(coins)
        # print(f"You currently have won {coins} coins on the chain")
