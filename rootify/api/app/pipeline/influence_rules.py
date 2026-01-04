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


PATTERN_SPECS = [
    InfluencePattern(
        label="direct",
        direction="any",
        regex=re.compile(r"\b(?:really\s+)?influenced\s+(?:me|us|my|our)\b", re.IGNORECASE),
    ),
    InfluencePattern(
        label="direct",
        direction="any",
        regex=re.compile(r"\b(?:was|were)\s+(?:a\s+)?(?:huge|big|major|massive)\s+influence\b", re.IGNORECASE),
    ),
    InfluencePattern(
        label="direct",
        direction="any",
        regex=re.compile(r"\b(?:one\s+of\s+)?(?:my|our)\s+(?:biggest|main|primary)\s+influences?\b", re.IGNORECASE),
    ),
    InfluencePattern(
        label="direct",
        direction="after",
        regex=re.compile(r"\b(?:take|took|taking)\s+(?:a\s+)?lot\s+from\b", re.IGNORECASE),
    ),
    InfluencePattern(
        label="direct",
        direction="after",
        regex=re.compile(r"\b(influenced\s+by)\b", re.IGNORECASE),
    ),

    InfluencePattern(
        label="direct",
        direction="after",
        regex=re.compile(
            r"\b(?:cited|cite|cites|named|list(?:ed)?)\s+(?:as\s+)?(?:his|her|their|its)\s+influences?\b"
            r"|\b(?:cited|cite|cites)\b(?!\s+(?:as\s+)?(?:an?\s+)?influence\s+by)(?!\s+as\s+an?\s+influence\s+by).*?\bas\s+(?:an?\s+)?influences?\b",
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
        regex=re.compile(r"\b(named|listed)\b.*?\bas an influence\b", re.IGNORECASE),
    ),
    InfluencePattern(
        label="direct",
        direction="after",
        regex=re.compile(r"\b(influences?\s+(include|have included)|other influences include)\b", re.IGNORECASE),
    ),
    InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(r"\b(inspired\s+by)\b", re.IGNORECASE),
    ),
    InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(r"\bgrew\s+up\s+listening\s+to\b", re.IGNORECASE),
    ),
    InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(r"\b(draws?|drawing)\s+inspiration\s+from\b", re.IGNORECASE),
    ),
    InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(r"\b(?:music|artists|bands|acts)\s+like\b", re.IGNORECASE),
    ),
    InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(r"\b(?:spinning|playing)\s+(?:the\s+)?likes\s+of\b", re.IGNORECASE),
    ),
    InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(r"\b(heavily\s+influenced\s+by)\b", re.IGNORECASE),
    ),

        InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(
            r"\b(?:was|were|is|are)\s+influenced\s+by\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(
            r"\b(?:drew|draws|drawing)\s+(?:heavily\s+)?(?:from|on)\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(
            r"\b(?:took|takes|taking)\s+(?:influence|influences)\s+from\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(
            r"\b(?:influences?|inspiration)\s+(?:range|ranged)\s+from\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(
            r"\bthe\s+influence\s+of\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(
            r"\b(?:was|were|is|are)\s+inspired\s+by\s+the\s+work\s+of\b",
            re.IGNORECASE,
        ),
    ),

        InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(
            r"\bwith\s+influence\s+from\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(
            r"\bwith\s+influence\s+from\s+artists?\s+such\s+as\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(
            r"\binfluenced\s+(?:prominently|notably|largely|mainly|partly)\s+by\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(
            r"\b(?:was|were|is|are)\s+influenced\s+by\s+bands?\s+such\s+as\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="strong",
        direction="after",
        regex=re.compile(
            r"\b(?:was|were|is|are)\s+influenced\s+by\s+artists?\s+such\s+as\b",
            re.IGNORECASE,
        ),
    ),

    InfluencePattern(
        label="strong",
        direction="any",
        regex=re.compile(
            r"\b(?:a|an)\s+[^.]{0,120}?\b(?:ripoff|clone|knockoff)\b",
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
        regex=re.compile(r"\breminds?\s+me\s+of\b", re.IGNORECASE),
    ),
    InfluencePattern(
        label="weak",
        direction="after",
        regex=re.compile(r"\b(compared\s+to)\b", re.IGNORECASE),
    ),
    InfluencePattern(
        label="weak",
        direction="after",
        regex=re.compile(r"\b(reminiscent\s+of)\b", re.IGNORECASE),
    ),
    InfluencePattern(
        label="weak",
        direction="after",
        regex=re.compile(r"\b(in\s+the\s+style\s+of)\b", re.IGNORECASE),
    ),
    InfluencePattern(
        label="weak",
        direction="after",
        regex=re.compile(r"\b(sounds?\s+like)\b", re.IGNORECASE),
    ),
]

_CLAUSE_CUTS_ALWAYS = (" which ", " that ", " while ")
_CLAUSE_CUTS_COND = (", and ", " and ", ", but ", " but ")


