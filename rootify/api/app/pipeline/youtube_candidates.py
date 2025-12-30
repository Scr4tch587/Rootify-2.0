import re 
import spacy
from pydantic import BaseModel
from typing import List, Literal, Pattern
from app.models import InfluenceCandidate

_nlp = spacy.load("en_core_web_sm") 


def extract_youtube_candidates(text: str) -> List[InfluenceCandidate]:
    doc = _nlp(text)
    out = []

    for sent in doc.sents:

    return out
