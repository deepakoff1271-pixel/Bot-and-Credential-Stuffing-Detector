import pandas as pd

KNOWN_USERS = {"alice", "bob", "carol"}
WINDOW = pd.Timedelta(minutes=5)

# 1. Read the notebook
df = pd.read_json("logs/notebook.txt", lines=True)
df = df[df["visitor"] != "unknown"].copy()

# 2. Sort by visitor and time
df["time"] = pd.to_datetime(df["time"])
df = df.sort_values(["visitor", "time"])

# 3. Split each visitor's activity into visits (30 seconds of silence = new visit)
gap = df.groupby("visitor")["time"].diff().dt.total_seconds()
df["new_visit"] = gap.isna() | (gap > 30)
df["visit_id"] = df.groupby("visitor")["new_visit"].cumsum()
df["gap"] = df.groupby(["visitor", "visit_id"])["time"].diff().dt.total_seconds()

# All failed attempts, used for the cross-visitor clue
failed = df[~df["got_in"]][["visitor", "username_tried", "time"]]


def other_failers(visitor, g):
    """For the usernames this visit tried: how many OTHER visitors failed on the same
    username around the same time? Returns the highest count."""
    start, end = g["time"].min(), g["time"].max()
    best = 0
    for name in g["username_tried"].unique():
        near = failed[
            (failed["username_tried"] == name)
            & (failed["time"] >= start - WINDOW)
            & (failed["time"] <= end + WINDOW)
            & (failed["visitor"] != visitor)
        ]
        best = max(best, near["visitor"].nunique())
    return best


# 4. Describe each visit with clues
rows = []
for (visitor, visit_id), g in df.groupby(["visitor", "visit_id"]):
    language = g["language"].fillna("")
    rows.append({
        "visitor": visitor,
        "total_requests": len(g),
        "failed_ratio": round(1 - g["got_in"].mean(), 3),
        "unique_usernames": g["username_tried"].nunique(),
        "invalid_username_ratio": round((~g["username_tried"].isin(KNOWN_USERS)).mean(), 3),
        "other_failers_same_username": other_failers(visitor, g),
        "avg_gap_sec": round(g["gap"].mean(), 3) if g["gap"].notna().any() else 60.0,
        "gap_std_sec": round(g["gap"].std(), 3) if g["gap"].notna().sum() > 1 else 0.0,
        "missing_language": int((language == "").all()),
        "script_browser": int(g["browser"].str.contains("python", case=False).any()),
        "label": 1 if visitor.startswith("bot") else 0,
        "kind": visitor.rsplit("-", 1)[0],
    })

features = pd.DataFrame(rows)

# 5. Save and show
features.to_csv("features.csv", index=False)

print("Number of visits:", len(features))
print()
print(features.groupby("kind")[["other_failers_same_username", "invalid_username_ratio"]].mean().round(1))