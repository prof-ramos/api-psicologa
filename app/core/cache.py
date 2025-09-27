"""
Caching strategies for astrological calculations.
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
from functools import wraps

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from ..core.config import settings

logger = logging.getLogger(__name__)


class InMemoryCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self, default_ttl: int = 3600):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl

    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired."""
        if 'expires_at' not in cache_entry:
            return True
        return datetime.now() > cache_entry['expires_at']

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self._cache:
            entry = self._cache[key]
            if not self._is_expired(entry):
                return entry['value']
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        ttl = ttl or self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at
        }

    def delete(self, key: str) -> None:
        """Delete key from cache."""
        self._cache.pop(key, None)

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()

    def size(self) -> int:
        """Get cache size."""
        return len(self._cache)


class RedisCache:
    """Redis-based cache with JSON serialization."""

    def __init__(self, redis_url: str = "redis://localhost:6379", default_ttl: int = 3600):
        if not REDIS_AVAILABLE:
            raise ImportError("Redis not available. Install with: pip install redis")

        self.default_ttl = default_ttl
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            raise

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in Redis cache with TTL."""
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value, default=str)
            self.redis_client.setex(key, ttl, serialized)
        except Exception as e:
            logger.error(f"Redis set error: {e}")

    def delete(self, key: str) -> None:
        """Delete key from Redis cache."""
        try:
            self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")

    def clear(self) -> None:
        """Clear all cache entries."""
        try:
            self.redis_client.flushdb()
        except Exception as e:
            logger.error(f"Redis clear error: {e}")


class CacheManager:
    """Unified cache manager that can use Redis or in-memory cache."""

    def __init__(self):
        self.cache = None
        self._init_cache()

    def _init_cache(self):
        """Initialize cache backend."""
        redis_url = getattr(settings, 'redis_url', None)

        if redis_url and REDIS_AVAILABLE:
            try:
                self.cache = RedisCache(redis_url)
                logger.info("Using Redis cache backend")
            except Exception as e:
                logger.warning(f"Redis unavailable, falling back to in-memory cache: {e}")
                self.cache = InMemoryCache()
        else:
            self.cache = InMemoryCache()
            logger.info("Using in-memory cache backend")

    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        # Create a unique key based on all arguments
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}:{key_hash}"

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return self.cache.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        self.cache.set(key, value, ttl)

    def delete(self, key: str) -> None:
        """Delete key from cache."""
        self.cache.delete(key)

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()


# Global cache manager instance
cache_manager = CacheManager()


def cached(prefix: str, ttl: Optional[int] = None):
    """
    Decorator for caching function results.

    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds (optional)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_manager.generate_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result

            # Execute function and cache result
            logger.debug(f"Cache miss for key: {cache_key}")
            result = func(*args, **kwargs)

            # Cache the result
            cache_manager.set(cache_key, result, ttl)

            return result

        return wrapper
    return decorator


def cache_astrological_subject(ttl: int = 7200):  # 2 hours default
    """Specific decorator for astrological subject caching."""
    return cached("astro_subject", ttl)


def cache_natal_chart(ttl: int = 14400):  # 4 hours default
    """Specific decorator for natal chart caching."""
    return cached("natal_chart", ttl)


def cache_transits(ttl: int = 1800):  # 30 minutes default
    """Specific decorator for transit calculations caching."""
    return cached("transits", ttl)