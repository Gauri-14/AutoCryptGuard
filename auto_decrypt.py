from backend.cryptanalysis_engine import predict_and_decrypt

ciphertext = input("Enter ciphertext: ")
pred, prob, result = predict_and_decrypt(ciphertext)
print(f"Predicted cipher: {pred} (confidence: {prob:.2f})")
print("Decrypted text:", result)