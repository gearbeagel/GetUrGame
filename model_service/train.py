import re
import pandas as pd
import joblib
import os
import logging
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from textblob import TextBlob

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

MODEL_DIR = "./model"
os.makedirs(MODEL_DIR, exist_ok=True)
logger.info(f"Model directory created/verified at {MODEL_DIR}")

logger.info("Loading dataset...")
start_time = time.time()
df = pd.read_csv(f"{MODEL_DIR}/games_may2024_full.csv")
logger.info(
    f"Dataset loaded with {len(df)} games in {time.time() - start_time:.2f} seconds"
)


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


logger.info("Starting data preprocessing...")
start_time = time.time()

logger.info("Creating combined features from descriptions, tags, and genres...")
df["combined_features"] = (
    df["short_description"].fillna("")
    + " "
    + df["categories"].fillna("")
    + " "
    + df["genres"].fillna("")
    + " "
    + df["tags"].fillna("")
)

logger.info("Cleaning text in combined features...")
df["combined_features"] = df["combined_features"].apply(
    lambda x: re.sub(r"[^a-zA-Z0-9\s.,!?\';:-]", "", x)
)

logger.info("Analyzing review sentiment...")
df["review_sentiment"] = df["reviews"].apply(analyze_review_sentiment)
logger.info("Processing estimated owners...")
df["estimated_owners_processed"] = df["estimated_owners"].apply(parse_estimated_owners)

logger.info(f"Data preprocessing completed in {time.time() - start_time:.2f} seconds")

logger.info("Starting feature extraction with TF-IDF...")
start_time = time.time()
tfidf = TfidfVectorizer(stop_words="english", max_features=1000)
tfidf_matrix = tfidf.fit_transform(df["combined_features"])
logger.info(
    f"TF-IDF vectorization completed in {time.time() - start_time:.2f} seconds. Matrix shape: {tfidf_matrix.shape}"
)

logger.info("Extracting primary genre for each game...")
df["primary_genre"] = (
    df["genres"].fillna("").apply(lambda x: x.split(",")[0].strip() if x else "Unknown")
)
genre_counts = df["primary_genre"].value_counts()
logger.info(
    f"Found {len(genre_counts)} unique primary genres. Top 5: {genre_counts.head().to_dict()}"
)

logger.info("Encoding genre labels...")
label_encoder = LabelEncoder()
genre_labels = label_encoder.fit_transform(df["primary_genre"])

logger.info("Training RandomForest classifier...")
start_time = time.time()
rf_model = RandomForestClassifier(
    n_estimators=200,  # More trees
    max_depth=20,  # Deeper trees
    min_samples_split=5,  # Prevent overfitting
    min_samples_leaf=2,  # Prevent overfitting
    random_state=42,
)
rf_model.fit(tfidf_matrix, genre_labels)
logger.info(f"Model training completed in {time.time() - start_time:.2f} seconds")

logger.info("Preparing slim dataset for recommendations...")
essential_columns = [
    "name",
    "AppID",
    "short_description",
    "header_image",
    "combined_features",
    "primary_genre",
]
df_slim = df[essential_columns]
logger.info(
    f"Slim dataset created with {len(df_slim)} rows and {len(essential_columns)} columns"
)

logger.info("Saving models and dataset...")
start_time = time.time()
joblib.dump(tfidf, f"{MODEL_DIR}/tfidf.pkl", compress=9)
logger.info("TF-IDF vectorizer saved")
joblib.dump(rf_model, f"{MODEL_DIR}/random_forest.pkl", compress=9)
logger.info("RandomForest model saved")
joblib.dump(label_encoder, f"{MODEL_DIR}/label_encoder.pkl", compress=9)
logger.info("Label encoder saved")
df_slim.to_csv(f"{MODEL_DIR}/games_may2024_cleaned.csv", index=False)
logger.info("Slim dataset saved to CSV")
logger.info(f"All models and data saved in {time.time() - start_time:.2f} seconds")

logger.info("Model training pipeline completed successfully")
print("Model training complete. TF-IDF and RandomForest classifier saved.")
