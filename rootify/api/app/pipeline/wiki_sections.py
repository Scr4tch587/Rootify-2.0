from typing import List, Dict, Tuple
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

def _iter_sections_with_paths(page) -> List[Tuple[str, str]]:
    out = []

    def walk(sections, prefix:str) -> None:
        for s in sections:
            title = s.title
            path = f"{prefix} > {title}" if prefix else title
            out.append((path, s.text))
            walk(s.sections, path)
    
    walk(page.sections, "")
    return out

def extract_relevant_sections(
        artist_name: str,
        keywords: List[str] = DEFAULT_SECTION_KEYWORDS,
) -> List[Dict[str, str]]:
    page = fetch_wikipedia_page_obj(artist_name)
    sections = _iter_sections_with_paths(page)

    found = []
    used_paths = set()
    
    for kw in keywords:
        kw_lower = kw.lower()
        for path,text in sections:
            if path.lower().endswith(kw_lower) and path not in used_paths:
                found.append({"keyword": kw, "section_path": path, "text": text})
                used_paths.add(path)
    
    if not found:
        return [{"keyword": "FALLBACK_FULL_PAGE", "section_path": page.title, "text": page.text}]
    return found