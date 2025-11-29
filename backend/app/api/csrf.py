"""CSRF token management endpoints."""

from fastapi import APIRouter, Response, HTTPException, Depends
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from pydantic import BaseModel
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["csrf"])


class CsrfSettings(BaseModel):
    """CSRF configuration model for fastapi-csrf-protect."""
    secret_key: str = settings.CSRF_SECRET_KEY
    token_location: str = settings.CSRF_TOKEN_LOCATION
    cookie_name: str = settings.CSRF_COOKIE_NAME
    header_name: str = settings.CSRF_HEADER_NAME
    max_age: int = settings.CSRF_MAX_AGE


@CsrfProtect.load_config
def get_csrf_config():
    """Load CSRF configuration."""
    return CsrfSettings()


@router.get("/csrf-token")
async def get_csrf_token(response: Response, csrf_protect: CsrfProtect = Depends()):
    """
    Generate and return a CSRF token.

    The token is returned in the response body as JSON and optionally
    set as a cookie for additional protection.

    Returns:
        dict: {"csrf_token": "generated-token"}

    Raises:
        HTTPException: If token generation fails
    """
    try:
        # Generate CSRF token
        # Note: generate_csrf() returns a tuple (unsigned_token, signed_token)
        # We use the signed token (second element) for validation
        csrf_token_tuple = csrf_protect.generate_csrf()

        # Extract the signed token (second element)
        if isinstance(csrf_token_tuple, (list, tuple)) and len(csrf_token_tuple) >= 2:
            csrf_token = csrf_token_tuple[1]  # Use signed token
        else:
            # Single token case (fallback for different library versions)
            csrf_token = csrf_token_tuple

        # Optionally set as cookie (defense in depth)
        # SECURITY FIX: secure=True in production (HTTPS required)
        response.set_cookie(
            key=settings.CSRF_COOKIE_NAME,
            value=csrf_token,
            max_age=settings.CSRF_MAX_AGE,
            httponly=True,  # Prevent JavaScript access
            samesite="lax",  # CSRF protection
            secure=not settings.DEBUG  # True in production (HTTPS), False in dev (HTTP)
        )

        logger.debug("CSRF token generated successfully")
        return {"csrf_token": csrf_token}

    except CsrfProtectError as e:
        logger.error(f"CSRF token generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"CSRF token generation failed: {str(e)}"
        )
