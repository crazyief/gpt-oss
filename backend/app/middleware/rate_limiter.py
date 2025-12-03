"""
Rate limiting middleware for API protection.

Implements pluggable rate limiting to prevent DoS attacks and resource exhaustion.

Supports two backends:
- Memory (default): Fast, single-instance, resets on restart
- Redis: Distributed, persistent, multi-instance support

RATE LIMITING STRATEGIES:
- Per-IP: Default, protects against DoS from single source
- Per-User: Optional, for authenticated users with higher/lower quotas
- Combined: Both IP and user limits (for premium users with dedicated quotas)

CONFIGURATION:
    RATE_LIMITER_BACKEND = "memory" | "redis"
    REDIS_URL = "redis://localhost:6379/0"  (required if using redis)

FIXED (Issue-11: No Rate Limiting):
===================================
Added basic rate limiting middleware with configurable limits per endpoint.

STAGE 3 IMPROVEMENTS:
- Added Redis adapter for distributed deployments
- Pluggable adapter pattern for easy testing
- Rate limit headers (X-RateLimit-Limit, X-RateLimit-Remaining)
- Per-user rate limiting support (Phase 6.2)
"""

import logging
from typing import Optional, Tuple
from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.middleware.rate_limiter_adapters import (
    RateLimiterAdapter,
    get_rate_limiter_adapter,
)

logger = logging.getLogger(__name__)


# User tier definitions for per-user rate limiting
# Tiers can be extended for premium/enterprise users
USER_TIERS = {
    "anonymous": {
        "multiplier": 1.0,  # Base rate limits
        "description": "Anonymous/unauthenticated users",
    },
    "free": {
        "multiplier": 1.5,  # 50% higher limits for registered users
        "description": "Free tier registered users",
    },
    "premium": {
        "multiplier": 3.0,  # 3x limits for premium users
        "description": "Premium tier users",
    },
    "enterprise": {
        "multiplier": 10.0,  # 10x limits for enterprise
        "description": "Enterprise tier users",
    },
}


class RateLimiter:
    """
    Rate limiter with pluggable storage backend.

    Supports:
    - Memory backend (default): Single-instance, fast, resets on restart
    - Redis backend: Distributed, persistent, multi-instance

    Rate limit rules are endpoint-specific:
    - Chat endpoint (expensive LLM calls): Low limit
    - List endpoints (cheap DB queries): High limit
    """

    def __init__(self, adapter: RateLimiterAdapter):
        """
        Initialize rate limiter with storage adapter.

        Args:
            adapter: Storage backend (Memory or Redis)
        """
        self._adapter = adapter

        # Rate limit rules: {endpoint_pattern: (max_requests, window_seconds)}
        # WHY different limits per endpoint:
        # - Chat endpoint is expensive (LLM calls) → moderate limit
        # - CRUD endpoints are cheap (database queries) → high limit
        # - Messages endpoint is frequent (polling) → lower limit
        self.limits = {
            "/api/chat": (30, 60),  # 30 chat requests per minute
            "/api/conversations": (120, 60),  # 120 conversation ops per minute
            "/api/projects": (120, 60),  # 120 project ops per minute
            "/api/messages": (200, 60),  # 200 message ops per minute
            "/api/documents": (60, 60),  # 60 document ops per minute
            "default": (200, 60),  # Default: 200 requests per minute
        }

    def check_rate_limit(
        self,
        client_ip: str,
        endpoint: str,
        user_id: Optional[str] = None,
        user_tier: str = "anonymous"
    ) -> Tuple[bool, int, int]:
        """
        Check if client exceeds rate limit.

        Supports both IP-based and user-based rate limiting:
        - IP-based: Default for all requests
        - User-based: For authenticated users with tier-specific limits

        Args:
            client_ip: Client IP address
            endpoint: API endpoint path
            user_id: Optional user ID for per-user rate limiting
            user_tier: User tier for rate limit multiplier (anonymous, free, premium, enterprise)

        Returns:
            Tuple of (allowed: bool, remaining: int, limit: int)
            - allowed: True if request should be allowed
            - remaining: Number of requests remaining in current window
            - limit: Maximum requests allowed in window
        """
        # Find matching limit rule
        limit_rule = "default"
        for pattern in self.limits.keys():
            if pattern != "default" and pattern in endpoint:
                limit_rule = pattern
                break

        base_max_requests, window_seconds = self.limits[limit_rule]

        # Apply tier multiplier for authenticated users
        tier_config = USER_TIERS.get(user_tier, USER_TIERS["anonymous"])
        max_requests = int(base_max_requests * tier_config["multiplier"])

        # Generate storage key based on authentication status
        if user_id:
            # User-based rate limiting (more generous, tied to account)
            key = f"user:{user_id}:{endpoint}"
        else:
            # IP-based rate limiting (default for anonymous)
            key = f"ip:{client_ip}:{endpoint}"

        # Delegate to adapter
        allowed, remaining = self._adapter.check_and_increment(
            key, max_requests, window_seconds
        )

        return allowed, remaining, max_requests

    def get_user_limits(self, user_tier: str = "anonymous") -> dict:
        """
        Get rate limits for a user tier.

        Args:
            user_tier: User tier name

        Returns:
            Dictionary of endpoint limits for the tier
        """
        tier_config = USER_TIERS.get(user_tier, USER_TIERS["anonymous"])
        multiplier = tier_config["multiplier"]

        return {
            endpoint: int(limit[0] * multiplier)
            for endpoint, limit in self.limits.items()
        }

    def cleanup_old_entries(self) -> int:
        """
        Periodic cleanup of expired entries to prevent memory leaks.

        Returns:
            Number of entries removed (0 for Redis, >0 for memory)
        """
        return self._adapter.cleanup()


