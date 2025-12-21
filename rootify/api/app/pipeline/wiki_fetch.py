import wikipediaapi

def _wiki_client() -> wikipediaapi.Wikipedia:
    return wikipediaapi.Wikipedia(
        user_agent="Rootify/0.1 (contact: dev@rootify.local)",
        language="en",
        extract_format = wikipediaapi.ExtractFormat.WIKI
    )

def fetch_wikipedia_page_obj(artist_name: str) -> wikipediaapi.WikipediaPage:
    wiki = _wiki_client()

    page = wiki.page(artist_name)

    if not page.exists():
        raise ValueError(f"Wikipedia page not found for: {artist_name}")
    return page

def fetch_wikipedia_page(artist_name: str) -> str:
    return fetch_wikipedia_page_obj(artist_name).text