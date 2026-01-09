import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score

C_LIST = [0.01, 0.1, 1.0, 10.0, 100.0]

def load(split):
    X = np.load(f"X_{split}.npy")
    y = np.load(f"y_{split}.npy")
    if X.shape[0] != y.shape[0]:
        raise ValueError(f"{split} mismatch: X={X.shape[0]} y={y.shape[0]}")
    return X, y

def pr_recall_f1(y, p, t):
    pred = (p >= t).astype(int)
    tp = ((pred == 1) & (y == 1)).sum()
    fp = ((pred == 1) & (y == 0)).sum()
    fn = ((pred == 0) & (y == 1)).sum()
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0
    return prec, rec, f1

def best_threshold_by_f1(y, p):
    best = (0.0, 0.5, 0.0, 0.0)  # f1, t, prec, rec
    for t in np.linspace(0.05, 0.95, 19):
        prec, rec, f1 = pr_recall_f1(y, p, float(t))
        if f1 > best[0]:
            best = (f1, float(t), prec, rec)
    return best  # f1, t, prec, rec

def main():
    X_train, y_train = load("train")
    X_val, y_val = load("val")
    X_test, y_test = load("test")

    best_model = None
    best_val_roc = -1.0

    for C in C_LIST:
        clf = LogisticRegression(C=C, class_weight="balanced", max_iter=2000, solver="liblinear")
        clf.fit(X_train, y_train)

        p_val = clf.predict_proba(X_val)[:, 1]
        roc_val = roc_auc_score(y_val, p_val) if len(np.unique(y_val)) > 1 else float("nan")
        pr_val = average_precision_score(y_val, p_val) if len(np.unique(y_val)) > 1 else float("nan")

        f1, t_star, p_star, r_star = best_threshold_by_f1(y_val, p_val)

        print("\nC =", C)
        print("VAL PR-AUC:", pr_val)
        print("VAL ROC-AUC:", roc_val)
        print("VAL best-F1:", f1, "T*:", t_star, "precision:", p_star, "recall:", r_star)

        if roc_val > best_val_roc:
            best_val_roc = roc_val
            best_model = (C, clf)

    bestC, bestclf = best_model

    p_val = bestclf.predict_proba(X_val)[:, 1]
    f1, t_star, p_star, r_star = best_threshold_by_f1(y_val, p_val)

    p_test = bestclf.predict_proba(X_test)[:, 1]
    roc_test = roc_auc_score(y_test, p_test) if len(np.unique(y_test)) > 1 else float("nan")
    pr_test = average_precision_score(y_test, p_test) if len(np.unique(y_test)) > 1 else float("nan")
    prec_t, rec_t, f1_t = pr_recall_f1(y_test, p_test, t_star)

    print("\nBEST C =", bestC)
    print("Chosen T* (from VAL):", t_star)
    print("TEST PR-AUC:", pr_test)
    print("TEST ROC-AUC:", roc_test)
    print("TEST @T* precision:", prec_t, "recall:", rec_t, "F1:", f1_t)

if __name__ == "__main__":
    main()
