import redis
from app.core.config import settings


redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=False)


def get_redis() -> redis.Redis:
    return redis_client
