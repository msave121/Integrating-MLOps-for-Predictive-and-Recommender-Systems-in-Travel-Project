# src/app.py
from flask import Flask, request, jsonify
import joblib
import pandas as pd
import logging
from pathlib import Path
import json
import sys
import threading
import argparse

# --- Logging setup ---
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

MODEL_PATH = Path("model/voyage_model/1/model.pkl")
COLUMNS_PATH = Path("src/columns.json")

logger.info("[INFO] Starting Flask app... importing dependencies, please wait...")
logger.info("[INFO] Checking model path...")

if not MODEL_PATH.exists():
    logger.error(f"❌ Model not found: {MODEL_PATH.resolve()}")
    sys.exit(1)

logger.info(f"📦 Loading pipeline from {MODEL_PATH}")

model = None
load_error = None

def load_model():
    global model, load_error
    try:
        model = joblib.load(MODEL_PATH)
    except Exception as e:
        load_error = e

# Run model loading in a separate thread with timeout
thread = threading.Thread(target=load_model)
thread.start()
thread.join(timeout=20)

if thread.is_alive():
    logger.error("❌ Model loading timed out (possible hang or large file).")
    sys.exit(1)

if load_error:
    logger.error(f"❌ Failed to load model: {load_error}")
    sys.exit(1)

logger.info("✅ Pipeline loaded successfully!")

# --- Load columns info ---
if COLUMNS_PATH.exists():
    with open(COLUMNS_PATH, "r") as f:
        columns_info = json.load(f)
    required_cols = columns_info.get("num_cols", []) + columns_info.get("cat_cols", [])
else:
    required_cols = []
    logger.warning("⚠️ No columns.json found — predictions may be incomplete.")

# --- Routes ---
@app.get("/health")
def health():
    return jsonify(status="ok", port=app.config.get("APP_PORT", None))

@app.get("/")
def home():
    return jsonify({"status": "Voyage Analytics API is running", "port": app.config.get("APP_PORT", None)})

@app.post("/predict")
def predict():
    try:
        data = request.get_json(force=True)
        logger.info(f"Received data keys: {list(data.keys())}")

        # Convert date strings -> year/month/day
        for prefix in ["date_flight", "date_hotel"]:
            if prefix in data and data[prefix]:
                dt = pd.to_datetime(data[prefix])
                data[f"{prefix}_year"] = int(dt.year)
                data[f"{prefix}_month"] = int(dt.month)
                data[f"{prefix}_day"] = int(dt.day)
                del data[prefix]

        # Convert to DataFrame
        df = pd.DataFrame([data])

        # Ensure expected columns exist and order them
        for col in required_cols:
            if col not in df.columns:
                df[col] = None
        if required_cols:
            df = df[required_cols]

        # Predict
        preds = model.predict(df)
        preds = [max(0, float(p)) for p in preds]  # prevent negatives, ensure JSON-serializable

        return jsonify({"prediction": preds})

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5055)
    args = parser.parse_args()

    app.config["APP_PORT"] = args.port
    logger.info(f"🚀 Starting Flask server at http://{args.host}:{args.port}/ ...")
    app.run(host=args.host, port=args.port, debug=False)
