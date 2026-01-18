from functools import lru_cache
from sentence_transformers import SentenceTransformer
import json
import joblib
import os

_HERE = os.path.dirname(__file__)


@lru_cache(maxsize=1)
def get_encoder(name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    return SentenceTransformer(name)


def _data_path(name: str) -> str:
    return os.path.join(_HERE, name)


@lru_cache(maxsize=1)
def get_stage1_meta():
    with open(_data_path("logreg_minilm_c10.meta.json"), "r") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def get_stage2_meta():
    with open(_data_path("logreg_direction_pair_c100.meta.json"), "r") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def get_stage1_model():
    return joblib.load(_data_path("logreg_minilm_c10.joblib"))


@lru_cache(maxsize=1)
def get_stage2_model():
    return joblib.load(_data_path("logreg_direction_pair_c100.joblib"))