# src/app.py
from flask import Flask, request, jsonify
import joblib
import pandas as pd
import logging
from pathlib import Path
import json
import sys

print("[INFO] Starting Flask app... importing dependencies, please wait...", flush=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

MODEL_PATH = Path("model/voyage_model/1/model.pkl")
COLUMNS_PATH = Path("src/columns.json")

print("[INFO] Checking model path...", flush=True)
if not MODEL_PATH.exists():
    print(f"[ERROR] ❌ Model not found: {MODEL_PATH}", flush=True)
    sys.exit(1)

logger.info(f"📦 Loading pipeline from {MODEL_PATH}")
try:
    model = joblib.load(MODEL_PATH)
    logger.info("✅ Pipeline loaded successfully!")
except Exception as e:
    logger.error(f"❌ Failed to load model: {e}")
    sys.exit(1)

# --- Load columns ---
print("[INFO] Loading column information...", flush=True)
if COLUMNS_PATH.exists():
    with open(COLUMNS_PATH, "r") as f:
        columns_info = json.load(f)
    required_cols = columns_info.get("num_cols", []) + columns_info.get("cat_cols", [])
else:
    logger.warning(f"⚠️ Columns file not found: {COLUMNS_PATH}")
    required_cols = []

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)
        logger.info(f"Received data keys: {list(data.keys())}")

        for prefix in ["date_flight", "date_hotel"]:
            if prefix in data:
                dt = pd.to_datetime(data[prefix])
                data[f"{prefix}_year"] = dt.year
                data[f"{prefix}_month"] = dt.month
                data[f"{prefix}_day"] = dt.day
                del data[prefix]

        df = pd.DataFrame([data])

        for col in required_cols:
            if col not in df.columns:
                df[col] = None
        df = df[required_cols]

        preds = model.predict(df)
        preds = [max(0, p) for p in preds]
        return jsonify({"prediction": preds})

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 400

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Voyage Analytics API is running"})

if __name__ == "__main__":
    print("[INFO] ✅ All dependencies imported successfully!", flush=True)
    print("[INFO] 🚀 Starting Flask on http://0.0.0.0:5055 ...", flush=True)
    app.run(host="0.0.0.0", port=5055, debug=True)
