import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score
import joblib

X_train = np.load("X_train.npy")
y_train = np.load("y_train.npy")

X_val = np.load("X_val.npy")
y_val = np.load("y_val.npy")

clf = LogisticRegression(
    class_weight="balanced",
    max_iter=1000,
    solver="liblinear",
)

clf.fit(X_train, y_train)

p_val = clf.predict_proba(X_val)[:, 1]

roc = roc_auc_score(y_val, p_val)
pr = average_precision_score(y_val, p_val)

import pandas as pd
import numpy as np
from collections import Counter

val_df = pd.read_csv("wikipedia_validation.csv")

bucket_val = val_df["bucket"].values
y_val = val_df["label"].values

import numpy as np
from collections import Counter
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

T_JUNK = 0.6
C_VALUES = [0.01, 0.1, 1.0, 10.0, 100.0]

results = []

for C in C_VALUES:
    clf = LogisticRegression(
        C=C,
        class_weight="balanced",
        max_iter=2000,
        solver="liblinear",
    )
    clf.fit(X_train, y_train)

    p_val = clf.predict_proba(X_val)[:, 1]

    pr = average_precision_score(y_val, p_val)
    roc = roc_auc_score(y_val, p_val)

    pred = (p_val >= T_JUNK).astype(int)
    tp = np.sum((pred == 1) & (y_val == 1))
    fp = np.sum((pred == 1) & (y_val == 0))
    fn = np.sum((pred == 0) & (y_val == 1))
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0

    fp_buckets = bucket_val[(pred == 1) & (y_val == 0)]
    fp_counts = Counter(fp_buckets)

    print("\nC =", C)
    print("PR-AUC:", pr)
    print("ROC-AUC:", roc)
    print(f"@T_junk={T_JUNK} precision:", precision, "recall:", recall)
    print("FP buckets:", dict(fp_counts))

    results.append((C, pr, precision, recall, dict(fp_counts)))

