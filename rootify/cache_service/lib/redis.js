import { createClient } from "redis";

const globalForRedis = globalThis;

async function connectClient(client) {
  if (!client.isOpen) {
    await client.connect();
  }
}

export async function getRedisClient() {
  const redisUrl = process.env.REDIS_URL;
  if (!redisUrl) {
    throw new Error("REDIS_URL is not set");
  }

  if (!globalForRedis.__redisClient) {
    globalForRedis.__redisClient = createClient({ url: redisUrl });
    globalForRedis.__redisClient.on("error", (err) => {
      console.error("Redis client error", err);
    });
  }

  await connectClient(globalForRedis.__redisClient);
  return globalForRedis.__redisClient;
}
