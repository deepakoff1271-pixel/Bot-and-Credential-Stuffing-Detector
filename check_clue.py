import pandas as pd

df = pd.read_csv("features.csv")
print(df.groupby("kind")["other_failers_same_username"].agg(["mean", "min", "max"]).round(1))

