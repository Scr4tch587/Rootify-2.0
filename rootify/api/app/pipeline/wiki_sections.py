from typing import List, Dict, Tuple
import re
from app.pipeline.wiki_fetch import fetch_wikipedia_page_obj

DEFAULT_SECTION_KEYWORDS = [
    "Influences",
    "Artistry",
    "Musical style",
    "Songwriting",
    "Themes",
    "Life",
    "Background",
    "Career",
]

_KEYWORD_ALIASES = {
    "Influences": [
        "influence",
        "influences",
        "influence and legacy",
        "style and influences",
        "musical style and influences",
        "legacy",
        "impact",
    ],
    "Artistry": [
        "artistry",
        "style",
        "musical style",
        "music",
        "sound",
    ],
    "Musical style": [
        "musical style",
        "style",
        "musical style and influences",
        "style and influences",
        "music",
        "sound",
        "genre",
    ],
    "Songwriting": [
        "songwriting",
        "lyrics",
        "composition",
        "writing",
        "music and lyrics",
    ],
    "Themes": [
        "themes",
        "lyrics",
        "lyrical",
        "subject matter",
    ],
    "Life": [
        "life",
        "personal life",
        "early life",
    ],
    "Background": [
        "background",
        "early life",
        "formation",
        "history",
        "origins",
    ],
    "Career": [
        "career",
        "history",
        "formation",
        "beginnings",
    ],
}

def _iter_sections_with_paths(page) -> List[Tuple[str, str]]:
    out = []
    def walk(sections, prefix: str) -> None:
        for s in sections:
            title = s.title
            path = f"{prefix} > {title}" if prefix else title
            out.append((path, s.text))
            walk(s.sections, path)
    walk(page.sections, "")
    return out

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())

def extract_relevant_sections(
    artist_name: str,
    keywords: List[str] = DEFAULT_SECTION_KEYWORDS,
) -> List[Dict[str, str]]:
    page = fetch_wikipedia_page_obj(artist_name)
    sections = _iter_sections_with_paths(page)

    found = []
    used_paths = set()

    for kw in keywords:
        aliases = _KEYWORD_ALIASES.get(kw, [kw])
        alias_norms = [_norm(a) for a in aliases]

        best = []
        for path, text in sections:
            if path in used_paths:
                continue
            title = path.split(" > ")[-1]
            title_n = _norm(title)

            score = None
            for a in alias_norms:
                if title_n == a:
                    score = 3
                    break
                if a in title_n:
                    score = 2
                if title_n in a:
                    score = max(score or 0, 1)

            if score is None:
                continue

            best.append((score, path, text))

        best.sort(key=lambda x: (-x[0], len(x[1])))
        for _, path, text in best:
            if path in used_paths:
                continue
            found.append({"keyword": kw, "section_path": path, "text": text})
            used_paths.add(path)

    if not found:
        return [{"keyword": "FALLBACK_FULL_PAGE", "section_path": page.title, "text": page.text}]
    return found