_GENRE_WORD = re.compile(
    r"\b(jazz|rock|roll|r&b|rhythm\s+and\s+blues|blues|folk|punk|metal|hip\s*hop|rap|electronic|techno|house|disco|funk|soul|gospel|country|classical|ambient|industrial|reggae|ska|grunge|new\s+wave|post[-\s]?punk|shoegaze|krautrock|avant[-\s]?garde)\b",
    re.IGNORECASE,
)

_MOVEMENT_WORD = re.compile(
    r"\b(music|scene|movement|genre|style|tradition)\b",
    re.IGNORECASE,
)

_REVERSE_INFLUENCE = re.compile(
    r"\b(?:have|has|had)\s+been\s+cited\s+as\s+(?:an?\s+)?influence\s+by\b"
    r"|\b(?:is|are|was|were)\s+cited\s+as\s+(?:an?\s+)?influence\s+by\b"
    r"|\b(?:have|has|had)\s+cited\b.*?\bas\s+(?:an?\s+)?influence\b"
    r"|\bcited\b.*?\bas\s+(?:an?\s+)?influence\b"
    r"|\b(?:have|has)\s+influenced\s+(?:countless|many|numerous|a\s+number\s+of)\b"
    r"|\b(?:is|are|was|were)\s+(?:highly|hugely|widely)\s+influential\b",
    re.IGNORECASE,
)

def _looks_like_artist_name(text: str) -> bool:
    t = text.strip()
    if not t:
        return False
    if len(t) < 3:
        return False

    has_cap = any("A" <= ch <= "Z" for ch in t)
    has_digit = any(ch.isdigit() for ch in t)
    has_symbol = any(ch in ".'&/-" for ch in t)

    if not (has_cap or has_digit or has_symbol):
        return False

    tl = t.lower()
    if _GENRE_WORD.search(tl) and not has_cap:
        return False

    if _MOVEMENT_WORD.search(tl) and not has_cap:
        return False

    return True


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
        tail = tail[m.end() :].strip()
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
        p = re.sub(r"^(?:including|such\s+as)\s+", "", p, flags=re.IGNORECASE)

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

def _norm_simple(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())

def _reverse_influenced_by_subject(sentence: str, subject_name: str) -> bool:
    sn = _norm_simple(subject_name)
    s = _norm_simple(sentence)
    s = re.sub(r"[’']", "'", s)
    return ("influenced by " + sn) in s or ("influenced by the " + sn) in s

_LABELISH_ORG = re.compile(r"\b(Records|Recordings|Label|Studio|Studios)\b", re.IGNORECASE)


def _is_labelish_org(text: str) -> bool:
    return bool(_LABELISH_ORG.search(text))


_ROLE_WORDS = re.compile(
    r"\b(guitarist|drummer|bassist|singer|vocalist|producer|composer|rapper|dj|member|frontman|frontwoman)\b",
    re.IGNORECASE,
)

_POSSESSIVE_BAD_NEXT = re.compile(r"^\s*(?:'s|’s)\s+(admiration|work|production|piece)\b", re.IGNORECASE)


def _is_possessive_abstract_owner(sentence: str, ent_end_char: int) -> bool:
    return bool(_POSSESSIVE_BAD_NEXT.search(sentence[ent_end_char:]))


def _org_is_just_descriptor(sentence: str, org_ent, sent_ents) -> bool:
    window = sentence[org_ent.end_char : min(len(sentence), org_ent.end_char + 40)]
    if not _ROLE_WORDS.search(window):
        return False
    for e in sent_ents:
        if e.label_ == "PERSON" and e.start_char > org_ent.end_char:
            return True
    return False


def extract_influence_candidates(text: str, section_path: str, subject_name: str | None = None):
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

        if subject_name and _reverse_influenced_by_subject(s, subject_name):
            continue

        if _REVERSE_INFLUENCE.search(s):
            continue

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

        sent_doc = _nlp(s)
        match_end = match.end()
        match_start = match.start()

        candidates = []
        for ent in sent_doc.ents:
            if ent.label_ not in {"PERSON", "ORG"}:
                continue
            if ent.label_ == "ORG" and _is_labelish_org(ent.text):
                continue

            if direction == "after":
                if ent.start_char >= match_end:
                    if ent.label_ == "ORG" and _org_is_just_descriptor(s, ent, sent_doc.ents):
                        continue
                    if _is_possessive_abstract_owner(s, ent.end_char):
                        continue
                    candidates.append(ent.text.strip())

            elif direction == "any":
                if ((ent.end_char <= match_end and match_start <= ent.start_char) or ent.start_char >= match_end):
                    if ent.label_ == "ORG" and _org_is_just_descriptor(s, ent, sent_doc.ents):
                        continue
                    if _is_possessive_abstract_owner(s, ent.end_char):
                        continue
                    candidates.append(ent.text.strip())

        tail = s[match_end:]
        if can_fallback:
            candidates.extend(_fallback_split_candidates(_truncate_tail(tail)))

        seen = set()
        for name in candidates:
            canon = _canonical_artist_name(name)
            if not canon:
                continue
            if not _looks_like_artist_name(canon):
                continue
            key = canon.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(
                {
                    "influence_artist": canon,
                    "pattern_type": pattern_type,
                    "section_path": section_path,
                    "snippet": s,
                }
            )

    return out
