import argparse
import pandas as pd
import json
import os
import joblib
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from features import prepare_X_y
from preprocess import prepare_dataset

def run_train(users_csv, flights_csv, hotels_csv=None):
    print("INFO:_main_:Merging datasets...")
    df = prepare_dataset(users_csv, flights_csv, hotels_csv)

    print("INFO:_main_:[INFO] Preparing features and target...")
    X, y, preprocessor, num_cols, cat_cols = prepare_X_y(df, target="price")

    print(f"INFO:_main_:[INFO] Using {len(num_cols)} numeric and {len(cat_cols)} categorical columns.")
    print(f"INFO:_main_:Training pipeline on {X.shape[0]} rows, {X.shape[1]} features")

    # --- Full pipeline with RandomForestRegressor ---
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            random_state=42
        ))
    ])

    pipeline.fit(X, y)

    # --- Save columns.json
    os.makedirs("src", exist_ok=True)
    columns_info = {"num_cols": num_cols, "cat_cols": cat_cols, "target": "price"}
    with open("src/columns.json", "w", encoding="utf-8") as f:
        json.dump(columns_info, f, indent=2)
    print("INFO:_main_:columns.json saved in src/")

    # --- Save full pipeline
    model_dir = "model/voyage_model/1"
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(pipeline, os.path.join(model_dir, "model.pkl"))
    print(f"INFO:_main_:Model saved at {model_dir}/model.pkl")

    # --- Also save copy under mlruns for test_model.py ---
    mlflow_dir = "mlruns/0/latest_model"
    os.makedirs(mlflow_dir, exist_ok=True)
    joblib.dump(pipeline, os.path.join(mlflow_dir, "model.pkl"))
    print(f"INFO:_main_:Model also saved in {mlflow_dir}/model.pkl")

    print("INFO:_main_:Training complete successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--users", required=True)
    parser.add_argument("--flights", required=True)
    parser.add_argument("--hotels", required=False)
    args = parser.parse_args()
    run_train(args.users, args.flights, args.hotels)
