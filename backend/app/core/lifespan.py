"""
Application lifespan management.

Handles startup and shutdown events for the FastAPI application.
"""

import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db.session import init_db
from app.config import settings

logger = logging.getLogger(__name__)


async def periodic_cleanup():
    """
    PERFORMANCE FIX (PERF-001): Periodic cleanup of rate limiter and stream sessions.

    Runs every 5 minutes to prevent memory leaks in:
    1. Rate limiter - removes expired IP/user entries
    2. Stream manager - removes completed and stale sessions

    WHY 5 minutes: Balances memory cleanup frequency with CPU overhead.
    Rate limiter entries expire after 1 hour, so cleaning every 5 minutes
    means at most we keep 12x5min = 1 hour of stale entries (acceptable).
    """
    while True:
        await asyncio.sleep(300)  # Every 5 minutes
        try:
            # Cleanup rate limiter entries
            from app.middleware.rate_limiter import get_rate_limiter
            rate_limiter = get_rate_limiter()
            rate_limiter.cleanup_old_entries()
            logger.info("Rate limiter cleanup completed")
        except Exception as e:
            logger.error(f"Rate limiter cleanup failed: {e}")

        try:
            # Cleanup stream manager sessions (MEMORY LEAK FIX)
            from app.services.stream_manager import stream_manager
            cleanup_result = await stream_manager.cleanup_all()
            if cleanup_result["total_cleaned"] > 0:
                logger.info(
                    f"Stream manager cleanup completed: "
                    f"{cleanup_result['completed_sessions']} completed, "
                    f"{cleanup_result['stale_sessions']} stale sessions removed"
                )
        except Exception as e:
            logger.error(f"Stream manager cleanup failed: {e}")


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
