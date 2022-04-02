from hashlib import sha256


def SHA256(text):
    return sha256(text.encode("ascii")).hexdigest()


def mine(block_number, transactions, previous_hash, prefix_zeros):
    prefix_str = "0" * prefix_zeros
    for nonce in range(MAX_NONCE): 
        text = str(block_number) + transactions + previous_hash + str(nonce)
        new_hash = SHA256(text)
        if new_hash.startswith(prefix_str):
            print(f"Yay! Successfully mined bitcoins with nonce value: {nonce}")
            return new_hash
    
    raise BaseException(f"Could not find correct hash after trying {MAX_NONCE} times!")


if __name__ == '__main__':
    
    # Input parameters start
    block_number = 3
    transactions = '''
    Akos --> Joska --> 20
    Pista --> Fecko --> 30
    Muci --> Duci --> 3001
    '''
    previous_hash = "b5d4045c3f466fa91fe2cc6abe79232a1a57cdf104f7a26e716e0a1e2789df78"
    difficulty = 8
    # Input parameters end
    
    MAX_NONCE = 10000000000
    import time
    start = time.time()
    print("Mining started.")
    new_hash = mine(block_number, transactions, previous_hash, difficulty)
    total_time = str(round((time.time() - start)))
    print(f"Mining ended. Mining took {total_time} seconds.")
    
    print(new_hash)
