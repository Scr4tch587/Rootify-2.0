import re 
import spacy
from pydantic import BaseModel
from typing import Literal, Pattern

_nlp = spacy.load("en_core_web_sm") 

PatternType = Literal["direct", "strong", "weak"]
PatternDirection = Literal["after", "any"]
class InfluencePattern(BaseModel):
    label: PatternType
    direction: PatternDirection
    regex: Pattern[str]

# Ordered by strength: first match wins (direct > strong > weak)
PATTERN_SPECS = [
    InfluencePattern(
        label="direct",
        direction="any",
        regex=re.compile(
            r"\b(?:really\s+)?influenced\s+(?:me|us|my|our)\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="direct",
        direction="any",
        regex=re.compile(
            r"\b(?:was|were)\s+(?:a\s+)?(?:huge|big|major|massive)\s+influence\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="direct",
        direction="any",
        regex=re.compile(
            r"\b(?:one\s+of\s+)?(?:my|our)\s+(?:biggest|main|primary)\s+influences?\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="direct",
        direction="after",
        regex=re.compile(
            r"\b(?:take|took|taking)\s+(?:a\s+)?lot\s+from\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="direct",
        direction="after",
        regex=re.compile(
            r"\b(influenced\s+by)\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="direct",
        direction="any",
        regex=re.compile(
            r"\bcited\b.*?\bas\s+(?:an\s+)?(?:\w+\s+){0,2}influences?\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="direct",
        direction="any",
        regex=re.compile(
            r"\b(named|listed)\b.*?\b(?:his|her|their)?\s*(?:biggest|primary|main)?\s*\w*\s*influences?\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="direct",
        direction="any",
        regex=re.compile(
            r"\b(named|listed)\b.*?\bas an influence\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="direct",
        direction="after",
        regex=re.compile(
            r"\b(influences?\s+(include|have included)|other influences include)\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(
            r"\b(inspired\s+by)\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(
            r"\bgrew\s+up\s+listening\s+to\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(
            r"\b(draws?|drawing)\s+inspiration\s+from\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(
            r"\bgrew\s+up\s+listening\s+to\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(
            r"\b(?:music|artists|bands|acts)\s+like\b",
            re.IGNORECASE,
        ),
    ),  

    InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(
            r"\b(?:spinning|playing)\s+(?:the\s+)?likes\s+of\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(
            r"\b(heavily\s+influenced\s+by)\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="weak",
        direction="after",
        regex=re.compile(
            r"\b(?:people|they|critics)\s+(?:compare|compared)\s+(?:me|us|our\s+music|the\s+band)\s+to\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="weak",
        direction="after",
        regex=re.compile(
            r"\breminds?\s+me\s+of\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="weak",
        direction="after",
        regex=re.compile(
            r"\b(compared\s+to)\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="weak",
        direction="after",
        regex=re.compile(
            r"\b(reminiscent\s+of)\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="weak",
        direction="after",
        regex=re.compile(
            r"\b(in\s+the\s+style\s+of)\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="weak",
        direction="after",
        regex=re.compile(
            r"\b(sounds?\s+like)\b",
            re.IGNORECASE,
        ),
    ),
]

_CLAUSE_CUTS_ALWAYS = (" which ", " that ", " while ")
_CLAUSE_CUTS_COND = (", and ", " and ", ", but ", " but ")

def _truncate_tail(tail: str) -> str:
    t = tail.strip()

    earliest = None

    for token in _CLAUSE_CUTS_ALWAYS:
        i = t.lower().find(token)
        if i != -1 and (earliest is None or i < earliest):
            earliest = i

    for token in _CLAUSE_CUTS_COND:
        start = 0
        tl = t.lower()
        while True:
            i = tl.find(token, start)
            if i == -1:
                break
            j = i + len(token)
            while j < len(t) and t[j].isspace():
                j += 1
            if j < len(t) and t[j].islower():
                if earliest is None or i < earliest:
                    earliest = i
                break
            start = i + 1

    return t if earliest is None else t[:earliest].strip()



_SPLIT_ON = re.compile(r",|\band\b|\&", re.IGNORECASE)

def _fallback_split_candidates(tail: str):
    tail = tail.strip().strip(".;:()[]")
    m = re.search(r"\bsuch as \b", tail, re.IGNORECASE)
    if m:
        tail = tail[m.end():].strip()
    if not tail:
        return []
    parts = [p.strip() for p in _SPLIT_ON.split(tail)]
    cleaned = []
    for p in parts:
        p = re.sub(r"^(the\s+)?soundtracks of\s+", "", p, flags=re.IGNORECASE)
        p = re.sub(r"^(the\s+)?(?:sampling\s+)?work of\s+", "", p, flags=re.IGNORECASE)
        p = re.sub(r"^\d{4}s\s+", "", p)
        p = re.sub(r"^(rock|pop|jazz|blues|folk|punk|metal|electronic)\s+groups?\s+", "", p, flags=re.IGNORECASE)
        p = re.sub(r"^(jazz|rock|pop|classical|electronic)\s+musician\s+", "", p, flags=re.IGNORECASE)
        p = re.sub(r"^\w+\s+musician\s+", "", p, flags=re.IGNORECASE)
        p = re.sub(r"\b\d{4}\b.*$", "", p).strip()
        p = re.sub(r"^(?:spinning|playing)\s+(?:the\s+)?likes\s+of\s+", "", p, flags=re.IGNORECASE)

        p = p.split('"', 1)[0].strip()   
        if len(p) < 2:
            continue
        if p.lower() in {"the", "a", "an"}:
            continue
        cleaned.append(p)
    seen = set()
    out = []
    for c in cleaned:
        if c in seen:
            continue
        seen.add(c)
        out.append(c)
    return out 

def _canonical_artist_name(name: str):
    n = name.strip()
    if n.lower().startswith("the "):
        n = n[4:].strip()
    n = re.sub(r"\s+", " ", n)
    n = re.sub(r"('s)\b", "", n)
    n = n.rstrip(" .,:;\"")
    n = re.sub(r"[’']$", "", n)
    n = re.sub(r"\s+(production|piece|work|admiration)\b.*$", "", n, flags=re.IGNORECASE).strip()
    return n

_LABELISH_ORG = re.compile(r"\b(Records|Recordings|Label|Studio|Studios)\b", re.IGNORECASE)

def _is_labelish_org(text: str) -> bool:
    return bool(_LABELISH_ORG.search(text))

def extract_influence_candidates(text: str, section_path: str):
    doc = _nlp(text)
    out = []

    for sent in doc.sents:
        s = sent.text.strip()
        if not s:
            continue
        can_fallback = True
        match = None
        pattern_type = None
        direction = None
        for pat in PATTERN_SPECS:
            match = pat.regex.search(s)
            if match:
                if match.re.pattern == r"\b(?:music|artists|bands|acts)\s+like\b":
                    can_fallback = False
                pattern_type = pat.label
                if pattern_type == "weak": 
                    can_fallback = False
                direction = pat.direction
                break

        if not match:
            continue

        match_start = match.start()

        sent_doc = _nlp(s)
        candidates = []
        for ent in sent_doc.ents:
            if ent.label_ not in {"PERSON", "ORG"}: continue
            if ent.label_ == "ORG" and _is_labelish_org(ent.text): continue
            match_end = match.end()
            match_start = match.start()
            if direction == "after":
                if ent.start_char >= match_end and ent.label_ in {"PERSON", "ORG"}:
                    candidates.append(ent.text.strip())
            elif direction == "any":
                if ((ent.end_char <= match_end and match_start <= ent.start_char) or ent.start_char >= match_end) and ent.label_ in {"PERSON", "ORG"}:
                    candidates.append(ent.text.strip())
        match_end = match.end()
        tail = s[match_end:]
        if can_fallback: candidates.extend(_fallback_split_candidates(_truncate_tail(tail)))
        seen = set()
        for name in candidates:
            canon = _canonical_artist_name(name)
            if not canon: continue
            if canon.lower() in seen:
                continue
            seen.add(canon.lower())
            out.append(
                {
                    "influence_artist": canon,
                    "pattern_type": pattern_type,
                    "section_path": section_path,
                    "snippet": s,
                }
            )

    return out
