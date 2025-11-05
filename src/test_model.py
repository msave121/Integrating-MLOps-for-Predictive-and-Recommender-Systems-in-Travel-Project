import os
import joblib
import pandas as pd
import sys

def load_model():
    """
    Try to load the latest trained model from the Jenkins workspace.
    """
    model_path = os.path.join("mlruns", "0", "latest_model", "model.pkl")
    if not os.path.exists(model_path):
        print(f"[ERROR] Model not found at: {model_path}")
        print("[HINT] Run the '🏗️ Build Model' stage first to train and save the model.")
        sys.exit(1)

    try:
        print(f"[INFO] Loading model from: {model_path}")
        model = joblib.load(model_path)
        print("[INFO] ✅ Model successfully loaded.")
        return model
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        sys.exit(1)


def test_model(model):
    """
    Basic smoke test to ensure the model can make predictions.
    """
    try:
        # Create dummy data with same structure expected by pipeline
        sample = pd.DataFrame({
            "userAge": [32],
            "userIncome": [70000],
            "flightDistance": [1500],
            "hotelRating": [4],
            "numDays": [5],
            "isHolidaySeason": [1],
            "flightClass": ["Economy"],
            "hotelLocation": ["CityCenter"],
            "userGender": ["Female"],
            "tripType": ["Leisure"]
        })

        print("[INFO] Running prediction on sample input...")
        preds = model.predict(sample)
        print(f"[INFO] ✅ Model prediction successful! Predicted price: {preds[0]:.2f}")

    except Exception as e:
        print(f"[ERROR] Model test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("[INFO] Testing model...")
    model = load_model()
    test_model(model)
    print("[INFO] 🎯 Model test completed successfully.")
