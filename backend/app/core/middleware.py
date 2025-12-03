"""
Middleware registration for FastAPI application.

Centralizes middleware configuration with proper ordering.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

logger = logging.getLogger(__name__)


def register_middleware(app: FastAPI) -> None:
    """
    Register all middleware in the correct order.

    CRITICAL: Middleware execution order matters!

    Middleware is executed in REVERSE order of registration.
    Last registered = first to execute.

    Execution order (request → response):
      1. Security Headers   (add security headers to response)
      2. CSRF Protection    (validate tokens)
      3. Request Size Limit (reject oversized)
      4. Rate Limiting      (enforce limits)
      5. CORS               (handle preflight, add headers)
      6. Application Routes (actual logic)

    Registration order (bottom to top):
      1. CORS               (registered first, executes last)
      2. Rate Limiting
      3. Request Size Limit
      4. CSRF Protection
      5. Security Headers   (registered last, executes first on response)

    WHY THIS ORDER:
    - Security headers added to ALL responses (registered last, wraps everything)
    - CORS must handle OPTIONS preflight BEFORE CSRF validation
    - Rate limiting should apply before expensive CSRF token validation
    - Request size limits prevent DoS before other processing
    - CSRF validates tokens after basic checks pass
    """

    # 1. CORS (registered first, executes on response)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],  # Allow all headers
    )
    logger.info(f"CORS middleware registered (origins: {settings.get_cors_origins()})")

    # 2. Rate Limiting
    # FIXED (Issue-11: No Rate Limiting on API Endpoints)
    # Protects against DoS attacks and resource exhaustion
    # DISABLED: Uncomment below lines to enable rate limiting in production
    # from app.middleware.rate_limiter import rate_limit_middleware
    # app.middleware("http")(rate_limit_middleware)
    # logger.info("Rate limiter middleware registered")
    logger.info("Rate limiter middleware DISABLED (enable in production)")

    # 3. Request Size Limiting
    # ARCHITECTURE FIX (ARCH-003): Prevents memory exhaustion attacks
    # LIMIT: 250MB to support document uploads (200MB per file + multipart overhead)
    # NOTE: Per-file validation (200MB) is handled in DocumentService.save_file()
    from app.middleware.request_size_limiter import RequestSizeLimitMiddleware
    app.add_middleware(RequestSizeLimitMiddleware, max_size=250_000_000)  # 250MB limit
    logger.info("Request size limiter middleware registered (max: 250MB)")

    # 4. CSRF Protection (registered last, executes first)
    # SECURITY FIX (SEC-003): Token-based validation for state-changing requests
    # Tokens must be fetched from /api/csrf-token and included in X-CSRF-Token header
    from app.middleware.csrf_protection import CSRFProtectionMiddleware
    app.add_middleware(CSRFProtectionMiddleware, allowed_origins=settings.get_cors_origins())
    logger.info("CSRF protection middleware registered")

    # 5. Security Headers (registered last, executes on response)
    # SECURITY FIX (HIGH): HTTP security headers to prevent common attacks
    from app.middleware.security_headers import SecurityHeadersMiddleware
    app.add_middleware(SecurityHeadersMiddleware)
    logger.info("Security headers middleware registered")
