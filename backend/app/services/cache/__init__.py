"""
Cache module for GPT-OSS backend.

Provides caching functionality with pluggable backends:
- MemoryCacheBackend: In-memory LRU cache with TTL (single-instance)
- RedisCacheBackend: Redis-backed distributed cache (production)

Usage:
    from app.services.cache import cache_service, cached, invalidate_on_change

    # Direct cache operations
    cache_service.set("key", value, ttl=300)
    value = cache_service.get("key")

    # Decorator-based caching
    @cached("projects:{project_id}", ttl=300)
    def get_project(db, project_id: int):
        return db.query(Project).filter_by(id=project_id).first()

    # Cache invalidation on mutation
    @invalidate_on_change("projects:list", "projects:{project_id}")
    def update_project(db, project_id: int, data):
        # Update logic...
"""

from app.services.cache.service import cache_service, CacheService
from app.services.cache.backends import (
    CacheBackend,
    MemoryCacheBackend,
    RedisCacheBackend,
)
from app.services.cache.decorators import cached, invalidate_on_change

__all__ = [
    # Service
    "cache_service",
    "CacheService",
    # Backends
    "CacheBackend",
    "MemoryCacheBackend",
    "RedisCacheBackend",
    # Decorators
    "cached",
    "invalidate_on_change",
]
