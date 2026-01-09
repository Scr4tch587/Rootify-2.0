import numpy as np

X_train = np.load("X_train.npy")
y_train = np.load("y_train.npy")
X_val = np.load("X_val.npy")
y_val = np.load("y_val.npy")

X_final = np.vstack([X_train, X_val])
y_final = np.concatenate([y_train, y_val])
from sklearn.linear_model import LogisticRegression

final_clf = LogisticRegression(
    C=10.0,
    class_weight="balanced",
    max_iter=2000,
    solver="liblinear",
)
final_clf.fit(X_final, y_final)
print("final model trained")

import joblib

joblib.dump(final_clf, "logreg_minilm_c10.joblib")
print("saved model")

import json

meta = {
    "encoder": "all-MiniLM-L6-v2",
    "embedding_dim": 384,
    "classifier": "logistic_regression",
    "C": 10.0,
    "class_weight": "balanced",
    "solver": "liblinear",
    "T_junk": 0.6,
    "strength_bands": [
        {"min_p": 0.6, "label": "weak"},
        {"min_p": 0.7, "label": "strong"},
        {"min_p": 0.85, "label": "very_strong"},
    ],
}

with open("logreg_minilm_c10.meta.json", "w") as f:
    json.dump(meta, f, indent=2)

print("saved metadata")

print(X_final.shape)
reloaded = joblib.load("logreg_minilm_c10.joblib")
p = reloaded.predict_proba(X_val[:5])[:, 1]
print("reload ok, sample probs:", p)
