from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
import base64
import csv
from datetime import datetime
import os
import psycopg2

AES_KEY_PATH = "keys/aes/aes_key.bin"
RSA_PUBLIC_KEY_PATH = "keys/rsa/public.pem"

# ------------------ AES ENCRYPTION (CBC + BASE64) ------------------

def encrypt_aes(plaintext):
    with open(AES_KEY_PATH, 'rb') as f:
        key = f.read()

    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    return f"{iv}:{ct}"

# ------------------ RSA ENCRYPTION (Public Key + BASE64) ------------------

def encrypt_rsa(plaintext):
    with open(RSA_PUBLIC_KEY_PATH, 'r') as f:
        public_key = RSA.import_key(f.read())

    cipher_rsa = PKCS1_OAEP.new(public_key)
    ciphertext = cipher_rsa.encrypt(plaintext.encode())
    return base64.b64encode(ciphertext).decode('utf-8')

# ------------------ Logging to CSV + PostgreSQL ------------------

def log_encryption(action, filename, cipher, key_size, score):
    log_file = 'logs/encryption.csv'
    file_exists = os.path.isfile(log_file)
    file_size = os.path.getsize(filename) if os.path.exists(filename) else 0

    # CSV Log
    with open(log_file, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists or os.path.getsize(log_file) == 0:
            writer.writerow(['Action', 'File Name', 'Cipher', 'Key Size', 'Score', 'Timestamp', 'File Size'])
        writer.writerow([
            action,
            filename,
            cipher,
            key_size,
            score,
            datetime.now().isoformat(),
            file_size
        ])

    # PostgreSQL Log
    log_encryption_postgres(action, filename, cipher, key_size, score, file_size)

def log_encryption_postgres(action, filename, cipher, key_size, score, file_size):
    try:
        conn = psycopg2.connect(
            dbname="autocryptguard",
            user="postgres",
            password="Gauri14",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO encryption_log (action, file_name, cipher, key_size, score, timestamp, file_size)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            action,
            filename,
            cipher,
            key_size,
            score,
            datetime.now(),
            file_size
        ))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("PostgreSQL logging failed:", e)
