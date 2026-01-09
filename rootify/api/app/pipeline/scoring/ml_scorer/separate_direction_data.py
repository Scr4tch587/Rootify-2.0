import pandas as pd
import re
import hashlib
import numpy as np
from pathlib import Path
from collections import Counter

RANDOM_SEED = 42

SOURCE_CSV = Path("/Users/scr4tch/Documents/Coding/Projects/Rootify2/rootify/api/app/pipeline/scoring/ml_scorer/wikipedia_data.csv")
OUT_DIR = Path("/Users/scr4tch/Documents/Coding/Projects/Rootify2/rootify/api/app/pipeline/scoring/ml_scorer")

INCLUDE_REVERSE_BUCKET = True

# Target number of PAIRS (groups) per split, after filtering.
VAL_GROUPS = 60
TEST_GROUPS = 60

CUE_RE = re.compile(
    r"\b("
    r"influenced by|was influenced by|influence of|influences include|influences|"
    r"inspired by|was inspired by|inspiration|drew inspiration from|"
    r"cited as an influence|cited .* as an influence|cites .* as an influence|"
    r"described .* as an influence|credited .* as an influence|"
    r"was shaped by|drew from|borrowed from|"
    r"acknowledged .* as an influence|named .* as an influence"
    r")\b",
    re.IGNORECASE,
)

RX = re.compile(
    r"\[SUBJECT\]\s*(.*?)\s*\[CANDIDATE\]\s*(.*?)\s*\[CONTEXT\]\s*(.*)$",
    re.DOTALL,
)

PRONOUN_LEAD_RE = re.compile(r"^(he|she|they|his|her|their|it|this|these|those)\b", re.IGNORECASE)
WORD_RE = re.compile(r"[a-z0-9]+")

STOP_TOKENS = {"the", "a", "an", "and", "of", "to"}

MAX_COMMAS_ALLOWED = 8
DROP_PRONOUN_LEAD = True
REQUIRE_CUE = True

def parse_input_text(s: str):
    m = RX.match(str(s))
    if not m:
        return None
    subject = m.group(1).strip()
    candidate = m.group(2).strip()
    context = m.group(3).strip()
    if not subject or not candidate or not context:
        return None
    return subject, candidate, context

def norm_space(s: str):
    return re.sub(r"\s+", " ", str(s)).strip()

def norm_ctx(ctx: str):
    return norm_space(ctx).lower()

def stable_id(text: str):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]

def sym_group_key(context: str, subject: str, candidate: str):
    c = norm_ctx(context)
    a = norm_space(subject).lower()
    b = norm_space(candidate).lower()
    x, y = (a, b) if a <= b else (b, a)
    return hashlib.sha1(f"{c}||{x}||{y}".encode("utf-8")).hexdigest()[:20]

def tokens(s: str):
    return [t for t in WORD_RE.findall(str(s).lower()) if t and t not in STOP_TOKENS]

def name_in_context(name: str, context: str):
    nt = tokens(name)
    if not nt:
        return False
    ct = set(tokens(context))
    nt2 = [t for t in nt if len(t) > 1]
    if not nt2:
        nt2 = nt
    if len(nt2) == 1:
        return nt2[0] in ct
    miss = 0
    for t in nt2:
        if t not in ct:
            miss += 1
            if miss > 1:
                return False
    return True

def too_listy(ctx: str):
    return str(ctx).count(",") > MAX_COMMAS_ALLOWED

def context_ok(ctx: str):
    c = str(ctx).strip()
    if REQUIRE_CUE and not CUE_RE.search(c):
        return False
    if DROP_PRONOUN_LEAD and PRONOUN_LEAD_RE.match(c):
        return False
    if too_listy(c):
        return False
    return True

