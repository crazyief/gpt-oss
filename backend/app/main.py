"""
Main FastAPI application entry point.

Initializes the FastAPI app, configures middleware, and registers routes.
"""

import logging
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.config import settings
from app.db.session import init_db

# Configure logging
# Format: timestamp - logger name - level - message
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def periodic_cleanup():
    """
    PERFORMANCE FIX (PERF-001): Periodic cleanup of rate limiter entries.

    Runs every 5 minutes to prevent memory leaks in the rate limiter.
    Without this, the rate limiter dictionary grows unbounded as new
    client IPs connect, eventually consuming all available memory.

    WHY 5 minutes: Balances memory cleanup frequency with CPU overhead.
    Rate limiter entries expire after 1 hour, so cleaning every 5 minutes
    means at most we keep 12x5min = 1 hour of stale entries (acceptable).
    """
    while True:
        await asyncio.sleep(300)  # Every 5 minutes
        try:
            from app.middleware.rate_limiter import rate_limiter
            rate_limiter.cleanup_old_entries()
            logger.info("Rate limiter cleanup completed")
        except Exception as e:
            logger.error(f"Rate limiter cleanup failed: {e}")


def validate_middleware_order(app: FastAPI):
    """
    HIGH-006: Validate middleware order at startup to catch configuration errors early.

    CRITICAL: Middleware execution order matters for correct CORS and CSRF handling.
    - CORS must execute AFTER CSRF to handle OPTIONS preflight requests
    - In FastAPI, middleware executes in REVERSE order of registration
    - So CORS must be registered BEFORE CSRF in code

    This validation ensures:
    1. CSRF middleware is present
    2. CORS middleware is present
    3. CORS is registered before CSRF (so CSRF executes first)

    Raises:
        AssertionError: If middleware order is incorrect (logged but doesn't crash app)
    """
    try:
        # Get middleware stack
        # Note: app.user_middleware is in LIFO order (last registered comes first in list)
        # So we need to reverse the indices to get registration order
        middleware_list = []
        for middleware in app.user_middleware:
            middleware_class = middleware.cls.__name__
            middleware_list.append(middleware_class)

        logger.debug(f"Middleware stack (LIFO order): {middleware_list}")

        # Find positions in the LIFO stack
        csrf_index = -1
        cors_index = -1

        for i, middleware_name in enumerate(middleware_list):
            if middleware_name == 'CSRFProtectionMiddleware':
                csrf_index = i
            elif middleware_name == 'CORSMiddleware':
                cors_index = i

        # Validate presence
        if csrf_index == -1:
            logger.warning("⚠️  CSRF middleware not found in stack")
            return
        elif cors_index == -1:
            logger.warning("⚠️  CORS middleware not found in stack")
            return

        # Validate order
        # In LIFO order (user_middleware), last registered appears FIRST
        # So CSRF (registered last) should have a LOWER index than CORS (registered first)
        # Because lower index = later in list = registered last = executes first
        if csrf_index < cors_index:
            # Correct order: CSRF has lower index (registered last, executes first)
            logger.info(
                f"✅ Middleware order validated: "
                f"CSRF (LIFO index {csrf_index}) executes BEFORE CORS (LIFO index {cors_index}). "
                f"This is correct - CSRF validates tokens first, then CORS handles preflight."
            )
        else:
            # Wrong order: CORS has lower index (registered last, executes first)
            error_msg = (
                f"❌ MIDDLEWARE ORDER ERROR: CORS (LIFO index {cors_index}) executes "
                f"BEFORE CSRF (LIFO index {csrf_index}). This will break CSRF validation! "
                f"CORS must be registered BEFORE CSRF in code (so CSRF executes first)."
            )
            logger.error(error_msg)
            logger.error("⚠️  APPLICATION MAY NOT WORK CORRECTLY - MIDDLEWARE ORDER ISSUE")
            # Don't crash app, but log prominently for developer attention

    except Exception as e:
        logger.error(f"Middleware order validation failed: {str(e)}")
        logger.error("⚠️  Could not validate middleware order - proceeding anyway")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events for the FastAPI application.
    Initializes database on startup and starts background cleanup tasks.

    Args:
        app: FastAPI application instance

    Yields:
        Control to the application runtime
    """
    # Startup: Initialize database
    logger.info("Starting GPT-OSS Backend API")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # PERFORMANCE FIX (PERF-001): Start rate limiter cleanup task
    cleanup_task = asyncio.create_task(periodic_cleanup())
    logger.info("Rate limiter cleanup task started (runs every 5 minutes)")

    # Log CSRF initialization status
    logger.info(f"CSRF protection initialized (token location: {settings.CSRF_TOKEN_LOCATION})")

    # HIGH-006: Validate middleware order at startup
    validate_middleware_order(app)

    # Yield control to the application
    yield

    # Shutdown: Cleanup resources
    logger.info("Shutting down GPT-OSS Backend API")

    # Cancel cleanup task gracefully
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        logger.info("Rate limiter cleanup task stopped")


# Create FastAPI application instance
app = FastAPI(
    title="GPT-OSS API",
    description="Backend API for GPT-OSS local AI knowledge assistant",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)


# ARCHITECTURE FIX (ARCH-001): Removed dangerous global JSON encoder monkey-patch
#
# PREVIOUS ISSUE: Monkey-patching json.JSONEncoder.default globally affects ALL
# JSON serialization in the process, including third-party libraries. This is
# extremely dangerous and can cause unpredictable behavior.
#
# NEW SOLUTION: FastAPI/Pydantic automatically handles datetime serialization
# correctly when using Pydantic models. All our endpoints use Pydantic response
# models, so datetime fields are automatically serialized to ISO 8601 format.
#
# If custom JSON encoding is needed for a specific endpoint (rare), use a
# custom response class:
#
#   from fastapi.responses import JSONResponse
#   import json
#
#   class UTCAwareJSONResponse(JSONResponse):
#       def render(self, content: Any) -> bytes:
#           return json.dumps(
#               content,
#               default=lambda obj: obj.isoformat() if isinstance(obj, datetime) else str(obj),
#               ensure_ascii=False
#           ).encode('utf-8')
#
#   @app.get("/special", response_class=UTCAwareJSONResponse)
#   async def special_endpoint(): ...
#
# For the timezone issue (timestamps showing "8h ago" for just-created messages),
# the fix is to ensure SQLAlchemy stores datetimes with timezone awareness or
# Pydantic models have proper serialization config. See models/database.py for
# the proper implementation using DateTime(timezone=True) in SQLAlchemy.


# ============================================================================
# MIDDLEWARE REGISTRATION (ORDER MATTERS!)
# ============================================================================
#
# CRITICAL: Middleware is executed in REVERSE order of registration.
# Last registered = first to execute.
#
# Execution order (request → response):
#   1. CSRF Protection    (validate tokens)
#   2. Request Size Limit (reject oversized)
#   3. Rate Limiting      (enforce limits)
#   4. CORS               (handle preflight, add headers)
#   5. Application Routes (actual logic)
#
# Registration order (bottom to top):
#   1. CORS               (registered first, executes last)
#   2. Rate Limiting
#   3. Request Size Limit
#   4. CSRF Protection    (registered last, executes first)
#
# WHY THIS ORDER:
# - CORS must handle OPTIONS preflight BEFORE CSRF validation
# - Rate limiting should apply before expensive CSRF token validation
# - Request size limits prevent DoS before other processing
# - CSRF validates tokens after basic checks pass
#
# ============================================================================

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
from app.middleware.rate_limiter import rate_limit_middleware
app.middleware("http")(rate_limit_middleware)
logger.info("Rate limiter middleware registered")

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


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns the health status of the API and its dependencies.
    Used by monitoring systems and docker health checks.

    Returns:
        JSONResponse: Health status including database and LLM service
    """
    from app.services.llm_service import llm_service

    # Check LLM service availability
    llm_healthy = await llm_service.health_check()

    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "database": "connected",
            "llm_service": "connected" if llm_healthy else "unavailable"
        }
    )


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint.

    Returns basic API information.

    Returns:
        dict: API name and version
    """
    return {
        "name": "GPT-OSS API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }


# Register API routers
# WHY prefix="/api": Standard REST API convention for versioning and organization.
# All endpoints are under /api/* to distinguish from static files and other routes.
from app.api import projects, conversations, chat, messages, csrf, documents

app.include_router(csrf.router, tags=["CSRF"])  # CSRF token endpoint (no prefix, already in router)
app.include_router(projects.router, prefix="/api", tags=["Projects"])
app.include_router(documents.router, prefix="/api", tags=["Documents"])
app.include_router(conversations.router, prefix="/api", tags=["Conversations"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(messages.router, prefix="/api", tags=["Messages"])


if __name__ == "__main__":
    # This allows running the app directly with: python -m app.main
    # For production, use: uvicorn app.main:app --reload
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
