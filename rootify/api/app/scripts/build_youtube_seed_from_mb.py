import argparse
import asyncio
import math
import re
import time
from dataclasses import dataclass
from typing import Iterable
from pathlib import Path

import httpx

from app.services.constants import YOUTUBE_ARTIST_SEED
from app.services.musicbrainz import MB_BASE, MB_HEADERS, MB_MIN_INTERVAL_SEC

_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
_WS_RE = re.compile(r"\s+")


def _normalize_name(name: str) -> str:
    norm = name.lower()
    norm = _NON_ALNUM_RE.sub(" ", norm)
    norm = _WS_RE.sub(" ", norm).strip()
    return norm


@dataclass(frozen=True)
class Candidate:
    name: str
    mbid: str
    score: float
    rating: float
    votes: int
    tag: str


class MusicBrainzClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(headers=MB_HEADERS, timeout=15.0)
        self._last_req_ts = 0.0

    async def close(self) -> None:
        await self._client.aclose()

    async def _rate_limit(self) -> None:
        now = time.time()
        wait = (self._last_req_ts + MB_MIN_INTERVAL_SEC) - now
        if wait > 0:
            await asyncio.sleep(wait)
        self._last_req_ts = time.time()

    async def get(self, url: str, params: dict) -> dict:
        last_err: Exception | None = None
        for attempt in range(3):
            try:
                await self._rate_limit()
                r = await self._client.get(url, params=params)
                r.raise_for_status()
                return r.json()
            except (httpx.ConnectError, httpx.ReadError, httpx.RemoteProtocolError) as exc:
                last_err = exc
                await asyncio.sleep(0.6 * (attempt + 1))
        raise last_err if last_err else RuntimeError("MusicBrainz request failed")


class Progress:
    def __init__(self, total: int) -> None:
        self.total = max(total, 1)
        self.done = 0

    def add(self, count: int = 1) -> None:
        self.done += count
        if self.done > self.total:
            self.total = self.done
        pct = int((self.done / self.total) * 100)
        print(f"\rProgress: {self.done}/{self.total} ({pct}%)", end="", flush=True)

    def finish(self) -> None:
        print()


async def _search_artists_by_tag(
    client: MusicBrainzClient,
    tag: str,
    limit: int,
    page_size: int = 100,
    progress: Progress | None = None,
) -> list[dict]:
    artists: list[dict] = []
    offset = 0
    while len(artists) < limit:
        batch = min(page_size, limit - len(artists))
        data = await client.get(
            f"{MB_BASE}/artist/",
            {
                "query": f"tag:{tag}",
                "fmt": "json",
                "limit": batch,
                "offset": offset,
            },
        )
        if progress:
            progress.add()
        items = data.get("artists", [])
        if not items:
            break
        artists.extend(items)
        offset += batch
    return artists


async def _fetch_rating(
    client: MusicBrainzClient,
    mbid: str,
    progress: Progress | None = None,
) -> tuple[float, int]:
    data = await client.get(
        f"{MB_BASE}/artist/{mbid}",
        {"fmt": "json", "inc": "ratings"},
    )
    if progress:
        progress.add()
    rating = data.get("rating") or {}
    value = float(rating.get("value") or 0.0)
    votes = int(rating.get("votes-count") or 0)
    return value, votes


def _popularity_score(rating: float, votes: int) -> float:
    if votes <= 0:
        return 0.0
    return rating * math.log10(votes + 1)


def _dedupe_candidates(
    candidates: Iterable[Candidate],
    existing_norms: set[str],
) -> list[Candidate]:
    seen_mbid: set[str] = set()
    out: list[Candidate] = []
    for c in candidates:
        if c.mbid in seen_mbid:
            continue
        if _normalize_name(c.name) in existing_norms:
            continue
        seen_mbid.add(c.mbid)
        out.append(c)
    return out


def _format_python_list(items: list[str]) -> str:
    lines = ["YOUTUBE_ARTIST_SEED = ["]
    for name in items:
        lines.append(f'    "{name}",')
    lines.append("]")
    return "\n".join(lines)


def _write_seed_to_constants(seed_block: str) -> None:
    constants_path = Path(__file__).resolve().parents[2] / "services" / "constants.py"
    text = constants_path.read_text()
    pattern = re.compile(r"YOUTUBE_ARTIST_SEED\s*=\s*\[(?:.|\n)*?\]\n", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        raise RuntimeError("Could not find YOUTUBE_ARTIST_SEED block in constants.py")
    new_text = text[: match.start()] + seed_block + "\n" + text[match.end() :]
    constants_path.write_text(new_text)


async def build_seed(
    tags: list[str],
    per_tag: int,
    total: int,
) -> list[Candidate]:
    existing_norms = {_normalize_name(name) for name in YOUTUBE_ARTIST_SEED}
    client = MusicBrainzClient()
    page_size = 100
    search_requests = sum(math.ceil(per_tag / page_size) for _ in tags)
    rating_requests = per_tag * len(tags)
    progress = Progress(search_requests + rating_requests)
    try:
        gathered: list[Candidate] = []
        for tag in tags:
            artists = await _search_artists_by_tag(
                client,
                tag,
                per_tag,
                page_size=page_size,
                progress=progress,
            )
            for artist in artists:
                mbid = artist.get("id")
                name = artist.get("name")
                if not mbid or not name:
                    continue
                rating, votes = await _fetch_rating(client, mbid, progress=progress)
                score = _popularity_score(rating, votes)
                gathered.append(
                    Candidate(
                        name=name,
                        mbid=mbid,
                        score=score,
                        rating=rating,
                        votes=votes,
                        tag=tag,
                    )
                )
        filtered = _dedupe_candidates(gathered, existing_norms)
        filtered.sort(key=lambda c: (c.score, c.votes), reverse=True)
        return filtered[:total]
    finally:
        progress.finish()
        await client.close()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a new YOUTUBE_ARTIST_SEED from MusicBrainz tag searches.",
    )
    parser.add_argument(
        "--tags",
        nargs="+",
        default=[
            "pop",
            "rock",
            "hip hop",
            "rap",
            "rnb",
            "soul",
            "jazz",
            "electronic",
            "indie",
            "alternative",
            "metal",
            "country",
            "classical",
            "latin",
            "k-pop",
        ],
        help="Space-separated list of MusicBrainz tags to search.",
    )
    parser.add_argument(
        "--per-tag",
        type=int,
        default=60,
        help="How many artists to fetch per tag search.",
    )
    parser.add_argument(
        "--total",
        type=int,
        default=200,
        help="Total number of new artists to output.",
    )
    parser.add_argument(
        "--format",
        choices=["python", "txt", "json"],
        default="python",
        help="Output format.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write the new seed list directly into services/constants.py.",
    )
    return parser.parse_args()


def _format_output(candidates: list[Candidate], fmt: str) -> str:
    names = [c.name for c in candidates]
    if fmt == "txt":
        return "\n".join(names)
    if fmt == "json":
        import json
        return json.dumps(names, indent=2)
    return _format_python_list(names)


def main() -> None:
    args = _parse_args()
    candidates = asyncio.run(
        build_seed(
            tags=args.tags,
            per_tag=args.per_tag,
            total=args.total,
        )
    )
    output = _format_output(candidates, args.format)
    if args.write:
        if args.format != "python":
            raise ValueError("--write requires --format python")
        _write_seed_to_constants(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
