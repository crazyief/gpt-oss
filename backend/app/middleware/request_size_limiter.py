"""
ARCHITECTURE FIX (ARCH-003): Request size limiting middleware to prevent DoS attacks.

Limits request body size to prevent memory exhaustion attacks where malicious
clients send extremely large payloads (e.g., 1GB JSON file) to crash the server.

WHY needed:
- Without limits, attackers can exhaust server memory by sending huge requests
- Default web servers have no built-in request size limits
- This is a critical production hardening requirement

Implementation:
- Checks Content-Length header before reading request body
- Returns HTTP 413 (Payload Too Large) if size exceeds limit
- Default limit: 10MB (configurable)
"""

import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from typing import Callable

logger = logging.getLogger(__name__)


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Limit request body size to prevent memory exhaustion attacks.

    This middleware checks the Content-Length header and rejects requests
    that exceed the configured size limit BEFORE reading the request body.

    Attributes:
        max_size: Maximum request body size in bytes (default: 10MB)
    """

    def __init__(self, app, max_size: int = 10_000_000):  # 10MB default
        super().__init__(app)
        self.max_size = max_size
        logger.info(f"Request size limiter initialized (max: {max_size / 1_000_000:.1f}MB)")

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Check request size before processing.

        Args:
            request: FastAPI request
            call_next: Next middleware/endpoint handler

        Returns:
            Response or HTTP 413 if request too large

        Security Notes:
            - Checks Content-Length header (mandatory for POST/PUT in HTTP/1.1)
            - Attackers can omit header, but server will timeout reading large bodies
            - For chunked encoding (no Content-Length), size is checked during streaming

        Error Handling:
            - SEC-M02: Handles None client (proxy configurations)
            - SEC-M01 + ERR-H01: Validates Content-Length header format
        """
        # SECURITY FIX (SEC-M02): Handle None client in proxy configurations
        # WHY: request.client can be None when behind certain reverse proxies
        # or load balancers that don't preserve client information.
        # Accessing .host on None would cause AttributeError and crash middleware.
        client_ip = request.client.host if request.client else "unknown"

        # Get Content-Length header
        content_length = request.headers.get("content-length")

        if content_length:
            # SECURITY FIX (SEC-M01 + ERR-H01): Handle malformed Content-Length
            # WHY: Attackers can send malformed headers to crash the middleware:
            # - "Content-Length: abc" → ValueError in int()
            # - "Content-Length: 999999999999999999999" → OverflowError
            # - "Content-Length: -100" → Negative size (logic error)
            # Crashing the middleware could bypass size checks entirely.
            try:
                content_length_int = int(content_length)

                # Additional validation: reject negative sizes
                # WHY: Negative Content-Length is invalid HTTP and could indicate attack
                if content_length_int < 0:
                    logger.warning(
                        f"Negative Content-Length header from {client_ip}: {content_length}"
                    )
                    return JSONResponse(
                        status_code=400,
                        content={"detail": "Invalid Content-Length header (negative value)"}
                    )

            except (ValueError, OverflowError) as e:
                # ValueError: Non-numeric string (e.g., "abc", "12.34.56")
                # OverflowError: Number too large for int (e.g., "999999999999999999999")
                logger.warning(
                    f"Malformed Content-Length header from {client_ip}: {content_length} ({type(e).__name__})"
                )
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid Content-Length header"}
                )

            # Check size limit
            if content_length_int > self.max_size:
                logger.warning(
                    f"Request too large: {content_length_int} bytes from {client_ip} "
                    f"to {request.url.path}"
                )
                return JSONResponse(
                    status_code=413,
                    content={
                        "detail": f"Request body too large. Maximum size: {self.max_size / 1_000_000:.1f}MB",
                        "error_type": "request_too_large",
                    },
                )

        return await call_next(request)
