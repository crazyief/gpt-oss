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


# Configure CORS middleware
# Allows frontend on localhost:3000 to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Configure rate limiting middleware
# FIXED (Issue-11: No Rate Limiting on API Endpoints)
# Protects against DoS attacks and resource exhaustion
from app.middleware.rate_limiter import rate_limit_middleware
app.middleware("http")(rate_limit_middleware)

# ARCHITECTURE FIX (ARCH-003): Request size limiting middleware
# Prevents memory exhaustion attacks from huge request payloads
from app.middleware.request_size_limiter import RequestSizeLimitMiddleware
app.add_middleware(RequestSizeLimitMiddleware, max_size=10_000_000)  # 10MB limit

# SECURITY FIX (SEC-003): CSRF protection middleware
# Validates Origin/Referer headers for state-changing requests
# Stage 1: Origin validation (no frontend changes needed)
# Stage 2: Token-based CSRF (requires frontend updates)
from app.middleware.csrf_protection import CSRFProtectionMiddleware
app.add_middleware(CSRFProtectionMiddleware, allowed_origins=settings.get_cors_origins())


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
from app.api import projects, conversations, chat, messages

app.include_router(projects.router, prefix="/api", tags=["Projects"])
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
