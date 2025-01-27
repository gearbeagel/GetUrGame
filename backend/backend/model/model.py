import re
import logging
import joblib
import kagglehub
import keras
import numpy as np
import pandas as pd
from keras.src.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from keras.src.models import Model
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l2
from tensorflow.keras import metrics
from textblob import TextBlob
import matplotlib.pyplot as plt
import os

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")


def ensure_data_directory():
    """Ensure that the model directory exists."""
    if not os.path.exists("./backend/model"):
        os.makedirs("./model")
        logging.info("Created directory: ./model")


def analyze_review_sentiment(review_text):
    """Analyze the sentiment of a review using TextBlob."""
    if isinstance(review_text, str):
        blob = TextBlob(review_text)
        return blob.sentiment.polarity
    return 0


def parse_estimated_owners(owner_range):
    """Parse the estimated owners range into a single number."""
    try:
        lower, upper = owner_range.split(" - ")
        return (int(lower) + int(upper)) / 2
    except ValueError:
        return 0


def preprocess_data(df):
    """Preprocess the input DataFrame."""
    required_columns = [
        "short_description", "tags", "genres", "reviews", "estimated_owners"
    ]
    for col in required_columns:
        if col not in df.columns:
            raise KeyError(f"Missing required column: {col}")

    df["combined_features"] = (df["short_description"].fillna("") + " " +
                               df["tags"].fillna("") + " " +
                               df["genres"].fillna(""))
    df["score"] = 0
    df["combined_features"] = df["combined_features"].apply(
        lambda x: re.sub(r"[^a-zA-Z0-9\s.,!?\';:-]', '', x"))
    df["review_sentiment"] = df["reviews"].apply(analyze_review_sentiment)
    df["estimated_owners_processed"] = df["estimated_owners"].apply(
        parse_estimated_owners)
    return df


def get_tfidf_and_scaler(df,
                         tfidf_path="./backend/model/tfidf.pkl",
                         scaler_path="./backend/model/scaler.pkl"):
    if os.path.exists(tfidf_path) and os.path.exists(scaler_path):
        logging.info("TF-IDF and Scaler already exist. Loading them...")
        tfidf = joblib.load(tfidf_path)
        scaler = joblib.load(scaler_path)
    else:
        logging.info("Creating TF-IDF and Scaler...")
        tfidf = TfidfVectorizer(max_features=5000)
        tfidf_matrix = tfidf.fit_transform(df["combined_features"])
        additional_features = df[[
            "review_sentiment", "estimated_owners_processed"
        ]].to_numpy()
        combined_features = np.hstack(
            [tfidf_matrix.toarray(), additional_features])
        scaler = StandardScaler()
        scaler.fit(combined_features)

        joblib.dump(tfidf, tfidf_path)
        joblib.dump(scaler, scaler_path)
        logging.info(
            f"TF-IDF saved to {tfidf_path}, Scaler saved to {scaler_path}")

    return tfidf, scaler


def prepare_data(df, tfidf, scaler):
    """Prepare the dataset for training."""
    combined_features = tfidf.transform(df["combined_features"]).toarray()
    additional_features = df[[
        "review_sentiment", "estimated_owners_processed"
    ]].values
    X = np.hstack([combined_features, additional_features])
    y = df["score"].to_numpy()
    X = scaler.transform(X)
    return X, y


def build_keras_model(input_dim):
    """Build and compile the Keras model."""
    input_layer = Input(shape=(input_dim, ))

    hidden_layer_1 = Dense(256,
                           activation="relu",
                           kernel_regularizer=l2(0.001))(input_layer)
    hidden_layer_2 = Dense(128, activation="relu",
                           kernel_regularizer=l2(0.01))(hidden_layer_1)

    output_layer = Dense(1)(hidden_layer_2)

    model = Model(inputs=input_layer, outputs=output_layer)
    model.compile(optimizer=Adam(),
                  loss="mean_squared_error",
                  metrics=[metrics.MeanSquaredError()])

    return model


def train_and_save_model(df, model_save_path="./backend/model/model.keras"):
    """Train the model and save it to disk."""
    tfidf, scaler = get_tfidf_and_scaler(df)
    X, y = prepare_data(df, tfidf, scaler)
    X_train, X_val, y_train, y_val = train_test_split(X,
                                                      y,
                                                      test_size=0.3,
                                                      random_state=42)

    model = build_keras_model(input_dim=X_train.shape[1])
    early_stopping = EarlyStopping(monitor="val_loss",
                                   patience=3,
                                   restore_best_weights=True)

    history = model.fit(X_train,
                        y_train,
                        epochs=5,
                        batch_size=128,
                        validation_data=(X_val, y_val),
                        callbacks=[early_stopping])

    model.save(model_save_path)
    logging.info(f"Model saved to {model_save_path}")

    plt.plot(history.history["loss"], label="Train Loss")
    plt.plot(history.history["val_loss"], label="Validation Loss")
    plt.legend()
    plt.title("Training History")
    plt.savefig("./backend/model/training_history.png")
    logging.info("Training history saved as ./model/training_history.png")


def get_keras_model(model_path="./backend/model/model.keras"):
    """Load the saved Keras model."""
    return keras.saving.load_model(model_path)


def load_tfidf_and_scaler(tfidf_path="./model/tfidf.pkl",
                          scaler_path="./model/scaler.pkl"):
    """Load saved TF-IDF and scaler."""
    tfidf = joblib.load(tfidf_path)
    scaler = joblib.load(scaler_path)
    return tfidf, scaler


def main():
    """Main function for training and saving the model."""
    try:
        ensure_data_directory()
        logging.info("Downloading dataset...")
        path = kagglehub.dataset_download("artermiloff/steam-games-dataset")
        df = pd.read_csv(path + "/games_may2024_cleaned.csv")

        logging.info("Preprocessing model...")
        df = preprocess_data(df)

        logging.info("Training and saving model...")
        train_and_save_model(df)
    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
