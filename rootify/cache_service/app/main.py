import json
import os
from fastapi import FastAPI, HTTPException, Request
from redis.asyncio import Redis
from redis.asyncio.client import Redis as RedisType

app = FastAPI()

REDIS_URL = os.environ["REDIS_URL"]
redis: RedisType | None = None

@app.on_event("startup")
async def _startup():
    global redis
    redis = Redis.from_url(REDIS_URL, decode_responses=True)

@app.on_event("shutdown")
async def _shutdown():
    global redis
    if redis is not None:
        await redis.aclose()

@app.get("/cache/{key:path}")
async def cache_get(key: str):
    assert redis is not None
    raw = await redis.get(key)
    if raw is None:
        raise HTTPException(status_code=404, detail="miss")
    return json.loads(raw)

@app.put("/cache/{key:path}")
async def cache_put(key: str, request: Request, ttl: int):
    assert redis is not None
    body = await request.json()
    raw = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
    await redis.setex(key, ttl, raw)
    return {"ok": True}
