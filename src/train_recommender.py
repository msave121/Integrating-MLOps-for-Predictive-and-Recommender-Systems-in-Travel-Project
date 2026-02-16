import argparse
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix, save_npz
from sklearn.decomposition import TruncatedSVD
import pickle

# --------------------------------------------------------
# Build item strings for flights & hotels
# --------------------------------------------------------

def build_items(flights_df, hotels_df):
    # Flights item format: "From → To — flightType"
    flights_df["item"] = (
        flights_df["from"] + " → " + flights_df["to"] + " — " + flights_df["flightType"]
    )

    # Hotels item format: "HotelName — Place"
    hotels_df["item"] = hotels_df["name"] + " — " + hotels_df["place"]

    return flights_df, hotels_df

# --------------------------------------------------------
# Main training function
# --------------------------------------------------------

def main(args):

    print("\nLoading datasets...")

    users = pd.read_csv(args.users)
    flights = pd.read_csv(args.flights)
    hotels = pd.read_csv(args.hotels)

    flights, hotels = build_items(flights, hotels)

    # Combine interactions from flights & hotels
    interactions = pd.concat([
        flights[["userCode", "item"]],
        hotels[["userCode", "item"]],
    ], ignore_index=True)

    print("Total interactions:", len(interactions))

    # Unique users and items
    user_list = sorted(interactions["userCode"].unique())
    item_list = sorted(interactions["item"].unique())

    print("Unique items:", len(item_list))
    print("Unique users:", len(user_list))

    # Create index maps
    user_to_idx = {u: i for i, u in enumerate(user_list)}
    item_to_idx = {it: i for i, it in enumerate(item_list)}

    # Build sparse matrix
    rows = interactions["userCode"].map(user_to_idx)
    cols = interactions["item"].map(item_to_idx)
    data = np.ones(len(interactions))

    matrix = csr_matrix(
        (data, (rows, cols)),
        shape=(len(user_list), len(item_list))
    )

    # Train SVD model
    svd = TruncatedSVD(n_components=50, random_state=42)
    svd.fit(matrix)

    # Save all models and maps
    with open("models/recommender_svd.pkl", "wb") as f:
        pickle.dump(svd, f)

    with open("models/user_to_idx.pkl", "wb") as f:
        pickle.dump(user_to_idx, f)

    with open("models/item_to_idx.pkl", "wb") as f:
        pickle.dump(item_to_idx, f)

    with open("models/user_list.pkl", "wb") as f:
        pickle.dump(user_list, f)

    with open("models/item_list.pkl", "wb") as f:
        pickle.dump(item_list, f)

    # SAVE actual matrix for API use
    save_npz("models/interactions.npz", matrix)

    print("\nSaved:")
    print("models/recommender_svd.pkl")
    print("models/user_to_idx.pkl")
    print("models/item_to_idx.pkl")
    print("models/user_list.pkl")
    print("models/item_list.pkl")
    print("models/interactions.npz")

    print("\nTraining completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--users")
    parser.add_argument("--flights")
    parser.add_argument("--hotels")
    args = parser.parse_args()
    main(args)
