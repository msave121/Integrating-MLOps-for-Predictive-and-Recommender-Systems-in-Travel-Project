import pandas as pd

df = pd.read_csv("data/users.csv")

# Remove incorrect / unknown genders
df = df[df["gender"].isin(["male", "female"])]

# Reset index
df = df.reset_index(drop=True)

df.to_csv("data/users_cleaned.csv", index=False)

print("✔ Cleaned file saved to data/users_cleaned.csv")
