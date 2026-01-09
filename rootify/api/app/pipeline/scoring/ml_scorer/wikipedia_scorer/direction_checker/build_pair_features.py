import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

def build_pairs(df: pd.DataFrame, seed: int):
    if "group" not in df.columns:
        raise ValueError("CSV must include a 'group' column. Regenerate direction_* CSVs with group included.")

    rng = np.random.default_rng(seed)

    pairs = []
    for g, chunk in df.groupby("group", sort=False):
        if len(chunk) != 2:
            continue
        labs = sorted(chunk["label"].tolist())
        if labs != [0, 1]:
            continue

        row_pos = chunk.loc[chunk["label"] == 1].iloc[0]
        row_neg = chunk.loc[chunk["label"] == 0].iloc[0]

        A_is_pos = bool(rng.integers(0, 2))
        if A_is_pos:
            A = row_pos["input_text"]
            B = row_neg["input_text"]
            y = 1
        else:
            A = row_neg["input_text"]
            B = row_pos["input_text"]
            y = 0

        pairs.append((A, B, y))

    if not pairs:
        return [], [], np.array([], dtype=np.int64)

    A_texts = [p[0] for p in pairs]
    B_texts = [p[1] for p in pairs]
    y = np.array([p[2] for p in pairs], dtype=np.int64)
    return A_texts, B_texts, y

def encode_pair_features(model, A_texts, B_texts, batch_size: int):
    embA = model.encode(A_texts, batch_size=batch_size, show_progress_bar=True)
    embB = model.encode(B_texts, batch_size=batch_size, show_progress_bar=True)
    X = np.concatenate([embA, embB, embA - embB, embA * embB], axis=1)
    return X

def main():
    seed = 42
    batch_size = 32

    model = SentenceTransformer("all-MiniLM-L6-v2")

    df_train = pd.read_csv("direction_training.csv")
    df_val = pd.read_csv("direction_validation.csv")
    df_test = pd.read_csv("direction_testing.csv")

    A_tr, B_tr, y_tr = build_pairs(df_train, seed=seed)
    A_va, B_va, y_va = build_pairs(df_val, seed=seed + 1)
    A_te, B_te, y_te = build_pairs(df_test, seed=seed + 2)

    X_tr = encode_pair_features(model, A_tr, B_tr, batch_size=batch_size)
    X_va = encode_pair_features(model, A_va, B_va, batch_size=batch_size)
    X_te = encode_pair_features(model, A_te, B_te, batch_size=batch_size)

    np.save("X_train.npy", X_tr)
    np.save("y_train.npy", y_tr)
    np.save("X_val.npy", X_va)
    np.save("y_val.npy", y_va)
    np.save("X_test.npy", X_te)
    np.save("y_test.npy", y_te)

    print("train pairs:", len(y_tr), "X:", X_tr.shape)
    print("val pairs:", len(y_va), "X:", X_va.shape)
    print("test pairs:", len(y_te), "X:", X_te.shape)

if __name__ == "__main__":
    main()
