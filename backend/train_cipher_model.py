import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib

df = pd.read_csv('../logs/cipher_dataset.csv')
df = df.dropna(subset=['ciphertext', 'label'])  
X = df['ciphertext']
y = df['label']

vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(1, 3))
X_vec = vectorizer.fit_transform(X)

model = MultinomialNB()
model.fit(X_vec, y)

joblib.dump((vectorizer, model), '../models/cipher_model.pkl')
print("Model trained and saved.")