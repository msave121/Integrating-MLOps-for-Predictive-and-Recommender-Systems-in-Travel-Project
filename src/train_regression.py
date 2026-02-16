import argparse
import pandas as pd
import json
import os
import joblib
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from features import prepare_X_y
from preprocess import prepare_dataset

import mlflow
import mlflow.sklearn


def run_train(users_csv, flights_csv, hotels_csv=None):
    print("INFO: [MLflow] Starting model training...")

    # --- Connect to your MLflow tracking server ---
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("Voyage Analytics Model")

    # --- Start MLflow run ---
    with mlflow.start_run(run_name="RandomForest_Training"):

        print("INFO: Merging datasets...")
        df = prepare_dataset(users_csv, flights_csv, hotels_csv)

        print("INFO: Preparing features and target...")
        X, y, preprocessor, num_cols, cat_cols = prepare_X_y(df, target="price")

        print(f"INFO: Using {len(num_cols)} numeric and {len(cat_cols)} categorical columns.")
        print(f"INFO: Training pipeline on {X.shape[0]} rows, {X.shape[1]} features")

        # --- Model setup ---
        params = {
            "n_estimators": 200,
            "max_depth": 10,
            "random_state": 42
        }

        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", RandomForestRegressor(**params))
        ])

        # --- Log model parameters ---
        mlflow.log_params(params)

        # --- Train model ---
        pipeline.fit(X, y)

        # --- Save columns.json ---
        os.makedirs("src", exist_ok=True)
        columns_info = {"num_cols": num_cols, "cat_cols": cat_cols, "target": "price"}
        with open("src/columns.json", "w", encoding="utf-8") as f:
            json.dump(columns_info, f, indent=2)
        print("INFO: columns.json saved in src/")

        # --- Save model locally ---
        model_dir = "model/voyage_model/1"
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, "model.pkl")
        joblib.dump(pipeline, model_path)
        print(f"INFO: Model saved at {model_path}")

        # --- Log model to MLflow ---
        mlflow.sklearn.log_model(
            sk_model=pipeline,
            artifact_path="model",
            registered_model_name="VoyagePricePredictor"
        )

        print("INFO: Model logged to MLflow successfully.")

        # --- Example metric (just for demo) ---
        r2 = pipeline.score(X, y)
        mlflow.log_metric("r2_score", r2)
        print(f"INFO: Logged metric r2_score = {r2:.4f}")

    print("✅ Training complete and tracked with MLflow!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--users", required=True)
    parser.add_argument("--flights", required=True)
    parser.add_argument("--hotels", required=False)
    args = parser.parse_args()
    run_train(args.users, args.flights, args.hotels)
