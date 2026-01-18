import os
import httpx

CACHE_SERVICE_URL = os.getenv("CACHE_SERVICE_URL")

async def cache_get_json(key: str):
    if not CACHE_SERVICE_URL:
        return None
    url = f"{CACHE_SERVICE_URL}/cache/{key}"
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            r = await client.get(url)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None

async def cache_put_json(key: str, value, ttl_seconds: int):
    if not CACHE_SERVICE_URL:
        return
    url = f"{CACHE_SERVICE_URL}/cache/{key}"
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            await client.put(url, params={"ttl": ttl_seconds}, json=value)
    except Exception:
        return
