"""
Cache backend implementations.

Provides pluggable backends for caching:
- MemoryCacheBackend: In-memory LRU cache with TTL (single-instance)
- RedisCacheBackend: Redis-backed distributed cache (production)
"""

import time
import fnmatch
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional
from threading import Lock

logger = logging.getLogger(__name__)


class CacheBackend(ABC):
    """Abstract base class for cache backends."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache with TTL (seconds)."""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        pass

    @abstractmethod
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern. Returns count deleted."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all cached values."""
        pass

    @abstractmethod
    def get_stats(self) -> dict:
        """Get cache statistics."""
        pass


class MemoryCacheBackend(CacheBackend):
    """
    In-memory cache backend with TTL support.

    Suitable for single-instance deployments or development.
    For multi-instance production, use RedisCacheBackend.

    Thread-safe implementation using Lock.

    Attributes:
        _cache: Dictionary storing {key: (value, expiry_timestamp)}
        _lock: Threading lock for thread-safe access
        _hits: Counter for cache hits
        _misses: Counter for cache misses
    """

    def __init__(self, max_size: int = 1000):
        """
        Initialize memory cache.

        Args:
            max_size: Maximum number of entries (LRU eviction when exceeded)
        """
        self._cache: dict[str, tuple[Any, float]] = {}
        self._lock = Lock()
        self._max_size = max_size
        self._hits = 0
        self._misses = 0
        self._access_order: list[str] = []  # For LRU tracking

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Returns None if key doesn't exist or has expired.
        Updates LRU order on hit.
        """
        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self._misses += 1
                return None

            value, expiry = entry

            if time.time() > expiry:
                # Entry expired, remove it
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)
                self._misses += 1
                return None

            # Cache hit - update LRU order
            self._hits += 1
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)

            return value

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """
        Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache (must be serializable)
            ttl: Time-to-live in seconds (default: 5 minutes)
        """
        with self._lock:
            # Evict LRU entries if at capacity
            while len(self._cache) >= self._max_size:
                if self._access_order:
                    oldest_key = self._access_order.pop(0)
                    if oldest_key in self._cache:
                        del self._cache[oldest_key]
                else:
                    # Fallback: remove arbitrary entry
                    self._cache.popitem()

            expiry = time.time() + ttl
            self._cache[key] = (value, expiry)

            # Update LRU order
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)

    def delete(self, key: str) -> None:
        """Delete value from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching glob pattern.

        Args:
            pattern: Glob pattern (e.g., "projects:*", "user:123:*")

        Returns:
            Number of keys deleted
        """
        with self._lock:
            keys_to_delete = [
                k for k in self._cache.keys()
                if fnmatch.fnmatch(k, pattern)
            ]

            for key in keys_to_delete:
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)

            count = len(keys_to_delete)
            if count > 0:
                logger.debug(f"Invalidated {count} cache entries matching '{pattern}'")

            return count

    def clear(self) -> None:
        """Clear all cached values."""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
            logger.info("Cache cleared")

    def get_stats(self) -> dict:
        """Get cache statistics."""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0

            return {
                "type": "memory",
                "entries": len(self._cache),
                "max_size": self._max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": f"{hit_rate:.1f}%"
            }

    def cleanup_expired(self) -> int:
        """
        Remove expired entries.

        Called periodically to prevent memory leaks.

        Returns:
            Number of entries removed
        """
        with self._lock:
            now = time.time()
            expired_keys = [
                k for k, (v, expiry) in self._cache.items()
                if now > expiry
            ]

            for key in expired_keys:
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)

            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

            return len(expired_keys)


class RedisCacheBackend(CacheBackend):
    """
    Redis cache backend for production deployments.

    Supports multi-instance deployments with shared cache.
    Requires redis-py package and running Redis server.

    Configuration via environment variables:
        REDIS_URL: Redis connection URL (e.g., redis://localhost:6379/0)
    """

    def __init__(self, redis_url: str):
        """
        Initialize Redis cache.

        Args:
            redis_url: Redis connection URL
        """
        try:
            import redis
            self._redis = redis.from_url(redis_url, decode_responses=True)
            self._redis.ping()  # Test connection
            self._available = True
            logger.info(f"Redis cache connected: {redis_url}")
        except ImportError:
            logger.warning("redis-py not installed, falling back to memory cache")
            self._available = False
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}, falling back to memory cache")
            self._available = False

    @property
    def available(self) -> bool:
        """Check if Redis is available."""
        return self._available

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis."""
        if not self._available:
            return None

        import json
        try:
            value = self._redis.get(f"gptoss:{key}")
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in Redis with TTL."""
        if not self._available:
            return

        import json
        try:
            self._redis.setex(
                f"gptoss:{key}",
                ttl,
                json.dumps(value, default=str)
            )
        except Exception as e:
            logger.error(f"Redis set error: {e}")

    def delete(self, key: str) -> None:
        """Delete value from Redis."""
        if not self._available:
            return

        try:
            self._redis.delete(f"gptoss:{key}")
        except Exception as e:
            logger.error(f"Redis delete error: {e}")

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        if not self._available:
            return 0

        try:
            keys = list(self._redis.scan_iter(f"gptoss:{pattern}"))
            if keys:
                self._redis.delete(*keys)
            return len(keys)
        except Exception as e:
            logger.error(f"Redis invalidate_pattern error: {e}")
            return 0

    def clear(self) -> None:
        """Clear all GPT-OSS keys from Redis."""
        if not self._available:
            return

        try:
            keys = list(self._redis.scan_iter("gptoss:*"))
            if keys:
                self._redis.delete(*keys)
            logger.info(f"Cleared {len(keys)} cache entries")
        except Exception as e:
            logger.error(f"Redis clear error: {e}")

    def get_stats(self) -> dict:
        """Get Redis cache statistics."""
        if not self._available:
            return {"type": "redis", "status": "unavailable"}

        try:
            info = self._redis.info("stats")
            return {
                "type": "redis",
                "status": "connected",
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "keys": self._redis.dbsize()
            }
        except Exception as e:
            return {"type": "redis", "status": "error", "error": str(e)}
