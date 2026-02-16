# src/app.py
from flask import Flask, request, jsonify
import os
import sys
import json
import logging
from pathlib import Path
import threading
import argparse

import joblib
import pandas as pd

# --- Logging setup ---
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- Paths ---
MODEL_PATH = Path("model/voyage_model/1/model.pkl")
COLUMNS_PATH = Path("src/columns.json")

logger.info("[INFO] Starting Flask app... importing dependencies, please wait...")
logger.info("[INFO] Checking model path... %s", MODEL_PATH.resolve())

# --- Model load (non-fatal) ---
model = None
model_loaded = False
load_error = None

def try_load_model():
    """Attempt to load model; don't crash the app if unavailable."""
    global model, model_loaded, load_error
    if not MODEL_PATH.exists():
        load_error = FileNotFoundError(f"Model not found: {MODEL_PATH.resolve()}")
        logger.warning("⚠️ %s", load_error)
        return
    try:
        logger.info("📦 Loading pipeline from %s", MODEL_PATH)
        model = joblib.load(MODEL_PATH)
        model_loaded = True
        logger.info("✅ Pipeline loaded successfully!")
    except Exception as e:
        load_error = e
        logger.error("❌ Failed to load model: %s", e)

thread = threading.Thread(target=try_load_model, daemon=True)
thread.start()
thread.join(timeout=20)
if thread.is_alive():
    logger.warning("⚠️ Model loading timed out; continuing without model for now.")

# --- Load columns info (non-fatal) ---
required_cols = []
if COLUMNS_PATH.exists():
    try:
        with open(COLUMNS_PATH, "r") as f:
            columns_info = json.load(f)
        required_cols = columns_info.get("num_cols", []) + columns_info.get("cat_cols", [])
    except Exception as e:
        logger.warning("⚠️ Failed reading columns.json: %s", e)
else:
    logger.warning("⚠️ No columns.json found — predictions may be incomplete.")

# --- Routes ---
@app.get("/health")
def health():
    return jsonify(
        status="ok",
        port=app.config.get("APP_PORT"),
        model_loaded=model_loaded,
        load_error=str(load_error) if load_error else None
    ), 200

@app.get("/")
def home():
    return jsonify({"status": "Voyage Analytics API is running", "port": app.config.get("APP_PORT")})

@app.post("/predict")
def predict():
    if not model_loaded:
        return jsonify(error="Model not loaded", details=str(load_error) if load_error else None), 503
    try:
        data = request.get_json(force=True) or {}
        logger.info("Received data keys: %s", list(data.keys()))

        # Convert date strings -> year/month/day
        for prefix in ["date_flight", "date_hotel"]:
            if prefix in data and data[prefix]:
                dt = pd.to_datetime(data[prefix])
                data[f"{prefix}_year"] = int(dt.year)
                data[f"{prefix}_month"] = int(dt.month)
                data[f"{prefix}_day"] = int(dt.day)
                del data[prefix]

        # To DataFrame
        df = pd.DataFrame([data])

        # Ensure expected columns exist and order them
        for col in required_cols:
            if col not in df.columns:
                df[col] = None
        if required_cols:
            df = df[required_cols]

        # Predict
        preds = model.predict(df)
        preds = [max(0, float(p)) for p in preds]  # non-negative, JSON-friendly

        return jsonify({"prediction": preds})
    except Exception as e:
        logger.error("Prediction error: %s", e)
        return jsonify(error=str(e)), 400

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")  # loopback for Jenkins probe
    parser.add_argument("--port", type=int, default=int(os.getenv("FLASK_PORT", "5055")))
    args = parser.parse_args()

    app.config["APP_PORT"] = args.port
    logger.info("🚀 Starting Flask server at http://%s:%s/ ...", args.host, args.port)
    app.run(host=args.host, port=args.port, debug=False)
