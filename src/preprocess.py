# src/preprocess.py
import pandas as pd

def prepare_dataset(users_path, flights_path, hotels_path=None):
    """
    Load CSVs and merge into a single DataFrame.
    Keeps logging prints so you know what's happening.
    """
    print(f"[INFO] Loading users from {users_path}")
    users = pd.read_csv(users_path)
    print(f"[INFO] Loading flights from {flights_path}")
    flights = pd.read_csv(flights_path)

    hotels = None
    if hotels_path:
        print(f"[INFO] Loading hotels from {hotels_path}")
        hotels = pd.read_csv(hotels_path)

    # merge flights + users
    print("[INFO] Merging flights + users")
    df = flights.merge(users, left_on="userCode", right_on="code", how="left", suffixes=("", "_user"))

    # merge hotels if provided
    if hotels is not None:
        print("[INFO] Merging hotels")
        df = df.merge(hotels, on=["travelCode", "userCode"], how="left", suffixes=("", "_hotel"))

    # try to coerce common numeric columns (safe)
    for col in ("price", "distance", "time", "total"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # attempt to parse date columns (non-fatal)
    for col in list(df.columns):
        if "date" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
            except Exception:
                pass

    print(f"[INFO] Merged dataframe shape: {df.shape}")
    return df
