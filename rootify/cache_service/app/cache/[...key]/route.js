import { NextResponse } from "next/server";
import { getRedisClient } from "../../../lib/redis";

function buildKey(params) {
  if (!params?.key || params.key.length === 0) {
    return null;
  }

  return params.key.join("/");
}

export async function GET(request, { params }) {
  const key = buildKey(params);
  if (!key) {
    return NextResponse.json({ detail: "missing key" }, { status: 400 });
  }

  const redis = await getRedisClient();
  const raw = await redis.get(key);

  if (raw === null) {
    return NextResponse.json({ detail: "miss" }, { status: 404 });
  }

  return NextResponse.json(JSON.parse(raw));
}

export async function PUT(request, { params }) {
  const key = buildKey(params);
  if (!key) {
    return NextResponse.json({ detail: "missing key" }, { status: 400 });
  }

  const { searchParams } = new URL(request.url);
  const ttlParam = searchParams.get("ttl");
  const ttl = ttlParam ? Number.parseInt(ttlParam, 10) : NaN;

  if (!Number.isFinite(ttl) || ttl <= 0) {
    return NextResponse.json({ detail: "invalid ttl" }, { status: 400 });
  }

  const body = await request.json();
  const raw = JSON.stringify(body);

  const redis = await getRedisClient();
  await redis.setEx(key, ttl, raw);

  return NextResponse.json({ ok: true });
}
