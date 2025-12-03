"""
Cache decorators for function memoization and invalidation.

Provides:
- @cached: Decorator to cache function results
- @invalidate_on_change: Decorator to invalidate cache after mutation
"""

import logging
from functools import wraps
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

# Type variable for generic return type
T = TypeVar('T')


def cached(key_pattern: str, ttl: int = 300) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for caching function results.

    Args:
        key_pattern: Cache key pattern with {arg} placeholders
                     e.g., "projects:{project_id}"
        ttl: Time-to-live in seconds

    Example:
        @cached("projects:{project_id}", ttl=300)
        def get_project(db, project_id: int):
            return db.query(Project).filter_by(id=project_id).first()

    Returns:
        Decorated function with caching
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Import here to avoid circular imports
            from app.services.cache.service import cache_service

            # Build cache key from function arguments
            # Skip 'db' argument (first positional or keyword arg)
            cache_kwargs = kwargs.copy()

            # Map positional args to parameter names (skip first arg assumed to be db)
            import inspect
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())

            for i, arg in enumerate(args):
                if i < len(params):
                    if params[i] != 'db':
                        cache_kwargs[params[i]] = arg

            # Format cache key
            try:
                cache_key = key_pattern.format(**cache_kwargs)
            except KeyError:
                # If key formatting fails, skip caching
                return func(*args, **kwargs)

            # Try cache first
            cached_value = cache_service.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value

            # Cache miss - execute function
            result = func(*args, **kwargs)

            # Cache the result
            if result is not None:
                cache_service.set(cache_key, result, ttl)
                logger.debug(f"Cache set: {cache_key}")

            return result

        return wrapper
    return decorator


def invalidate_on_change(*patterns: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to invalidate cache patterns after function execution.

    Args:
        *patterns: Cache key patterns to invalidate

    Example:
        @invalidate_on_change("projects:list", "projects:{project_id}")
        def update_project(db, project_id: int, data):
            # Update logic...

    Returns:
        Decorated function with cache invalidation
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Import here to avoid circular imports
            from app.services.cache.service import cache_service

            result = func(*args, **kwargs)

            # Build pattern args from function arguments
            import inspect
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())

            pattern_kwargs = kwargs.copy()
            for i, arg in enumerate(args):
                if i < len(params):
                    pattern_kwargs[params[i]] = arg

            # Invalidate each pattern
            for pattern in patterns:
                try:
                    formatted_pattern = pattern.format(**pattern_kwargs)
                    cache_service.invalidate_pattern(formatted_pattern)
                except KeyError:
                    # If pattern formatting fails, invalidate as-is
                    cache_service.invalidate_pattern(pattern)

            return result

        return wrapper
    return decorator
