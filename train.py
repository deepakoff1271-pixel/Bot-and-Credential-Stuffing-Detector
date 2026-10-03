import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupShuffleSplit, GroupKFold, cross_val_score
from sklearn.metrics import confusion_matrix, classification_report

df = pd.read_csv("features.csv")

# The clues the model may see (NOT the visitor name, NOT the kind)
FEATURES = [
    "total_requests", "failed_ratio", "unique_usernames",
    "avg_gap_sec", "gap_std_sec", "missing_language", "script_browser",
    "invalid_username_ratio", "other_failers_same_username",
]

X = df[FEATURES]
y = df["label"]
groups = df["visitor"]  # rows from the same visitor stay together

# Split by visitor: 70% of visitors to learn from, 30% held back for the exam
splitter = GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=42)
train_idx, test_idx = next(splitter.split(X, y, groups))

X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

print("Training rows:", len(X_train), "| Test rows:", len(X_test))
print("Bots in test set:", int(y_test.sum()), "| Humans in test set:", int((y_test == 0).sum()))
print()

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
pred = model.predict(X_test)

print("Confusion matrix (rows = truth, columns = guess)")
print("            guessed human   guessed bot")
print(confusion_matrix(y_test, pred))
print()
print(classification_report(y_test, pred, target_names=["human", "bot"]))

# Which kinds of visitors did it get right?
results = df.iloc[test_idx][["kind"]].copy()
results["correct"] = (pred == y_test.values)
print("Correct answers by visitor type:")
print(results.groupby("kind")["correct"].agg(["sum", "count"]))
print()

# A fairer score: repeat the exam 5 times with different groups of visitors held back
cv_model = RandomForestClassifier(n_estimators=100, random_state=42)
scores = cross_val_score(cv_model, X, y, groups=groups, cv=GroupKFold(n_splits=5))
print("5-round exam scores:", scores.round(3))
print("Average:", round(scores.mean(), 3))
print()

importance = pd.Series(model.feature_importances_, index=FEATURES).sort_values(ascending=False)
print("Most useful clues:")
print(importance.round(3))

joblib.dump(model, "model.pkl")
print("\nModel saved as model.pkl")