# src/test_model.py
import os
import joblib
import pandas as pd
import json

def test_model():
    print("[INFO] Testing model...")

    # --- Locate model ---
    jenkins_model_path = os.path.join("mlruns", "0", "latest_model", "model.pkl")
    local_model_path = os.path.join("model", "voyage_model", "1", "model.pkl")

    model_path = jenkins_model_path if os.path.exists(jenkins_model_path) else local_model_path
    if not os.path.exists(model_path):
        print(f"[ERROR] Model not found at: {model_path}")
        print("[HINT] Run the '🏗️ Build Model' stage first to train and save the model.")
        exit(1)

    print(f"[INFO] Loading model from: {model_path}")
    model = joblib.load(model_path)

    # --- Load column info to ensure matching schema ---
    columns_path = os.path.join("src", "columns.json")
    if os.path.exists(columns_path):
        with open(columns_path, "r") as f:
            columns_info = json.load(f)
        expected_features = columns_info.get("num_cols", []) + columns_info.get("cat_cols", [])
        print(f"[INFO] Loaded {len(expected_features)} expected features.")
    else:
        print("[WARN] columns.json not found — using manual column list.")
        expected_features = [
            "travelCode", "userCode", "from", "to", "flightType", "time", "distance", "agency",
            "name", "age", "gender", "company", "place", "days", "price_hotel",
            "name_hotel", "total"
        ]

    # --- Create test input with all required columns ---
    test_row = {
        "travelCode": "T001",
        "userCode": "U001",
        "from": "NYC",
        "to": "LAX",
        "flightType": "Economy",
        "time": 360,
        "distance": 2450,
        "agency": "XTravel",
        "date_flight": "2025-10-20",
        "name": "John Doe",
        "age": 30,
        "gender": "Male",
        "company": "TestCorp",
        "place": "New York",
        "days": 10,
        "price_hotel": 200.0,
        "name_hotel": "HotelX",
        "total": 500.0
    }

    # Convert to DataFrame and align columns
    df = pd.DataFrame([test_row])
    for col in expected_features:
        if col not in df.columns:
            df[col] = None
    df = df[expected_features]

    print(f"[INFO] Prepared test data with {df.shape[1]} columns.")

    # --- Run prediction ---
    try:
        prediction = model.predict(df)
        print(f"[SUCCESS] ✅ Model test prediction: {prediction[0]:.2f}")
    except Exception as e:
        print(f"[ERROR] Failed to test model: {e}")
        exit(1)

    print("[INFO] Model test completed successfully!")

if __name__ == "__main__":
    test_model()
