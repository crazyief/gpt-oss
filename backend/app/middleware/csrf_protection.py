"""
SECURITY FIX (SEC-003): CSRF protection middleware.

This is a STAGE 1 INTERIM SOLUTION that provides basic CSRF protection without
breaking the existing frontend application.

CURRENT IMPLEMENTATION:
- Validates Origin/Referer headers for state-changing requests (POST/PUT/DELETE)
- Ensures requests come from allowed origins (same as CORS policy)
- Lightweight, no token management required
- Compatible with existing frontend code

LIMITATIONS:
- Does not protect against attacks from same-origin (e.g., XSS injected scripts)
- Relies on browser-provided headers (can be stripped by some proxies)
- Not suitable for cookie-based authentication (we don't use cookies yet)

STAGE 2 UPGRADE PATH:
- Add fastapi-csrf-protect with proper token-based CSRF protection
- Frontend must fetch CSRF token from /api/csrf-token endpoint
- Include token in X-CSRF-Token header for all state-changing requests
- More robust but requires frontend changes

WHY this approach for Stage 1:
- Provides immediate protection against basic CSRF attacks
- No frontend changes required (won't break existing app)
- Easy to upgrade to token-based CSRF in Stage 2
- Better than no protection at all
"""

import logging
from urllib.parse import urlparse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from typing import Callable

logger = logging.getLogger(__name__)


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    Basic CSRF protection via Origin/Referer validation.

    Validates that state-changing requests (POST/PUT/DELETE) come from
    allowed origins. This prevents external sites from making requests
    to our API on behalf of users.

    Attributes:
        allowed_origins: Set of origins allowed to make requests
        protected_methods: HTTP methods that require CSRF protection
    """

    def __init__(self, app, allowed_origins: list[str]):
        super().__init__(app)
        # Parse origins to get just the scheme://host:port part
        self.allowed_origins = {self._parse_origin(origin) for origin in allowed_origins}
        self.protected_methods = {"POST", "PUT", "DELETE", "PATCH"}
        logger.info(f"CSRF protection initialized for origins: {self.allowed_origins}")

    def _parse_origin(self, origin: str) -> str:
        """
        Parse origin URL to get scheme://host:port format.

        Args:
            origin: Full origin URL (e.g., http://localhost:3000)

        Returns:
            Normalized origin string
        """
        parsed = urlparse(origin)
        # Include port if non-standard
        if parsed.port:
            return f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
        return f"{parsed.scheme}://{parsed.hostname}"

    def _get_request_origin(self, request: Request) -> str | None:
        """
        Extract origin from request headers.

        Checks Origin header first (modern browsers), falls back to Referer.

        Args:
            request: FastAPI request

        Returns:
            Origin string or None if not found
        """
        # Prefer Origin header (added by browsers for POST/PUT/DELETE)
        if origin := request.headers.get("origin"):
            return self._parse_origin(origin)

        # Fallback to Referer header
        if referer := request.headers.get("referer"):
            return self._parse_origin(referer)

        return None

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Validate CSRF protection for state-changing requests.

        Args:
            request: FastAPI request
            call_next: Next middleware/endpoint handler

        Returns:
            Response or HTTP 403 if CSRF validation fails

        Flow:
            1. Skip validation for safe methods (GET, HEAD, OPTIONS)
            2. Extract origin from request headers
            3. Validate origin is in allowed list
            4. Allow request if valid, reject with 403 if not
        """
        # Skip CSRF check for safe methods
        if request.method not in self.protected_methods:
            return await call_next(request)

        # Skip CSRF check for health endpoint (monitoring systems don't send Origin)
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)

        # Get request origin
        request_origin = self._get_request_origin(request)

        # Reject requests without origin (missing Origin AND Referer)
        if not request_origin:
            logger.warning(
                f"CSRF: Missing Origin/Referer header for {request.method} {request.url.path} "
                f"from {request.client.host}"
            )
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "CSRF validation failed: Missing Origin/Referer header",
                    "error_type": "csrf_error",
                },
            )

        # Validate origin is allowed
        if request_origin not in self.allowed_origins:
            logger.warning(
                f"CSRF: Invalid origin '{request_origin}' for {request.method} {request.url.path} "
                f"from {request.client.host}. Allowed: {self.allowed_origins}"
            )
            return JSONResponse(
                status_code=403,
                content={
                    "detail": f"CSRF validation failed: Origin '{request_origin}' not allowed",
                    "error_type": "csrf_error",
                },
            )

        # Origin validated, allow request
        return await call_next(request)
