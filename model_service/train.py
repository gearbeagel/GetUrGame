import re
import pandas as pd
import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from textblob import TextBlob

MODEL_DIR = "./model"
os.makedirs(MODEL_DIR, exist_ok=True)

df = pd.read_csv(f"{MODEL_DIR}/games_may2024_cleaned.csv")


def analyze_review_sentiment(review_text):
    if isinstance(review_text, str):
        blob = TextBlob(review_text)
        return blob.sentiment.polarity
    return 0


def parse_estimated_owners(owner_range):
    try:
        lower, upper = owner_range.split(" - ")
        return (int(lower) + int(upper)) / 2
    except ValueError:
        return 0


df["combined_features"] = (
    df["short_description"].fillna("")
    + " "
    + df["tags"].fillna("")
    + " "
    + df["genres"].fillna("")
)

df["combined_features"] = df["combined_features"].apply(
    lambda x: re.sub(r"[^a-zA-Z0-9\s.,!?\';:-]", "", x)
)

df["review_sentiment"] = df["reviews"].apply(analyze_review_sentiment)
df["estimated_owners_processed"] = df["estimated_owners"].apply(parse_estimated_owners)

tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
tfidf_matrix = tfidf.fit_transform(df["combined_features"])

nn_model = NearestNeighbors(n_neighbors=10, metric="cosine", algorithm="brute")
nn_model.fit(tfidf_matrix)

joblib.dump(tfidf, f"{MODEL_DIR}/tfidf.pkl")
joblib.dump(nn_model, f"{MODEL_DIR}/nearest_neighbors.pkl")
df.to_csv(f"{MODEL_DIR}/games_may2024_cleaned.csv", index=False)

print("Model training complete. TF-IDF and NearestNeighbors saved.")
