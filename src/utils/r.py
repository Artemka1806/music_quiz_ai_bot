import redis.asyncio as aioredis

from src.utils.settings import settings


async def init_redis_pool() -> aioredis.Redis:
    redis = await aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        password=settings.REDIS_PASSWORD.get_secret_value(),
        db=settings.REDIS_DB,
        encoding="utf-8",
        decode_responses=True
    )
    return redis


redis_pool: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global redis_pool
    if redis_pool is None:
        redis_pool = await init_redis_pool()
    return redis_pool

