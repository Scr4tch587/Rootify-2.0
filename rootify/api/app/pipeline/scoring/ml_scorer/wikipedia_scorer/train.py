import pandas as pd
import sklearn
from sentence_transformers import SentenceTransformer
import torch
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

df = pd.read_csv('/Users/scr4tch/Documents/Coding/Projects/Rootify2/rootify/api/app/pipeline/scoring/ml_scorer/wikipedia_scorer/wikipedia_training.csv')
texts = df["input_text"].tolist()
embeddings = model.encode(texts, batch_size = 32, show_progress_bar=True)
labels = df["label"].values
ids = df["id"].values

print(embeddings.shape)
print(len(texts))
print(len(labels))
print(len(ids))
np.save("X_train.npy", embeddings)
np.save("y_train.npy", labels)
np.save("ids_train.npy", ids)

df = pd.read_csv('/Users/scr4tch/Documents/Coding/Projects/Rootify2/rootify/api/app/pipeline/scoring/ml_scorer/wikipedia_scorer/wikipedia_validation.csv')
texts = df["input_text"].tolist()
embeddings = model.encode(texts, batch_size = 32, show_progress_bar=True)
labels = df["label"].values
ids = df["id"].values

print(embeddings.shape)
print(len(texts))
print(len(labels))
print(len(ids))
np.save("X_val.npy", embeddings)
np.save("y_val.npy", labels)
np.save("ids_val.npy", ids)

df = pd.read_csv('/Users/scr4tch/Documents/Coding/Projects/Rootify2/rootify/api/app/pipeline/scoring/ml_scorer/wikipedia_scorer/wikipedia_testing.csv')
texts = df["input_text"].tolist()
embeddings = model.encode(texts, batch_size = 32, show_progress_bar=True)
labels = df["label"].values
ids = df["id"].values

print(embeddings.shape)
print(len(texts))
print(len(labels))
print(len(ids))
np.save("X_test.npy", embeddings)
np.save("y_test.npy", labels)
np.save("ids_tes.npy", ids)