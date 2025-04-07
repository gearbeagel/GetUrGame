from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np

MODEL_DIR = "./model"
df = pd.read_csv(f"{MODEL_DIR}/games_may2024_cleaned.csv")
tfidf = joblib.load(f"{MODEL_DIR}/tfidf.pkl")
nn_model = joblib.load(f"{MODEL_DIR}/nearest_neighbors.pkl")

tfidf_matrix = tfidf.transform(df["combined_features"])

app = FastAPI()


class GameRequest(BaseModel):
    game_names: list[str]


@app.post("/recommend/")
async def recommend_games(request: GameRequest):
    """Recommend games based on similar games using NearestNeighbors."""
    try:
        owned_games = set(request.game_names)
        valid_games = df[df["name"].isin(owned_games)]

        if valid_games.empty:
            raise HTTPException(
                status_code=404, detail="No matching games found in dataset"
            )

        owned_indices = valid_games.index.tolist()
        owned_vectors = tfidf_matrix[owned_indices]

        all_indices = set()
        for vec in owned_vectors:
            distances, indices = nn_model.kneighbors(
                vec, n_neighbors=100
            )  # increase pool
            all_indices.update(indices[0])

        all_indices = list(all_indices)
        np.random.shuffle(all_indices)  # randomize order

        recommendations = []
        for i in all_indices:
            game_name = df.iloc[i]["name"]
            if game_name not in owned_games:
                recommendations.append(
                    {
                        "name": df.iloc[i]["name"],
                        "short_description": df.iloc[i]["short_description"],
                        "header_image": df.iloc[i].get("header_image", ""),
                        "appid": int(df.iloc[i]["AppID"]),
                    }
                )
            if len(recommendations) == 5:
                break

        return {"recommendations": recommendations}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
