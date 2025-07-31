import csv
import random
import nltk

nltk.download('brown')
from nltk.corpus import brown

def caesar_encrypt(plaintext, shift=3):
    result = ''
    for char in plaintext:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char
    return result

def xor_encrypt(plaintext, key=42):
    return ''.join(chr(ord(c) ^ key) for c in plaintext)

def vigenere_encrypt(plaintext, key):
    result = ''
    key = key.lower()
    key_index = 0
    for char in plaintext:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            k = ord(key[key_index % len(key)]) - ord('a')
            result += chr((ord(char) - base + k) % 26 + base)
            key_index += 1
        else:
            result += char
    return result

# Use Brown corpus sentences as plaintexts
sentences = [' '.join(sent) for sent in brown.sents()]

with open('../logs/cipher_dataset.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ciphertext', 'label'])

    # Caesar samples
    for shift in [1, 3, 5, 7]:
        for _ in range(100):
            pt = random.choice(sentences).lower()
            ct = caesar_encrypt(pt, shift)
            writer.writerow([ct, 'caesar'])

    # XOR samples
    for key in [13, 42, 99]:
        for _ in range(100):
            pt = random.choice(sentences).lower()
            ct = xor_encrypt(pt, key)
            writer.writerow([ct, 'xor'])

    # Vigenère samples
    for key in ['key', 'test', 'abc', 'crypto']:
        for _ in range(100):
            pt = random.choice(sentences).lower()
            ct = vigenere_encrypt(pt, key)
            writer.writerow([ct, 'vigenere'])

print("Dataset generated!")