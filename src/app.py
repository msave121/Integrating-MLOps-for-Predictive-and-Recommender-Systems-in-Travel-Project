# src/app.py
from flask import Flask, request, jsonify
import joblib
import pandas as pd
import logging
from pathlib import Path
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

MODEL_PATH = Path("model/voyage_model/1/model.pkl")
COLUMNS_PATH = Path("src/columns.json")

# --- Load pipeline ---
if not MODEL_PATH.exists():
    raise FileNotFoundError(f"❌ Model not found: {MODEL_PATH}")
logger.info(f"📦 Loading pipeline from {MODEL_PATH}")
model = joblib.load(MODEL_PATH)
logger.info("✅ Pipeline loaded successfully!")

# --- Load columns ---
if COLUMNS_PATH.exists():
    with open(COLUMNS_PATH, "r") as f:
        columns_info = json.load(f)
    required_cols = columns_info.get("num_cols", []) + columns_info.get("cat_cols", [])
else:
    required_cols = []

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)
        logger.info(f"Received data keys: {list(data.keys())}")

        # Convert date strings
        for prefix in ["date_flight", "date_hotel"]:
            if prefix in data:
                dt = pd.to_datetime(data[prefix])
                data[f"{prefix}_year"] = dt.year
                data[f"{prefix}_month"] = dt.month
                data[f"{prefix}_day"] = dt.day
                del data[prefix]

        # Convert to DataFrame
        df = pd.DataFrame([data])

        # Fill missing columns
        for col in required_cols:
            if col not in df.columns:
                df[col] = None
        df = df[required_cols]

        # Predict
        preds = model.predict(df)
        # Ensure non-negative
        preds = [max(0, p) for p in preds]
        return jsonify({"prediction": preds})

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 400

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Voyage Analytics API is running"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)