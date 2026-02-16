import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
import pickle
import os
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from name_vectorizer import NameVectorizer

# Load dataset
df = pd.read_csv("data/users_cleaned.csv")

# Extract first name only (important!)
df["first_name"] = df["name"].apply(lambda x: x.split()[0])

# Setup NameVectorizer
vectorizer = NameVectorizer()
X_name = vectorizer.transform_batch(df["first_name"][:1000])


# Prepare additional features
X_age = df["age"].values.reshape(-1, 1)

# Combine name vector + age
X = np.hstack([X_name, X_age])

# Encode target (gender)
gender_map = {"male": 0, "female": 1}
y = df["gender"].map(gender_map).values

# Save gender encoder
os.makedirs("encoders", exist_ok=True)
pickle.dump(gender_map, open("encoders/gender_encoder.pkl", "wb"))
pickle.dump(vectorizer, open("encoders/name_vectorizer.pkl", "wb"))

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, shuffle=True
)

# High-performance classifier
model = XGBClassifier(
    n_estimators=50,   # TEMP
    max_depth=6,
    learning_rate=0.1,
    eval_metric="logloss",
    verbosity=1
)


# Train
model.fit(X_train, y_train)

# Evaluate
accuracy = model.score(X_test, y_test)

# Log with MLflow
mlflow.set_experiment("gender-classifier-v2")

with mlflow.start_run():
    mlflow.log_metric("accuracy", accuracy)
    mlflow.sklearn.log_model(model, "model")

print(f"✔ Training complete! Accuracy = {accuracy:.4f}")
