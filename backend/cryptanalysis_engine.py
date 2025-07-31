import joblib

def caesar_brute_force(ciphertext):
    candidates = []
    for shift in range(1, 26):
        result = ''
        for char in ciphertext:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                result += chr((ord(char) - base - shift) % 26 + base)
            else:
                result += char
        candidates.append(result)
    # Pick the candidate with the most common English words
    return max(candidates, key=lambda s: sum(w in s.lower() for w in ['the', 'and', 'of', 'to', 'in', 'is', 'it', 'that']))

def xor_brute_force(ciphertext):
    candidates = []
    for key in range(256):
        try:
            result = ''.join(chr(ord(c) ^ key) for c in ciphertext)
            candidates.append(result)
        except Exception:
            continue
    # Pick the candidate with the most common English words
    return max(candidates, key=lambda s: sum(w in s.lower() for w in ['the', 'and', 'of', 'to', 'in', 'is', 'it', 'that']))

def vigenere_decrypt(ciphertext, key):
    result = ''
    key = key.lower()
    key_index = 0
    for char in ciphertext:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            k = ord(key[key_index % len(key)]) - ord('a')
            result += chr((ord(char) - base - k) % 26 + base)
            key_index += 1
        else:
            result += char
    return result

def predict_and_decrypt(ciphertext):
    vectorizer, model = joblib.load('models/cipher_model.pkl')
    X_vec = vectorizer.transform([ciphertext])
    pred = model.predict(X_vec)[0]
    prob = model.predict_proba(X_vec).max()
    if pred == 'caesar':
        result = caesar_brute_force(ciphertext)
    elif pred == 'xor':
        result = xor_brute_force(ciphertext)
    elif pred == 'vigenere':
        # Try common keys used in your dataset
        for key in ['key', 'test', 'abc', 'crypto']:
            attempt = vigenere_decrypt(ciphertext, key)
            if any(w in attempt.lower() for w in ['the', 'and', 'of', 'to', 'in', 'is', 'it', 'that']):
                result = attempt
                break
        else:
            result = "(Vigenère decryption failed: unknown key)"
    else:
        result = "(Unknown cipher type)"
    return pred, prob, result