from collections import defaultdict
from typing import Dict, List
import gc
import joblib
import numpy as np
import pandas as pd
import random
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity

MODEL_DIR = "./model"
df = pd.read_csv(f"{MODEL_DIR}/games_may2024_cleaned.csv")
tfidf = joblib.load(f"{MODEL_DIR}/tfidf.pkl")
rf_model = joblib.load(f"{MODEL_DIR}/random_forest.pkl")
label_encoder = joblib.load(f"{MODEL_DIR}/label_encoder.pkl")

random.seed(None)

recent_recommendations: Dict[str, Dict[int, float]] = defaultdict(dict)
MAX_RECENT_GAMES = 20
RECOMMENDATION_COOLDOWN = 3 * 24 * 60 * 60

app = FastAPI()


class GameRequest(BaseModel):
    game_names: list[str]
    user_id: str = None  # Optional user ID for tracking recommendations


def clean_old_recommendations():
    """Clean up old entries from the recommendation cache."""
    current_time = time.time()
    users_to_check = list(recent_recommendations.keys())

    for user_hash in users_to_check:
        user_games = recent_recommendations[user_hash]
        games_to_remove = []

        for game_id, timestamp in user_games.items():
            if current_time - timestamp > RECOMMENDATION_COOLDOWN:
                games_to_remove.append(game_id)

        for game_id in games_to_remove:
            del user_games[game_id]

        if not user_games:
            del recent_recommendations[user_hash]


def get_user_hash(request: GameRequest) -> str:
    """Generate a unique hash for the user based on user_id or game list."""
    if request.user_id:
        return f"user_{request.user_id}"

    game_list = sorted(request.game_names)
    game_str = ",".join(game_list)
    return f"games_{hash(game_str)}"


def update_recent_recommendations(user_hash: str, recommended_games: List[dict]):
    """Update the cache with newly recommended games."""
    current_time = time.time()

    user_recent = recent_recommendations[user_hash]

    for game in recommended_games:
        user_recent[game["appid"]] = current_time

    if len(user_recent) > MAX_RECENT_GAMES:
        sorted_games = sorted(user_recent.items(), key=lambda x: x[1])
        games_to_keep = sorted_games[-MAX_RECENT_GAMES:]

        recent_recommendations[user_hash] = dict(games_to_keep)


def create_user_profile(valid_games):
    """
    Create a user profile based on the genre probabilities of owned games.

    Args:
        valid_games (DataFrame): DataFrame containing the user's valid games

    Returns:
        numpy.ndarray: User profile as a 1D array of genre probabilities
    """
    owned_indices = valid_games.index.tolist()
    owned_features = df.iloc[owned_indices]["combined_features"].values

    owned_tfidf = tfidf.transform(owned_features)
    owned_genre_probs = rf_model.predict_proba(owned_tfidf)
    user_profile = owned_genre_probs.mean(axis=0).reshape(1, -1)

    del owned_tfidf, owned_genre_probs
    gc.collect()

    return user_profile


def find_candidate_games(
    user_profile, owned_games, user_recent_games, candidate_pool_size=50
):
    """
    Find candidate games for recommendation by processing in batches.

    Args:
        user_profile (numpy.ndarray): User profile as a 1D array of genre probabilities
        owned_games (set): Set of game names owned by the user
        user_recent_games (set): Set of game IDs recently recommended to the user
        candidate_pool_size (int): Maximum number of candidates to collect

    Returns:
        list: List of candidate game dictionaries with similarity scores
    """
    batch_size = 1000
    candidates = []

    for start_idx in range(0, len(df), batch_size):
        end_idx = min(start_idx + batch_size, len(df))
        batch_indices = list(range(start_idx, end_idx))

        batch_games = set(df.iloc[batch_indices]["name"].values)
        if not batch_games - owned_games:
            continue

        batch_features = df.iloc[batch_indices]["combined_features"].values
        batch_tfidf = tfidf.transform(batch_features)
        batch_genre_probs = rf_model.predict_proba(batch_tfidf)
        batch_similarities = cosine_similarity(user_profile, batch_genre_probs)[0]
        batch_similar_indices = np.argsort(batch_similarities)[::-1]

        for i in batch_similar_indices:
            actual_idx = batch_indices[i]
            game_name = df.iloc[actual_idx]["name"]
            game_id = int(df.iloc[actual_idx]["AppID"])

            if game_name in owned_games or game_id in user_recent_games:
                continue

            candidates.append(
                {
                    "name": game_name,
                    "short_description": df.iloc[actual_idx]["short_description"],
                    "header_image": df.iloc[actual_idx].get("header_image", ""),
                    "appid": game_id,
                    "similarity": float(batch_similarities[i]),
                }
            )
            if len(candidates) >= candidate_pool_size:
                break

        del batch_tfidf, batch_genre_probs, batch_similarities
        gc.collect()

        if len(candidates) >= candidate_pool_size:
            break

    return candidates


def select_recommendations(candidates):
    """
    Select recommendations from candidates using weighted random sampling.

    Args:
        candidates (list): List of candidate game dictionaries with similarity scores

    Returns:
        list: List of selected game dictionaries without similarity scores
    """
    if len(candidates) <= 5:
        for game in candidates:
            game.pop("similarity", None)
        return candidates

    weights = [game["similarity"] for game in candidates]

    min_weight = min(weights)
    if min_weight < 0:
        weights = [w - min_weight + 0.01 for w in weights]

    selected_indices = []
    remaining_indices = list(range(len(candidates)))

    while len(selected_indices) < 5 and remaining_indices:
        remaining_weights = [weights[i] for i in remaining_indices]
        total_weight = sum(remaining_weights)
        normalized_weights = [w / total_weight for w in remaining_weights]

        selected_idx = random.choices(
            remaining_indices, weights=normalized_weights, k=1
        )[0]
        selected_indices.append(selected_idx)
        remaining_indices.remove(selected_idx)

    recommendations = [candidates[i] for i in selected_indices]

    for game in recommendations:
        game.pop("similarity", None)

    return recommendations


@app.post("/recommend/")
async def recommend_games(request: GameRequest):
    """Recommend games based on genre preferences using RandomForest classifier.
    Memory-optimized implementation that computes probabilities on-demand.
    Uses weighted random sampling to provide varied recommendations on each request.
    Prevents the same game from being recommended multiple times in a row."""
    try:
        # Initialize user data and clean old recommendations
        user_hash = get_user_hash(request)
        clean_old_recommendations()
        user_recent_games = set(recent_recommendations.get(user_hash, {}).keys())

        # Validate user's games
        owned_games = set(request.game_names)
        valid_games = df[df["name"].isin(owned_games)]

        if valid_games.empty:
            raise HTTPException(
                status_code=404, detail="No matching games found in dataset"
            )

        # Create user profile based on owned games
        user_profile = create_user_profile(valid_games)

        # Find candidate games for recommendation
        candidates = find_candidate_games(user_profile, owned_games, user_recent_games)

        # Select final recommendations using weighted random sampling
        recommendations = select_recommendations(candidates)

        # Update recommendation history
        update_recent_recommendations(user_hash, recommendations)

        return {"recommendations": recommendations}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
