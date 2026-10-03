import pandas as pd
import joblib

df = pd.read_csv("features.csv")

FEATURES = [
    "total_requests", "failed_ratio", "unique_usernames",
    "avg_gap_sec", "gap_std_sec", "missing_language", "script_browser",
]

model = joblib.load("model_v2.pkl")

for kind in ["human-giveup", "human-wrongname", "human-office"]:
    group = df[df["kind"] == kind]
    pred = model.predict(group[FEATURES])
    print(f"{kind}: {len(group)} visits, wrongly flagged as bot: {int(pred.sum())}")

    