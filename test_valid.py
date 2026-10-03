import pandas as pd
import joblib

df = pd.read_csv("features.csv")

FEATURES = [
    "total_requests", "failed_ratio", "unique_usernames",
    "avg_gap_sec", "gap_std_sec", "missing_language", "script_browser",
    "invalid_username_ratio",
]

model = joblib.load("model_v3.pkl")

valid = df[df["kind"] == "bot-valid"]
pred = model.predict(valid[FEATURES])

print("Valid-username bot visits:", len(valid))
print("Caught as bot:", int(pred.sum()))
print("Missed:", int((pred == 0).sum()))
print("Catch rate:", round(pred.mean(), 3))