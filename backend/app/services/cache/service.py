"""
Cache service with automatic backend selection.

Provides a unified interface for caching with pluggable backends.
Uses Redis if REDIS_URL is configured, otherwise falls back to memory cache.
"""

import os
import logging
from typing import Any, Optional

from app.services.cache.backends import (
    CacheBackend,
    MemoryCacheBackend,
    RedisCacheBackend,
)

logger = logging.getLogger(__name__)


class CacheService:
    """
    Cache service with automatic backend selection.

    Uses Redis if REDIS_URL is configured, otherwise falls back to memory cache.
    Provides a consistent interface regardless of backend.

    Common cache key patterns:
        - projects:list             - List of all projects
        - projects:{id}             - Single project by ID
        - projects:{id}:stats       - Project statistics
        - conversations:{id}        - Single conversation
        - conversations:project:{id} - Conversations for a project
    """

    def __init__(self):
        """Initialize cache service with appropriate backend."""
        redis_url = os.getenv("REDIS_URL")

        if redis_url:
            redis_backend = RedisCacheBackend(redis_url)
            if redis_backend.available:
                self._backend = redis_backend
                logger.info("Using Redis cache backend")
            else:
                self._backend = MemoryCacheBackend()
                logger.info("Redis unavailable, using memory cache backend")
        else:
            self._backend = MemoryCacheBackend()
            logger.info("Using memory cache backend (set REDIS_URL for Redis)")

    @property
    def backend(self) -> CacheBackend:
        """Get the underlying cache backend."""
        return self._backend

    def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        return self._backend.get(key)

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set cached value with TTL (default: 5 minutes)."""
        self._backend.set(key, value, ttl)

    def delete(self, key: str) -> None:
        """Delete cached value."""
        self._backend.delete(key)

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        return self._backend.invalidate_pattern(pattern)

    def clear(self) -> None:
        """Clear all cached values."""
        self._backend.clear()

    def get_stats(self) -> dict:
        """Get cache statistics."""
        return self._backend.get_stats()

    def cleanup_expired(self) -> int:
        """Cleanup expired entries (memory backend only)."""
        if isinstance(self._backend, MemoryCacheBackend):
            return self._backend.cleanup_expired()
        return 0


# Singleton instance
cache_service = CacheService()
