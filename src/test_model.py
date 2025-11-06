import os
import json
import pandas as pd
import joblib

def run_test():
    try:
        model_path = os.path.join("model", "voyage_model", "1", "model.pkl")
        print(f"[INFO] Model found at {model_path}")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at: {model_path}")

        print("[INFO] Testing model...")
        model = joblib.load(model_path)

        print(f"[INFO] Loading model from: {model_path}")

        columns_json = os.path.join("src", "columns.json")
        if not os.path.exists(columns_json):
            raise FileNotFoundError("columns.json not found in src/")

        with open(columns_json, "r", encoding="utf-8") as f:
            cols = json.load(f)

        expected_cols = cols["num_cols"] + cols["cat_cols"]
        print(f"[INFO] Loaded {len(expected_cols)} expected features.")

        # Create a test input dataframe
        sample = {
            "from": ["NYC"],
            "to": ["LAX"],
            "flightType": ["Economy"],
            "time": [360],
            "distance": [2450],
            "agency": ["XTravel"],
            "age": [30],
            "gender": ["Female"],
            "days": [5],
            "price_hotel": [120],
            "total": [800],
            "company": ["JetAir"],
            "name": ["Alice"],
            "name_hotel": ["Marriott"],
            "place": ["Los Angeles"]
        }

        test_df = pd.DataFrame(sample)
        test_df = test_df.reindex(columns=expected_cols, fill_value=0)

        print(f"[INFO] Prepared test data with {len(test_df.columns)} columns.")
        preds = model.predict(test_df)
        print(f"[INFO] Prediction output: {preds.tolist()}")

        print("[INFO] Model test completed successfully.")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to test model: {e}")
        return False

if __name__ == "__main__":
    run_test()
