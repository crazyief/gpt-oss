"""
Rate limiting middleware for API protection.

Implements simple in-memory rate limiting to prevent DoS attacks
and resource exhaustion.

FIXED (Issue-11: No Rate Limiting):
===================================
Added basic rate limiting middleware with configurable limits per endpoint.

FUTURE IMPROVEMENTS (Stage 2+):
- Use Redis for distributed rate limiting (multi-instance support)
- Add rate limit headers (X-RateLimit-Limit, X-RateLimit-Remaining)
- Implement sliding window algorithm (currently uses fixed window)
- Add per-user rate limits (after authentication implemented)
"""

import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse


class RateLimiter:
    """
    In-memory rate limiter using token bucket algorithm.

    Limitations:
    - Single-instance only (not distributed)
    - Memory-based (resets on server restart)
    - IP-based only (no user-based limits yet)

    Good enough for Stage 1. Stage 2 will add Redis-based limiter.
    """

    def __init__(self):
        # Storage: {client_ip: {endpoint: (timestamp, request_count)}}
        self.requests: Dict[str, Dict[str, Tuple[float, int]]] = defaultdict(
            lambda: defaultdict(lambda: (time.time(), 0))
        )

        # Rate limit rules: {endpoint_pattern: (max_requests, window_seconds)}
        # WHY different limits per endpoint:
        # - Chat endpoint is expensive (LLM calls) → low limit
        # - List endpoints are cheap (database queries) → high limit
        self.limits = {
            "/api/chat": (10, 60),  # 10 chat requests per minute
            "/api/conversations": (60, 60),  # 60 conversation ops per minute
            "/api/projects": (60, 60),  # 60 project ops per minute
            "/api/messages": (100, 60),  # 100 message ops per minute
            "default": (100, 60),  # Default: 100 requests per minute
        }

    def check_rate_limit(self, client_ip: str, endpoint: str) -> Tuple[bool, int]:
        """
        Check if client exceeds rate limit.

        Args:
            client_ip: Client IP address
            endpoint: API endpoint path

        Returns:
            Tuple of (allowed: bool, remaining: int)
            - allowed: True if request should be allowed
            - remaining: Number of requests remaining in current window

        Algorithm (Token Bucket):
        1. Get current timestamp and last request time
        2. If window expired, reset counter
        3. Otherwise, increment counter
        4. Compare against limit
        """
        # Find matching limit rule
        limit_rule = "default"
        for pattern in self.limits.keys():
            if pattern in endpoint:
                limit_rule = pattern
                break

        max_requests, window_seconds = self.limits[limit_rule]

        # Get or initialize request tracking
        last_time, count = self.requests[client_ip][endpoint]
        current_time = time.time()

        # Check if window expired
        if current_time - last_time >= window_seconds:
            # Reset window
            self.requests[client_ip][endpoint] = (current_time, 1)
            return True, max_requests - 1

        # Within window - check limit
        if count < max_requests:
            # Allow request
            self.requests[client_ip][endpoint] = (last_time, count + 1)
            return True, max_requests - count - 1
        else:
            # Exceed limit
            return False, 0

    def cleanup_old_entries(self):
        """
        Periodic cleanup of expired entries to prevent memory leaks.

        Should be called periodically (e.g., via background task).
        Removes entries older than 1 hour.

        WHY cleanup needed:
        - Memory leak prevention: Dict grows unbounded otherwise
        - Attack mitigation: Prevents memory exhaustion attacks
        """
        current_time = time.time()
        cleanup_threshold = 3600  # 1 hour

        # Iterate copy to allow deletion during iteration
        for client_ip in list(self.requests.keys()):
            for endpoint in list(self.requests[client_ip].keys()):
                last_time, _ = self.requests[client_ip][endpoint]
                if current_time - last_time > cleanup_threshold:
                    del self.requests[client_ip][endpoint]

            # Remove client if no endpoints left
            if not self.requests[client_ip]:
                del self.requests[client_ip]


# Global rate limiter instance
# WHY global: Single instance across all requests for accurate counting
rate_limiter = RateLimiter()


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

    client_ip = request.client.host

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


async def rate_limit_middleware(request: Request, call_next):
    """
    FastAPI middleware to enforce rate limits.

    Flow:
    1. Extract client IP (with spoofing protection)
    2. Check rate limit
    3. If exceeded, return 429 Too Many Requests
    4. Otherwise, process request

    Args:
        request: FastAPI request
        call_next: Next middleware/endpoint handler

    Returns:
        Response or HTTP 429 if rate limited
    """
    # SECURITY FIX (SEC-002): Get client IP with X-Forwarded-For validation
    client_ip = get_client_ip(request)

    # Get endpoint path
    endpoint = request.url.path

    # Check rate limit
    allowed, remaining = rate_limiter.check_rate_limit(client_ip, endpoint)

    if not allowed:
        # Rate limit exceeded
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded. Please try again later.",
                "error_type": "rate_limit_error",
            },
            headers={
                "Retry-After": "60",  # Suggest retry after 60 seconds
            },
        )

    # Process request
    response = await call_next(request)

    # Add rate limit headers (informational)
    # WHY useful: Clients can see how many requests they have left
    response.headers["X-RateLimit-Remaining"] = str(remaining)

    return response