def _create_rate_limiter() -> RateLimiter:
    """
    Factory function to create rate limiter with configured backend.

    Reads configuration from settings module.
    Falls back to memory backend if Redis configuration fails.
    """
    from app.config import settings

    backend = getattr(settings, "RATE_LIMITER_BACKEND", "memory")
    redis_url = getattr(settings, "REDIS_URL", None)

    try:
        adapter = get_rate_limiter_adapter(backend, redis_url)
        logger.info(f"Rate limiter initialized with {backend} backend")
        return RateLimiter(adapter)
    except Exception as e:
        logger.warning(
            f"Failed to initialize {backend} rate limiter, falling back to memory: {e}"
        )
        adapter = get_rate_limiter_adapter("memory")
        return RateLimiter(adapter)


# Global rate limiter instance (lazy initialization)
# WHY global: Single instance across all requests for accurate counting
_rate_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
    """Get or create the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = _create_rate_limiter()
    return _rate_limiter


# Legacy alias for backward compatibility
# Use get_rate_limiter() function for new code
rate_limiter = None  # Will be set on first access via middleware


def get_client_ip(request: Request) -> str:
    """
    SECURITY FIX (SEC-002): Extract client IP with X-Forwarded-For validation.

    Only trusts X-Forwarded-For header when request comes from a known proxy.
    This prevents IP spoofing attacks where malicious clients add fake
    X-Forwarded-For headers to bypass rate limiting.

    Args:
        request: FastAPI request

    Returns:
        str: Client IP address

    Security Notes:
        - Without validation, attackers can spoof any IP by setting X-Forwarded-For
        - We only trust the header when the direct connection comes from a proxy
        - In production, add your nginx/cloudflare IPs to settings.TRUSTED_PROXIES
    """
    from app.config import settings

    # SEC-M02 FIX: Handle None client (can occur behind certain reverse proxies)
    # WHY this check: In some proxy configurations (nginx, AWS ALB, Cloudflare),
    # request.client can be None. Without this check, we'd get AttributeError.
    client_ip = request.client.host if request.client else "unknown"

    # Only trust X-Forwarded-For from known proxies
    if client_ip in settings.TRUSTED_PROXIES and "x-forwarded-for" in request.headers:
        # SECURITY FIX: Get the leftmost IP (actual client)
        # Format: X-Forwarded-For: client, proxy1, proxy2
        # The first IP is the original client, subsequent are proxies
        # WHY first IP: The client IP is always first in the chain.
        # Proxies append their IP, so last IP is the closest proxy, not the client.
        forwarded_ips = [ip.strip() for ip in request.headers["x-forwarded-for"].split(",")]
        if forwarded_ips:
            client_ip = forwarded_ips[0]  # First IP = actual client

    return client_ip


def get_user_info(request: Request) -> Tuple[Optional[str], str]:
    """
    Extract user ID and tier from request.

    When authentication is implemented, this function will:
    1. Check for auth token (JWT, session, API key)
    2. Validate token and extract user ID
    3. Look up user tier from database

    SECURITY: Header-based tier override is DISABLED in production.
    Only allowed in development mode with explicit flag.

    Args:
        request: FastAPI request

    Returns:
        Tuple of (user_id: Optional[str], user_tier: str)
    """
    from app.config import settings

    # SECURITY FIX: Only allow header-based override in development
    # This prevents attackers from bypassing rate limits by spoofing headers
    if getattr(settings, 'DEBUG', False) and getattr(settings, 'ALLOW_TEST_HEADERS', False):
        user_id = request.headers.get("X-User-ID")
        user_tier = request.headers.get("X-User-Tier", "anonymous")
        if user_tier not in USER_TIERS:
            user_tier = "anonymous"
        return user_id, user_tier

    # Production: Always return anonymous until proper auth is implemented
    # TODO (Stage 6): Implement proper authentication check
    return None, "anonymous"


async def rate_limit_middleware(request: Request, call_next):
    """
    FastAPI middleware to enforce rate limits.

    Flow:
    1. Extract client IP (with spoofing protection)
    2. Extract user info (for per-user rate limiting)
    3. Check rate limit (IP-based or user-based)
    4. If exceeded, return 429 Too Many Requests
    5. Otherwise, process request and add rate limit headers

    Args:
        request: FastAPI request
        call_next: Next middleware/endpoint handler

    Returns:
        Response or HTTP 429 if rate limited
    """
    # SECURITY FIX (SEC-002): Get client IP with X-Forwarded-For validation
    client_ip = get_client_ip(request)

    # Get user info for per-user rate limiting
    user_id, user_tier = get_user_info(request)

    # Get endpoint path
    endpoint = request.url.path

    # Get rate limiter instance (lazy initialization)
    limiter = get_rate_limiter()

    # Check rate limit (supports both IP and user-based)
    allowed, remaining, limit = limiter.check_rate_limit(
        client_ip, endpoint, user_id, user_tier
    )

    if not allowed:
        # Rate limit exceeded
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded. Please try again later.",
                "error_type": "rate_limit_error",
                "user_tier": user_tier,
                "limit": limit,
            },
            headers={
                "Retry-After": "60",  # Suggest retry after 60 seconds
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Tier": user_tier,
            },
        )

    # Process request
    response = await call_next(request)

    # Add rate limit headers (informational)
    # WHY useful: Clients can see their rate limit status
    response.headers["X-RateLimit-Limit"] = str(limit)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Tier"] = user_tier

    return response
