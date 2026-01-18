import re
import json
import numpy as np
from .registry import get_encoder, get_stage1_meta, get_stage2_meta, get_stage1_model, get_stage2_model

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

def ml_score_wikipedia(input_texts):
    encoder1 = get_encoder()
    embeddings = encoder1.encode(input_texts, batch_size=BATCH_SIZE, show_progress_bar=False)

    stage1_meta = get_stage1_meta()
    stage2_meta = get_stage2_meta()

    T_KEEP = float(stage1_meta.get("T_junk", stage1_meta.get("T", 0.6)))
    FLIP_T = 0.1
    encoder_name = stage2_meta.get("encoder", ENCODER_NAME_FALLBACK)

    stage1 = get_stage1_model()
    p = stage1.predict_proba(embeddings)[:, 1]

    passed = [i for i, prob in enumerate(p) if prob >= T_KEEP]

    A_texts = []
    B_texts = []
    discard = set()
    kept_idx = []

    for i in passed:
        A = input_texts[i]
        B = swap_input_text(A)
        if B:
            A_texts.append(A)
            B_texts.append(B)
            kept_idx.append(i)
        else:
            discard.add(i)

    pA_by_i = {}
    if kept_idx:
        stage2 = get_stage2_model()
        encoder2 = get_encoder(encoder_name)
        X_dir = pair_features(encoder2, A_texts, B_texts, BATCH_SIZE)
        pA = stage2.predict_proba(X_dir)[:, 1]
        for j, i in enumerate(kept_idx):
            pA_by_i[i] = float(pA[j])

    out = []
    for i, input_text in enumerate(input_texts):
        p_valid = float(p[i])

        if i in discard:
            out.append({"input_text": input_text, "p_valid": p_valid, "is_junk": True})
            continue

        if p_valid < T_KEEP:
            out.append({"input_text": input_text, "p_valid": p_valid, "is_junk": True})
            continue

        pA_i = pA_by_i.get(i, None)
        if pA_i is not None and pA_i <= FLIP_T:
            out.append({"input_text": input_text, "p_valid": p_valid, "is_junk": True})
        else:
            out.append({"input_text": input_text, "p_valid": p_valid, "is_junk": False})

    return out
