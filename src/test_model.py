# src/test_model.py
import mlflow
import sys

def test_model():
    print("[INFO] Testing model...")

    try:
        model = mlflow.pyfunc.load_model("models:/flight_price_model/Production")
        print("[INFO] Model loaded successfully.")
    except Exception as e:
        print(f"[ERROR] Could not load model: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_model()
    print("[INFO] Test completed successfully ✅")
