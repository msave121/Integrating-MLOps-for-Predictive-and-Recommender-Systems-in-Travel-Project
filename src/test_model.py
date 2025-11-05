# src/test_model.py
import os
import joblib
import pandas as pd

def test_model():
    print("[INFO] Testing model...")

    # Define both possible model paths
    jenkins_model_path = os.path.join("mlruns", "0", "latest_model", "model.pkl")
    local_model_path = os.path.join("model", "voyage_model", "1", "model.pkl")

    # Choose whichever exists
    if os.path.exists(jenkins_model_path):
        model_path = jenkins_model_path
    elif os.path.exists(local_model_path):
        model_path = local_model_path
    else:
        print(f"[ERROR] Model not found at either:\n - {jenkins_model_path}\n - {local_model_path}")
        print("[HINT] Run the '🏗️ Build Model' stage first to train and save the model.")
        exit(1)

    print(f"[INFO] Loading model from: {model_path}")
    model = joblib.load(model_path)

    # --- Dummy test data for validation ---
    # (You can replace this with a small real dataset if desired)
    sample = pd.DataFrame({
        "user_id": [1],
        "origin": ["DEL"],
        "destination": ["BOM"],
        "days_until_flight": [10],
        "airline": ["IndiGo"],
        "num_hotels_visited": [5]
    })

    # Try prediction
    try:
        prediction = model.predict(sample)
        print(f"[SUCCESS] Model test prediction: {prediction[0]:.2f}")
    except Exception as e:
        print(f"[ERROR] Failed to test model: {e}")
        exit(1)

    print("[INFO] ✅ Model test completed successfully!")


if __name__ == "__main__":
    test_model()
