# src/recommender_api.py
from fastapi import FastAPI
import numpy as np
import pickle
from scipy.sparse import load_npz

app = FastAPI()

print("Loading recommender model...")

with open("models/recommender_svd.pkl", "rb") as f:
    svd = pickle.load(f)

with open("models/user_to_idx.pkl", "rb") as f:
    user_to_idx = pickle.load(f)

with open("models/item_list.pkl", "rb") as f:
    item_list = pickle.load(f)

with open("models/interactions.npz", "rb") as f:
    interaction_matrix = load_npz(f)

# Precompute embeddings
user_embeddings = svd.transform(interaction_matrix)
item_embeddings = svd.components_.T

print("Model loaded successfully!")

@app.get("/recommend")
def recommend(user_id: int, top_k: int = 5):
    if user_id not in user_to_idx:
        return {"flight_recommendations": [], "hotel_recommendations": []}

    u_idx = user_to_idx[user_id]

    scores = user_embeddings[u_idx] @ item_embeddings.T
    sorted_idx = np.argsort(scores)[::-1]

    # split items
    flight_items = []
    hotel_items = []

    for idx in sorted_idx:
        item = item_list[idx]

        if "→" in item:    # flight
            flight_items.append({"item": item, "score": float(scores[idx])})
        else:              # hotel
            hotel_items.append({"item": item, "score": float(scores[idx])})

        if len(flight_items) >= top_k and len(hotel_items) >= top_k:
            break

    return {
        "user_id": user_id,
        "flight_recommendations": flight_items[:top_k],
        "hotel_recommendations": hotel_items[:top_k],
    }
