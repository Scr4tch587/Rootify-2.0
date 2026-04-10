import re

import httpx

YOUTUBE_SEARCH_URL = "https://www.youtube.com/results"
YOUTUBE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

VIDEO_ID_RE = re.compile(r'"videoId":"([A-Za-z0-9_-]{11})"')


def _build_search_queries(artist_name: str) -> list[str]:
    base = artist_name.strip()
    return [
        f"{base} influences interview",
        f"{base} musical influences",
        f"{base} inspired by interview",
        f"{base} talks about influences",
    ]


async def _search_video_ids(query: str) -> list[str]:
    params = {"search_query": query}
    async with httpx.AsyncClient(headers=YOUTUBE_HEADERS, timeout=15.0, follow_redirects=True) as client:
        response = await client.get(YOUTUBE_SEARCH_URL, params=params)
        response.raise_for_status()

    seen: set[str] = set()
    out: list[str] = []
    for match in VIDEO_ID_RE.findall(response.text):
        if match in seen:
            continue
        seen.add(match)
        out.append(match)
    return out


async def discover_youtube_videos(artist_name: str, max_results: int = 5) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []

    for query in _build_search_queries(artist_name):
        video_ids = await _search_video_ids(query)
        for video_id in video_ids:
            if video_id in seen:
                continue
            seen.add(video_id)
            out.append(video_id)
            if len(out) >= max_results:
                return out

    return out