def build_pairs(df_src: pd.DataFrame, base_label: int, source_tag: str, stats: Counter):
    rows = []
    seen = set()

    for _, r in df_src.iterrows():
        parsed = parse_input_text(r["input_text"])
        if not parsed:
            stats["parse_fail"] += 1
            continue

        subject, candidate, context = parsed

        if not name_in_context(candidate, context):
            stats["cand_not_found"] += 1
            continue

        if not context_ok(context):
            stats["ctx_reject"] += 1
            continue

        g = sym_group_key(context, subject, candidate)
        g2 = f"{source_tag}||{g}"
        if g2 in seen:
            stats["dedup"] += 1
            continue
        seen.add(g2)

        orig = f"[SUBJECT] {subject} [CANDIDATE] {candidate} [CONTEXT] {context}"
        swap = f"[SUBJECT] {candidate} [CANDIDATE] {subject} [CONTEXT] {context}"

        if base_label == 1:
            rows.append({"group": g2, "input_text": orig, "label": 1})
            rows.append({"group": g2, "input_text": swap, "label": 0})
        else:
            rows.append({"group": g2, "input_text": orig, "label": 0})
            rows.append({"group": g2, "input_text": swap, "label": 1})

        stats["kept_groups"] += 1

    return pd.DataFrame(rows)

def split_by_group(pairs: pd.DataFrame):
    groups = pairs["group"].unique().tolist()
    rng = np.random.default_rng(RANDOM_SEED)
    rng.shuffle(groups)

    val_n = min(VAL_GROUPS, len(groups) // 5) if len(groups) >= 5 else max(1, len(groups) // 3)
    test_n = min(TEST_GROUPS, len(groups) // 5) if len(groups) >= 5 else max(1, len(groups) // 3)

    val_groups = set(groups[:val_n])
    test_groups = set(groups[val_n : val_n + test_n])
    train_groups = set(groups[val_n + test_n :])

    train = pairs[pairs["group"].isin(train_groups)].copy()
    val = pairs[pairs["group"].isin(val_groups)].copy()
    test = pairs[pairs["group"].isin(test_groups)].copy()
    return train, val, test

def validate_pairs(df: pd.DataFrame, name: str):
    grp = df.groupby("group")["label"].agg(["count", "sum"]).reset_index()
    bad = grp[(grp["count"] != 2) | (grp["sum"] != 1)]
    if len(bad) > 0:
        raise ValueError(f"{name} malformed pairing: {bad.head(10).to_dict(orient='records')}")

def add_ids(df: pd.DataFrame):
    df = df.copy()
    df["id"] = df["input_text"].apply(stable_id)
    df["bucket"] = df["label"].map({1: "direction_correct", 0: "direction_reversed"})
    df = df.set_index("id")
    return df[["input_text", "label", "bucket", "group"]]

def main():
    df = pd.read_csv(SOURCE_CSV, names=["id", "input_text", "label", "bucket"], index_col="id")

    stats = Counter()
    parts = []

    pos = df[df["bucket"] == "positive"].copy()
    parts.append(build_pairs(pos, base_label=1, source_tag="pos", stats=stats))

    if INCLUDE_REVERSE_BUCKET:
        rev = df[df["bucket"] == "reverse_direction"].copy()
        parts.append(build_pairs(rev, base_label=0, source_tag="rev", stats=stats))

    parts = [p for p in parts if len(p) > 0]
    if not parts:
        raise RuntimeError("No direction pairs generated after filtering.")

    pairs = pd.concat(parts, ignore_index=True)

    train, val, test = split_by_group(pairs)

    validate_pairs(train, "train")
    validate_pairs(val, "val")
    validate_pairs(test, "test")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    add_ids(train).to_csv(OUT_DIR / "direction_training.csv")
    add_ids(val).to_csv(OUT_DIR / "direction_validation.csv")
    add_ids(test).to_csv(OUT_DIR / "direction_testing.csv")

    print("total_groups:", pairs["group"].nunique(), "total_rows:", len(pairs))
    print("train_pairs:", train["group"].nunique(), "val_pairs:", val["group"].nunique(), "test_pairs:", test["group"].nunique())
    print("stats:", dict(stats))

if __name__ == "__main__":
    main()
