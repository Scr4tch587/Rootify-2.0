import numpy as np
import joblib
from sklearn.metrics import roc_auc_score, average_precision_score

T = 0.5

X_test = np.load("X_test.npy")
y_test = np.load("y_test.npy")

clf = joblib.load("logreg_direction_pair_c100.joblib")
p_test = clf.predict_proba(X_test)[:, 1]

print("test ROC-AUC:", roc_auc_score(y_test, p_test))
print("test PR-AUC:", average_precision_score(y_test, p_test))

pred = (p_test >= T).astype(int)

tp = np.sum((pred == 1) & (y_test == 1))
fp = np.sum((pred == 1) & (y_test == 0))
fn = np.sum((pred == 0) & (y_test == 1))

precision = tp / (tp + fp) if (tp + fp) else 0.0
recall = tp / (tp + fn) if (tp + fn) else 0.0

print(f"@T_choice={T} predicted A-correct:", int(tp + fp))
print("precision:", round(precision, 3), "recall:", round(recall, 3))
