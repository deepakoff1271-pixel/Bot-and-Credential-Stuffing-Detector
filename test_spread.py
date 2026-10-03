import pandas as pd
import joblib

df = pd.read_csv("features.csv")

FEATURES = [
    "total_requests", "failed_ratio", "unique_usernames",
    "avg_gap_sec", "gap_std_sec", "missing_language", "script_browser",
]

model = joblib.load("model_v1.pkl")

spread = df[df["kind"] == "bot-spread"]
pred = model.predict(spread[FEATURES])

print("Spread-bot visits:", len(spread))
print("Caught as bot:    ", int(pred.sum()))
print("Missed (called human):", int((pred == 0).sum()))
print("Catch rate:", round(pred.mean(), 3))