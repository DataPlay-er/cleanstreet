import logging
from contextlib import contextmanager
from typing import Optional

import redis
from redis import Redis

from app.config import settings

logger = logging.getLogger(__name__)


def get_redis_client() -> Redis:
    return redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_timeout=2,
        socket_connect_timeout=2,
    )

# Module-level client — single connection pool shared across the process
_redis: Redis = get_redis_client()


def _rate_limit_key(username: str) -> str:
    return f"auth:rl:{username}"


def _denylist_key(jti: str) -> str:
    return f"auth:deny:{jti}"


def is_rate_limited(username: str) -> bool:
    try:
        count = _redis.get(_rate_limit_key(username))
        if count is None:
            return False
        return int(count) >= settings.rate_limit_max_attempts
    except redis.RedisError as e:
        logger.warning("Redis unavailable during rate limit check: %s", e)
        return False   # fail open — don't lock out users because Redis is down


def record_failed_attempt(username: str) -> int:
    try:
        key = _rate_limit_key(username)
        pipe = _redis.pipeline()
        pipe.incr(key)
        # Only set TTL on first attempt — don't reset the window on each failure
        pipe.expire(key, settings.rate_limit_window_seconds, nx=True)
        results = pipe.execute()
        return results[0]   # the new count from INCR
    except redis.RedisError as e:
        logger.warning("Redis unavailable during failed attempt record: %s", e)
        return 0


def clear_failed_attempts(username: str) -> None:
    try:
        _redis.delete(_rate_limit_key(username))
    except redis.RedisError as e:
        logger.warning("Redis unavailable during attempt counter clear: %s", e)


def get_failed_attempts(username: str) -> int:
    """Return current failed attempt count (for informational purposes)."""
    try:
        count = _redis.get(_rate_limit_key(username))
        return int(count) if count else 0
    except redis.RedisError:
        return 0


def denylist_token(jti: str, ttl_seconds: int) -> None:
    try:
        _redis.setex(_denylist_key(jti), ttl_seconds, "1")
    except redis.RedisError as e:
        logger.error("Redis unavailable — could not denylist token %s: %s", jti, e)
        # Fail loud here — a failed denylist means the token stays valid.
        # Log and monitor; don't silently skip.


def is_token_denylisted(jti: str) -> bool:
    try:
        return _redis.exists(_denylist_key(jti)) == 1
    except redis.RedisError as e:
        logger.warning("Redis unavailable during denylist check: %s", e)
        return False