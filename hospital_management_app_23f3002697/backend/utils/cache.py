"""
Redis caching utilities for API performance
"""
import os
import json
import logging
from typing import Any, Optional

import redis

logger = logging.getLogger(__name__)

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

try:
    redis_client = redis.Redis.from_url(REDIS_URL)
    # Test connection lazily when used
except redis.RedisError as exc:
    logger.error("Failed to initialize Redis client: %s", exc)
    redis_client = None


def is_cache_available() -> bool:
    return redis_client is not None


def cache_get(key: str) -> Optional[str]:
    if not is_cache_available():
        return None
    try:
        value = redis_client.get(key)
        return value.decode('utf-8') if value else None
    except redis.RedisError as exc:
        logger.warning("Redis GET failed for key %s: %s", key, exc)
        return None


def cache_get_json(key: str) -> Optional[Any]:
    value = cache_get(key)
    if value is None:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        logger.warning("Failed to decode cached JSON for key %s", key)
        return None


def cache_set(key: str, value: str, ttl: int = 300) -> bool:
    if not is_cache_available():
        return False
    try:
        redis_client.setex(key, ttl, value)
        return True
    except redis.RedisError as exc:
        logger.warning("Redis SET failed for key %s: %s", key, exc)
        return False


def cache_set_json(key: str, value: Any, ttl: int = 300) -> bool:
    try:
        serialized = json.dumps(value)
    except (TypeError, ValueError) as exc:
        logger.warning("Failed to serialize value for key %s: %s", key, exc)
        return False
    return cache_set(key, serialized, ttl)


def cache_delete(key: str) -> bool:
    if not is_cache_available():
        return False
    try:
        redis_client.delete(key)
        return True
    except redis.RedisError as exc:
        logger.warning("Redis DELETE failed for key %s: %s", key, exc)
        return False


def cache_delete_pattern(pattern: str) -> int:
    """
    Delete cached keys matching pattern. Uses SCAN to avoid blocking Redis.
    """
    if not is_cache_available():
        return 0
    deleted = 0
    try:
        for key in redis_client.scan_iter(match=pattern):
            redis_client.delete(key)
            deleted += 1
    except redis.RedisError as exc:
        logger.warning("Redis SCAN/DELETE failed for pattern %s: %s", pattern, exc)
    return deleted


def invalidate_doctor_availability_cache(doctor_id: int) -> None:
    cache_delete_pattern(f"doctor:availability:{doctor_id}*")


def invalidate_doctor_search_cache() -> None:
    cache_delete_pattern("doctors:search:*")

