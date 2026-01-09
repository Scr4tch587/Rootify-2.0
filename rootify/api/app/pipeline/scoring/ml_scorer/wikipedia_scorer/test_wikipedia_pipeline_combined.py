import re
import json
import numpy as np
import pandas as pd
import joblib
from sentence_transformers import SentenceTransformer
from sklearn.metrics import roc_auc_score, average_precision_score
from collections import Counter

# ==== paths (edit locally) ====
STAGE1_MODEL_PATH = "logreg_minilm_c10.joblib"
STAGE1_META_PATH = "logreg_minilm_c10.meta.json"

STAGE2_MODEL_PATH = "logreg_direction_pair_c100.joblib"
STAGE2_META_PATH = "logreg_direction_pair_c100.meta.json"

# Stage 1 feature arrays + aligned dataframe for bucket info
X_TEST_PATH = "X_test.npy"
Y_TEST_PATH = "y_test.npy"
TEST_DF_PATH = "wikipedia_testing.csv"

# Stage 2 embedding config (should match meta)
ENCODER_NAME_FALLBACK = "all-MiniLM-L6-v2"
BATCH_SIZE = 64

RX = re.compile(
    r"\[SUBJECT\]\s*(.*?)\s*\[CANDIDATE\]\s*(.*?)\s*\[CONTEXT\]\s*(.*)$",
    re.DOTALL,
)

REAL_BUCKETS = {"positive", "reverse_direction"}

def load_json(path: str):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def parse_input_text(s: str):
    m = RX.match(str(s))
    if not m:
        return None
    subj = m.group(1).strip()
    cand = m.group(2).strip()
    ctx = m.group(3).strip()
    if not subj or not cand or not ctx:
        return None
    return subj, cand, ctx

def swap_input_text(s: str):
    parsed = parse_input_text(s)
    if not parsed:
        return None
    subj, cand, ctx = parsed
    return f"[SUBJECT] {cand} [CANDIDATE] {subj} [CONTEXT] {ctx}"

def pair_features(encoder, A_texts, B_texts, batch_size):
    embA = encoder.encode(A_texts, batch_size=batch_size, show_progress_bar=False)
    embB = encoder.encode(B_texts, batch_size=batch_size, show_progress_bar=False)
    return np.concatenate([embA, embB, embA - embB, embA * embB], axis=1)

def pr_recall_f1(y, pred):
    tp = np.sum((pred == 1) & (y == 1))
    fp = np.sum((pred == 1) & (y == 0))
    fn = np.sum((pred == 0) & (y == 1))
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return precision, recall, f1, tp, fp, fn

def eval_flip_only(pA, expected, flip_t):
    decision = np.where(pA <= flip_t, "flip", "keep")

    pos_mask = (expected == "keep")
    rev_mask = (expected == "flip")

    damage = int(np.sum(pos_mask & (decision == "flip")))
    fixed = int(np.sum(rev_mask & (decision == "flip")))

    pos_total = int(np.sum(pos_mask))
    rev_total = int(np.sum(rev_mask))

    dmg_rate = (damage / pos_total) if pos_total else 0.0
    fix_rate = (fixed / rev_total) if rev_total else 0.0

    acc = float(np.mean(decision == expected)) if len(expected) else 0.0
    return dmg_rate, fix_rate, acc, damage, pos_total, fixed, rev_total

def main():
    stage1_meta = load_json(STAGE1_META_PATH)
    stage2_meta = load_json(STAGE2_META_PATH)

    T_JUNK = float(stage1_meta.get("T_junk", stage1_meta.get("T", 0.6)))
    ENCODER_NAME = stage2_meta.get("encoder", ENCODER_NAME_FALLBACK)

    X_test = np.load(X_TEST_PATH)
    y_test = np.load(Y_TEST_PATH).astype(int)

    test_df = pd.read_csv(TEST_DF_PATH)
    if "input_text" not in test_df.columns or "bucket" not in test_df.columns:
        raise ValueError("TEST_DF must contain columns: input_text, bucket")

    bucket = test_df["bucket"].astype(str).values
    input_text = test_df["input_text"].astype(str).values

    stage1 = joblib.load(STAGE1_MODEL_PATH)
    p_junk = stage1.predict_proba(X_test)[:, 1]
    pred_junk = (p_junk >= T_JUNK).astype(int)

    print("=== Stage 1 (junk gate) ===")
    print("model:", STAGE1_MODEL_PATH)
    print("T_junk:", T_JUNK)
    print("test ROC-AUC:", roc_auc_score(y_test, p_junk))
    print("test PR-AUC:", average_precision_score(y_test, p_junk))

    precision, recall, f1, tp, fp, fn = pr_recall_f1(y_test, pred_junk)
    print(f"@T_junk={T_JUNK} predicted junk:", int(tp + fp))
    print("precision:", round(precision, 3), "recall:", round(recall, 3), "F1:", round(f1, 3))

    fp_buckets = bucket[(pred_junk == 1) & (y_test == 0)]
    print("false positives by bucket:", dict(Counter(fp_buckets)))

    passed = (pred_junk == 0)
    is_real = np.isin(bucket, list(REAL_BUCKETS))
    eval_mask = passed & is_real

    print("\n=== Stage 2 (direction) evaluated on Stage-1-passed real-claim buckets only ===")
    print("model:", STAGE2_MODEL_PATH)
    print("encoder:", ENCODER_NAME)

    print("passed total:", int(passed.sum()))
    print("passed real-claims:", int(eval_mask.sum()))
    print("passed positives:", int(np.sum(eval_mask & (bucket == "positive"))))
    print("passed reverse_direction:", int(np.sum(eval_mask & (bucket == "reverse_direction"))))

    idx = np.where(eval_mask)[0].tolist()

    A_texts = []
    B_texts = []
    kept_idx = []
    dropped_parse = 0

    for i in idx:
        A = input_text[i]  # A = keep original pipeline direction
        B = swap_input_text(A)  # B = flipped direction
        if B is None:
            dropped_parse += 1
            continue
        A_texts.append(A)
        B_texts.append(B)
        kept_idx.append(i)

    print("direction eval rows (after parseable swap):", len(kept_idx), "dropped_parse:", dropped_parse)
    if len(kept_idx) == 0:
        return

    stage2 = joblib.load(STAGE2_MODEL_PATH)
    encoder = SentenceTransformer(ENCODER_NAME)
    X_dir = pair_features(encoder, A_texts, B_texts, BATCH_SIZE)
    pA = stage2.predict_proba(X_dir)[:, 1]  # P(A is correct direction)

    expected = np.array(["keep" if bucket[i] == "positive" else "flip" for i in kept_idx], dtype=object)

    print("\n=== Stage 2 flip-only threshold sweep (recommended policy) ===")
    print("Policy: flip if pA <= flip_t, else keep. (No 'uncertain' decisions.)")
    for flip_t in [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]:
        dmg_rate, fix_rate, acc, damage, pos_total, fixed, rev_total = eval_flip_only(pA, expected, flip_t)
        print(
            f"flip_t={flip_t:.2f} | damage={dmg_rate:.3f} ({damage}/{pos_total}) "
            f"| fix={fix_rate:.3f} ({fixed}/{rev_total}) | acc={acc:.3f}"
        )

    print("\n=== End-to-end summary (Stage 1 gating) ===")
    print("Stage1 kept real-claims:", int(eval_mask.sum()), "of", int(is_real.sum()))
    print("Note: sweep above evaluates Stage 2 only on Stage-1-passed real-claims.")

if __name__ == "__main__":
    main()
