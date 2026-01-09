import numpy as np
import joblib
import json
from sklearn.linear_model import LogisticRegression

C_FINAL = 100.0
T_FINAL = 0.5

X_train = np.load("X_train.npy")
y_train = np.load("y_train.npy")
X_val = np.load("X_val.npy")
y_val = np.load("y_val.npy")

X_final = np.vstack([X_train, X_val])
y_final = np.concatenate([y_train, y_val])

final_clf = LogisticRegression(
    C=C_FINAL,
    class_weight="balanced",
    max_iter=2000,
    solver="liblinear",
)
final_clf.fit(X_final, y_final)
print("final model trained")

joblib.dump(final_clf, "logreg_direction_pair_c100.joblib")
print("saved model")

meta = {
    "task": "direction_pair_choice",
    "encoder": "all-MiniLM-L6-v2",
    "embedding_dim": 384,
    "pair_feature_dim": 1536,
    "pair_features": ["embA", "embB", "embA-embB", "embA*embB"],
    "classifier": "logistic_regression",
    "C": C_FINAL,
    "class_weight": "balanced",
    "solver": "liblinear",
    "T_choice": T_FINAL,
    "label_semantics": {
        "y=1": "A_is_correct_direction",
        "y=0": "B_is_correct_direction",
    },
}

with open("logreg_direction_pair_c100.meta.json", "w") as f:
    json.dump(meta, f, indent=2)

print("saved metadata")
print(X_final.shape)

reloaded = joblib.load("logreg_direction_pair_c100.joblib")
p = reloaded.predict_proba(X_val[:5])[:, 1]
print("reload ok, sample probs:", p)
