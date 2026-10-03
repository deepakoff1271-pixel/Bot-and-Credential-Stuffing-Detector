import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold, cross_val_predict

df = pd.read_csv("features.csv")

FEATURES = [
    "total_requests", "failed_ratio", "unique_usernames",
    "avg_gap_sec", "gap_std_sec", "missing_language", "script_browser",
    "invalid_username_ratio", "other_failers_same_username",
]

# Every visit is predicted while its visitor is held out of training
model = RandomForestClassifier(n_estimators=100, random_state=42)
pred = cross_val_predict(
    model, df[FEATURES], df["label"], groups=df["visitor"], cv=GroupKFold(n_splits=5)
)

df["pred"] = pred
df["wrong"] = df["pred"] != df["label"]

summary = df.groupby("kind")["wrong"].agg(["sum", "count"])
summary.columns = ["wrong", "total"]
print(summary)
print()
print("Humans wrongly blocked:", int(((df["label"] == 0) & (df["pred"] == 1)).sum()))
print("Bots missed:           ", int(((df["label"] == 1) & (df["pred"] == 0)).sum()))
