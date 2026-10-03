import pandas as pd
import joblib

df = pd.read_csv("features.csv")

FEATURES = [
    "total_requests", "failed_ratio", "unique_usernames",
    "avg_gap_sec", "gap_std_sec", "missing_language", "script_browser",
    "invalid_username_ratio", "other_failers_same_username",
]

model = joblib.load("model_v4.pkl")

small = df[df["kind"] == "bot-small"]
pred = model.predict(small[FEATURES])

print("Small attack:", len(small), "visits")
print("Caught as bot:", int(pred.sum()))
print("Missed:", int((pred == 0).sum()))
print("Catch rate:", round(pred.mean(), 3))
print()
print("Average 'other failers' clue for this attack:",
      round(small["other_failers_same_username"].mean(), 1))
      