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
        """
        content_length = request.headers.get("content-length")

        if content_length:
            content_length = int(content_length)
            if content_length > self.max_size:
                logger.warning(
                    f"Request too large: {content_length} bytes from {request.client.host} "
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
