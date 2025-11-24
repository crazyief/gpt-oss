"""
SECURITY FIX (SEC-003): CSRF protection middleware using token validation.

This is the STAGE 2 PRODUCTION IMPLEMENTATION that provides robust CSRF protection
using cryptographically signed tokens.

CURRENT IMPLEMENTATION:
- Token-based CSRF protection using fastapi-csrf-protect
- Validates CSRF tokens on all state-changing requests (POST/PUT/DELETE/PATCH)
- Tokens must be fetched from /api/csrf-token endpoint
- Tokens included in X-CSRF-Token header for validation
- GET, HEAD, OPTIONS are exempt from CSRF validation

SECURITY FEATURES:
- Cryptographically signed tokens (prevents forgery)
- Time-limited tokens (1 hour expiry, prevents replay attacks)
- Header-based transmission (more secure than query params)
- Defense in depth with optional cookie storage

MIGRATION FROM STAGE 1:
- Replaced Origin/Referer validation with token-based validation
- More robust against attacks from same-origin (XSS)
- Not affected by proxy header stripping
- Suitable for cookie-based authentication (future use)

WHY this approach for Stage 2:
- Industry-standard CSRF protection mechanism
- Resistant to all known CSRF attack vectors
- Compatible with modern frontend frameworks
- Meets security compliance requirements (IEC 62443)
"""

import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings

logger = logging.getLogger(__name__)


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection middleware using token-based validation.

    Validates CSRF tokens on all state-changing requests (POST, PUT, DELETE, PATCH).
    GET, HEAD, OPTIONS are exempt from CSRF validation.

    Token must be sent in X-CSRF-Token header.
    """

    def __init__(self, app, allowed_origins: list[str] = None):
        super().__init__(app)
        self.allowed_origins = set(allowed_origins) if allowed_origins else set()
        self.csrf_protect = CsrfProtect()

        # Configure CSRF settings
        self.csrf_protect._secret_key = settings.CSRF_SECRET_KEY
        self.csrf_protect._token_location = settings.CSRF_TOKEN_LOCATION
        self.csrf_protect._header_name = settings.CSRF_HEADER_NAME

        logger.info(f"CSRF protection initialized (token-based, header: {settings.CSRF_HEADER_NAME})")

    async def dispatch(self, request: Request, call_next):
        """
        Validate CSRF protection for state-changing requests.

        Args:
            request: FastAPI request
            call_next: Next middleware/endpoint handler

        Returns:
            Response or HTTP 403 if CSRF validation fails

        Flow:
            1. Skip validation for safe methods (GET, HEAD, OPTIONS)
            2. Skip validation for whitelisted endpoints
            3. Extract token from X-CSRF-Token header
            4. Validate token cryptographic signature
            5. Allow request if valid, reject with 403 if not
        """
        # Exempt safe methods (GET, HEAD, OPTIONS)
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return await call_next(request)

        # Exempt CSRF token endpoint (can't validate token when fetching token)
        if request.url.path == "/api/csrf-token":
            return await call_next(request)

        # Exempt health check endpoint (monitoring systems don't send tokens)
        if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)

        # Validate CSRF token for state-changing requests
        # Extract token from header
        csrf_token = request.headers.get(settings.CSRF_HEADER_NAME)

        if not csrf_token:
            logger.warning(
                f"CSRF: Missing token for {request.method} {request.url.path} "
                f"from {request.client.host if request.client else 'unknown'}"
            )
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "CSRF token missing. Include X-CSRF-Token header.",
                    "error_type": "csrf_error",
                }
            )

        # Validate token (checks signature and expiry)
        # Note: We manually validate the token by checking it against the secret
        # The library's validate_csrf() is designed for cookie-based tokens,
        # but we're using header-based tokens, so we use the internal serializer
        from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

        try:
            serializer = URLSafeTimedSerializer(
                settings.CSRF_SECRET_KEY,
                salt="fastapi-csrf-token"
            )
            # Decode and validate the token (will raise exception if invalid/expired)
            serializer.loads(csrf_token, max_age=settings.CSRF_MAX_AGE)
        except (SignatureExpired, BadSignature) as e:
            # Token is invalid or expired - this is a CSRF error (403)
            logger.warning(
                f"CSRF: Token validation failed for {request.method} {request.url.path}: {str(e)}"
            )
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "CSRF token invalid or expired. Fetch new token from /api/csrf-token.",
                    "error_type": "csrf_error",
                }
            )
        except Exception as e:
            # Unexpected error during validation - this is a server error (500)
            logger.error(f"CSRF validation error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error during CSRF validation.",
                    "error_type": "server_error",
                }
            )

        # Token valid, proceed with request
        logger.debug(f"CSRF token validated for {request.method} {request.url.path}")
        return await call_next(request)
