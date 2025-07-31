def calculate_score(cipher, key_size, mode=None, hash_algo=None):
    if cipher == 'AES':
        if key_size == 128:
            return 5
        elif key_size == 192:
            return 7
        elif key_size == 256:
            return 9
    elif cipher == 'RSA':
        if key_size == 1024:
            return 4
        elif key_size == 2048:
            return 8
        elif key_size == 4096:
            return 10
    return 0