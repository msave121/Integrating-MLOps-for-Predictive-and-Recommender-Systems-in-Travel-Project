import pandas as pd
import os
import pickle
from sklearn.preprocessing import LabelEncoder

# Load data
data = pd.read_csv("data/users_cleaned.csv")[["name", "company", "gender"]]

# Create encoders
le_name = LabelEncoder()
le_company = LabelEncoder()
le_gender = LabelEncoder()

# Fit encoders
data["name_encoded"] = le_name.fit_transform(data["name"])
data["company_encoded"] = le_company.fit_transform(data["company"])
data["gender_encoded"] = le_gender.fit_transform(data["gender"])

# Create folder if not exists
os.makedirs("encoders", exist_ok=True)

# Save encoders
pickle.dump(le_name, open("encoders/name_encoder.pkl", "wb"))
pickle.dump(le_company, open("encoders/company_encoder.pkl", "wb"))
pickle.dump(le_gender, open("encoders/gender_encoder.pkl", "wb"))

print("\n✔ Encoders saved successfully!")
print("📁 encoders/name_encoder.pkl")
print("📁 encoders/company_encoder.pkl")
print("📁 encoders/gender_encoder.pkl")
