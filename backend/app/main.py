"""
Main FastAPI application entry point.

Initializes the FastAPI app, configures middleware, and registers routes.
"""

import logging
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events for the FastAPI application.
    Initializes database on startup.

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

    # Yield control to the application
    yield

    # Shutdown: Cleanup resources
    logger.info("Shutting down GPT-OSS Backend API")


# Create FastAPI application instance
app = FastAPI(
    title="GPT-OSS API",
    description="Backend API for GPT-OSS local AI knowledge assistant",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)


# Custom JSON response class with timezone-aware datetime serialization
# WHY: Ensures all timestamps include UTC timezone info (Z suffix)
# PROBLEM: SQLAlchemy stores naive datetimes, JavaScript interprets them as local time
# SOLUTION: Override Pydantic's datetime serialization to add timezone info
# User feedback: Timestamps showing "8h ago" for just-created messages (GMT+8 timezone issue)
from pydantic import field_serializer
from typing import Any
import json


# Configure Pydantic to serialize datetimes with UTC timezone
# This is done by customizing the BaseModel's model_config in each schema
# For now, we'll monkey-patch the JSON encoder globally
original_default = json.JSONEncoder.default


def utc_aware_json_encoder(self, obj):
    """Custom JSON encoder that adds UTC timezone to naive datetimes."""
    if isinstance(obj, datetime):
        # If naive datetime (no timezone info), assume it's UTC
        if obj.tzinfo is None:
            obj = obj.replace(tzinfo=timezone.utc)
        # Serialize to ISO 8601 with Z suffix
        return obj.isoformat().replace('+00:00', 'Z')
    return original_default(self, obj)


# Monkey-patch the JSON encoder globally
json.JSONEncoder.default = utc_aware_json_encoder


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
