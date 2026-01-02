import asyncio
import time
from dataclasses import dataclass
from typing import Optional

import httpx

MB_BASE = "https://musicbrainz.org/ws/2"
MB_HEADERS = {
    "User-Agent": "Rootify/0.1 (contact: k318zhang@gmail.com)",
    "Accept": "application/json",
}

_mb_client: httpx.AsyncClient | None = None
_mb_client_lock = asyncio.Lock()

async def _get_mb_client() -> httpx.AsyncClient:
    global _mb_client
    if _mb_client is not None:
        return _mb_client
    async with _mb_client_lock:
        if _mb_client is None:
            _mb_client = httpx.AsyncClient(headers=MB_HEADERS, timeout=10.0)
        return _mb_client

@dataclass(frozen=True)
class CacheItem:
    value: Optional[str]
    expires_at: float

_name_to_mbid: dict[str, CacheItem] = {}
_mbid_to_name: dict[str, CacheItem] = {}

_in_flight_name: dict[str, asyncio.Future] = {}
_in_flight_mbid: dict[str, asyncio.Future] = {}

_cache_lock = asyncio.Lock()
_rate_lock = asyncio.Lock()
_last_req_ts = 0.0

POS_TTL_NAME_TO_MBID = 60 * 60 * 24 * 14
NEG_TTL_NAME_TO_MBID = 60 * 60 * 24 * 1
POS_TTL_MBID_TO_NAME = 60 * 60 * 24 * 60
NEG_TTL_MBID_TO_NAME = 60 * 60 * 24 * 7

MB_MIN_INTERVAL_SEC = 1.0


def _now() -> float:
    return time.time()


def _normalize_key(s: str) -> str:
    return " ".join(s.lower().split()).strip()


async def _rate_limit():
    global _last_req_ts
    async with _rate_lock:
        now = _now()
        wait = (_last_req_ts + MB_MIN_INTERVAL_SEC) - now
        if wait > 0:
            await asyncio.sleep(wait)
        _last_req_ts = _now()


async def _mb_get(url: str, params: dict) -> dict:
    await _rate_limit()
    client = await _get_mb_client()
    try:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()
    except (httpx.ConnectError, httpx.ReadError, httpx.RemoteProtocolError):
        await asyncio.sleep(0.4)
        await _rate_limit()
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()

async def fetch_mbid_cached(name: str, score_threshold: int = 85) -> Optional[str]:
    key = _normalize_key(name)
    now = _now()

    async with _cache_lock:
        item = _name_to_mbid.get(key)
        if item and item.expires_at > now:
            return item.value

        fut = _in_flight_name.get(key)
        if fut is None:
            fut = asyncio.get_running_loop().create_future()
            _in_flight_name[key] = fut
            leader = True
        else:
            leader = False

    if not leader:
        return await fut

    try:
        data = await _mb_get(
            f"{MB_BASE}/artist/",
            {"query": f'artist:"{name}"', "fmt": "json"},
        )

        artists = data.get("artists", [])
        mbid = None
        if artists:
            top = artists[0]
            if top.get("score", 0) >= score_threshold:
                mbid = top.get("id")

        ttl = POS_TTL_NAME_TO_MBID if mbid else NEG_TTL_NAME_TO_MBID
        async with _cache_lock:
            _name_to_mbid[key] = CacheItem(mbid, now + ttl)
            fut = _in_flight_name.pop(key)
            fut.set_result(mbid)

        return mbid
    except Exception:
        async with _cache_lock:
            fut = _in_flight_name.pop(key)
            fut.set_result(None)
            _name_to_mbid[key] = CacheItem(None, now + NEG_TTL_NAME_TO_MBID)
        return None



async def fetch_deduped_name_cached(mbid: str) -> Optional[str]:
    key = mbid.strip()
    now = _now()

    async with _cache_lock:
        item = _mbid_to_name.get(key)
        if item and item.expires_at > now:
            return item.value

        fut = _in_flight_mbid.get(key)
        if fut is None:
            fut = asyncio.get_running_loop().create_future()
            _in_flight_mbid[key] = fut
            leader = True
        else:
            leader = False

    if not leader:
        return await fut

    try:
        data = await _mb_get(
            f"{MB_BASE}/artist/{key}",
            {"fmt": "json"},
        )

        canon = data.get("name")
        ttl = POS_TTL_MBID_TO_NAME if canon else NEG_TTL_MBID_TO_NAME

        async with _cache_lock:
            _mbid_to_name[key] = CacheItem(canon, now + ttl)
            fut = _in_flight_mbid.pop(key)
            fut.set_result(canon)

        return canon
    except Exception:
        async with _cache_lock:
            fut = _in_flight_mbid.pop(key)
            fut.set_result(None)
            _mbid_to_name[key] = CacheItem(None, now + NEG_TTL_MBID_TO_NAME)
        return None
