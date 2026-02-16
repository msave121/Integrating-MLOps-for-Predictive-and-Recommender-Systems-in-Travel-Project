import pandas as pd

hotels = pd.read_csv("data/hotels.csv")
flights = pd.read_csv("data/flights.csv")

items = pd.concat([
    hotels['name'].astype(str),
    flights['from'].astype(str) + " → " + flights['to'].astype(str) + " — " + flights['flightType']
])

print("Unique item count:", items.nunique())
