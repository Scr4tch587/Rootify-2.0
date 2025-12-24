import re 
import spacy

_nlp = spacy.load("en_core_web_sm") 

_DIRECT_PATTERNS = [
    re.compile(r"\b(influenced by)\b", re.IGNORECASE),
    re.compile(r"\b(influences include|other influences include|influences have included)\b", re.IGNORECASE),
    re.compile(r"\b(cited as an influence)\b", re.IGNORECASE),
]


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
        p = p.strip().strip(".;:()[]")
        p = re.sub(r"^(the\s+)?soundtracks of\s+", "", p, flags=re.IGNORECASE)
        p = re.sub(r"^\d{4}s\s+", "", p)
        p = re.sub(r"^(rock|pop|jazz|blues|folk|punk|metal|electronic)\s+groups?\s+", "", p, flags=re.IGNORECASE)

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
    n = n.rstrip(" .,:;")
    return n

def extract_influence_candidates(text: str, section_path: str):
    doc = _nlp(text)
    out = []

    for sent in doc.sents:
        s = sent.text.strip()
        if not s:
            continue

        match = None
        for pat in _DIRECT_PATTERNS:
            match = pat.search(s)
            if match:
                break

        if not match:
            continue

        match_start = match.start()

        sent_doc = _nlp(s)
        candidates = []
        for ent in sent_doc.ents:
            if ent.start_char > match_start and ent.label_ in {"PERSON", "ORG"}:
                candidates.append(ent.text.strip())
        tail = s[match.end():]
        candidates.extend(_fallback_split_candidates(tail))
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
                    "pattern_type": "direct",
                    "section_path": section_path,
                    "snippet": s,
                }
            )

    return out
