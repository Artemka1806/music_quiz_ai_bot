import redis.asyncio as aioredis

from src.utils.settings import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


async def init_redis_pool() -> aioredis.Redis:
    logger.info("Initializing Redis connection pool")
    try:
        redis = await aioredis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            password=settings.REDIS_PASSWORD.get_secret_value(),
            db=settings.REDIS_DB,
            encoding="utf-8",
            decode_responses=True
        )
        logger.info("Successfully connected to Redis")
        return redis
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        raise


redis_pool: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global redis_pool
    if redis_pool is None:
        logger.debug("Redis pool not initialized, creating new pool")
        redis_pool = await init_redis_pool()
    return redis_pool

