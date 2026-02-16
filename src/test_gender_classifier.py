import mlflow
import pickle
import pandas as pd
import numpy as np

print("\n📌 Loading model from MLflow Registry...\n")

# ---------------------------------------------------------------------
# 1️⃣ Load the model directly from your real artifact path
# ---------------------------------------------------------------------
model_path = r"mlruns/634045032032732958/models/m-fd5a4e5e6c614f9185d7f2ac2a36cd1f/artifacts"
model = mlflow.pyfunc.load_model(model_path)

print("✔ Model loaded successfully!\n")

# ---------------------------------------------------------------------
# 2️⃣ Load encoders
# ---------------------------------------------------------------------
gender_map = pickle.load(open("encoders/gender_encoder.pkl", "rb"))
name_vectorizer = pickle.load(open("encoders/name_vectorizer.pkl", "rb"))

# Reverse map: 0→male , 1→female
gender_inv = {v: k for k, v in gender_map.items()}

# ---------------------------------------------------------------------
# 3️⃣ Test samples
# ---------------------------------------------------------------------
samples = [
    ("Joseph Holsten", 37, "female"),
    ("Emma Watson", 29, "female"),
    ("Anita Smothers", 48, "female"),
]

print("🎯 Predictions:\n")
print(f"{'Name':20} | {'Predicted':10} | {'Actual':8} | Result")
print("-" * 60)

# ---------------------------------------------------------------------
# 4️⃣ Predict loop
# ---------------------------------------------------------------------
for name, age, actual in samples:

    first_name = name.split()[0]

    # 🔥 FIX: batch transform
    v_name = name_vectorizer.transform_batch([first_name])

    # final input vector → concatenate name_vec + age
    X = np.hstack([v_name, np.array([[age]])])

    pred = model.predict(X)[0]
    predicted_gender = gender_inv[pred]

    result = "✅ Correct" if predicted_gender == actual else "❌ Wrong"

    print(f"{name:20} | {predicted_gender:10} | {actual:8} | {result}")
