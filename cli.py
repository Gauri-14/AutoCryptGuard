from backend import encryption_engine, score_calculator
from Crypto.Random import get_random_bytes
import os

def get_file(prompt):
    path = input(prompt)
    if not os.path.isfile(path):
        print("File does not exist.")
        return None
    return path

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def main():
    while True:
        print("\n==== AutoCryptGuard Encryption/Decryption ====")
        print("1. Encrypt a file")
        print("2. Decrypt a file")
        print("Q. Quit")
        choice = input("Select an option (1/2 or Q to quit): ").strip().lower()

        if choice == 'q':
            print("Exiting AutoCryptGuard. Goodbye!")
            break

        if choice not in ['1', '2']:
            print("Invalid choice.")
            continue

        print("Choose cipher:")
        print("1. AES")
        print("2. RSA")
        cipher_choice = input("Select cipher (1/2): ").strip()
        if cipher_choice == '1':
            cipher = 'AES'
        elif cipher_choice == '2':
            cipher = 'RSA'
        else:
            print("Invalid cipher choice.")
            continue

        if choice == '1':  # Encrypt
            filename = get_file("Enter path to file to encrypt: ")
            if not filename:
                continue
            with open(filename, 'rb') as f:
                data = f.read()

            if cipher == 'AES':
                ensure_dir('keys/aes')
                ensure_dir('encrypted/aes')
                key = get_random_bytes(16)
                nonce, ciphertext, tag = encryption_engine.aes_encrypt(data, key)
                out_file = os.path.join('encrypted', 'aes', os.path.basename(filename) + '.aes')
                with open(out_file, 'wb') as f:
                    f.write(nonce + tag + ciphertext)
                key_file = os.path.join('keys', 'aes', os.path.basename(filename) + '.aes.key')
                with open(key_file, 'wb') as f:
                    f.write(key)
                print(f"AES key saved to {key_file}")
                score = score_calculator.calculate_score('AES', 128)
                encryption_engine.log_encryption('ENCRYPT', filename, 'AES', 128, score)
                print(f'File encrypted as {out_file}. Score: {score}/10')

            elif cipher == 'RSA':
                ensure_dir('keys/rsa')
                ensure_dir('encrypted/rsa')
                private_key, public_key = encryption_engine.rsa_generate_keys()
                ciphertext = encryption_engine.rsa_encrypt(data, public_key)
                out_file = os.path.join('encrypted', 'rsa', os.path.basename(filename) + '.rsa')
                with open(out_file, 'wb') as f:
                    f.write(ciphertext)
                priv_key_file = os.path.join('keys', 'rsa', os.path.basename(filename) + '.rsa_private.pem')
                pub_key_file = os.path.join('keys', 'rsa', os.path.basename(filename) + '.rsa_public.pem')
                with open(priv_key_file, 'wb') as f:
                    f.write(private_key)
                with open(pub_key_file, 'wb') as f:
                    f.write(public_key)
                print(f"RSA private key saved to {priv_key_file}")
                print(f"RSA public key saved to {pub_key_file}")
                score = score_calculator.calculate_score('RSA', 2048)
                encryption_engine.log_encryption('ENCRYPT', filename, 'RSA', 2048, score)
                print(f'File encrypted as {out_file}. Score: {score}/10')

        elif choice == '2':  # Decrypt
            filename = get_file("Enter path to file to decrypt: ")
            if not filename:
                continue

            if cipher == 'AES':
                ensure_dir(os.path.join('decrypted', 'aes'))
                with open(filename, 'rb') as f:
                    content = f.read()
                nonce = content[:16]
                tag = content[16:32]
                ciphertext = content[32:]
                key_file = os.path.join('keys', 'aes', os.path.basename(filename).replace('.aes', '') + '.aes.key')
                if not os.path.exists(key_file):
                    print(f"Key file {key_file} not found. Cannot decrypt.")
                    continue
                with open(key_file, 'rb') as f:
                    key = f.read()
                try:
                    data = encryption_engine.aes_decrypt(nonce, ciphertext, tag, key)
                    out_file = os.path.join('decrypted', 'aes', os.path.basename(filename).replace('.aes', '') + '.decrypted')
                    with open(out_file, 'wb') as f:
                        f.write(data)
                    print(f'File decrypted as {out_file}')
                    score = score_calculator.calculate_score('AES', 128)
                    encryption_engine.log_encryption('DECRYPT', filename, 'AES', 128, score)
                except Exception as e:
                    print("Decryption failed:", e)

            elif cipher == 'RSA':
                ensure_dir(os.path.join('decrypted', 'rsa'))
                with open(filename, 'rb') as f:
                    ciphertext = f.read()
                priv_key_file = os.path.join('keys', 'rsa', os.path.basename(filename).replace('.rsa', '.rsa_private.pem'))
                if not os.path.exists(priv_key_file):
                    print(f"Private key file {priv_key_file} not found. Cannot decrypt.")
                    continue
                with open(priv_key_file, 'rb') as f:
                    private_key = f.read()
                try:
                    data = encryption_engine.rsa_decrypt(ciphertext, private_key)
                    out_file = os.path.join('decrypted', 'rsa', os.path.basename(filename).replace('.rsa', '') + '.decrypted')
                    with open(out_file, 'wb') as f:
                        f.write(data)
                    print(f'File decrypted as {out_file}')
                    score = score_calculator.calculate_score('RSA', 2048)
                    encryption_engine.log_encryption('DECRYPT', filename, 'RSA', 2048, score)
                except Exception as e:
                    print("Decryption failed:", e)

if __name__ == '__main__':
    main()