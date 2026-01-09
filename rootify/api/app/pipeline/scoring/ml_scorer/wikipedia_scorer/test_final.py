import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import roc_auc_score, average_precision_score
from collections import Counter

T_JUNK = 0.6

X_test = np.load("X_test.npy")
y_test = np.load("y_test.npy")

test_df = pd.read_csv("wikipedia_testing.csv")
bucket_test = test_df["bucket"].values

clf = joblib.load("logreg_minilm_c10.joblib")
p_test = clf.predict_proba(X_test)[:, 1]

print("test ROC-AUC:", roc_auc_score(y_test, p_test))
print("test PR-AUC:", average_precision_score(y_test, p_test))

pred = (p_test >= T_JUNK).astype(int)

tp = np.sum((pred == 1) & (y_test == 1))
fp = np.sum((pred == 1) & (y_test == 0))
fn = np.sum((pred == 0) & (y_test == 1))

precision = tp / (tp + fp) if (tp + fp) else 0.0
recall = tp / (tp + fn) if (tp + fn) else 0.0

fp_buckets = bucket_test[(pred == 1) & (y_test == 0)]
fp_counts = Counter(fp_buckets)

print(f"@T_junk={T_JUNK} predicted positives:", int(tp + fp))
print("precision:", round(precision, 3), "recall:", round(recall, 3))
print("false positives by bucket:", dict(fp_counts))
