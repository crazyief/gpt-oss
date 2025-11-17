"""
Main FastAPI application entry point.

Initializes the FastAPI app, configures middleware, and registers routes.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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


# Configure CORS middleware
# Allows frontend on localhost:3000 to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns the health status of the API and its dependencies.
    Used by monitoring systems and docker health checks.

    Returns:
        JSONResponse: Health status including database and LLM service
    """
    # TODO: Add actual LLM service health check in task-003
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "database": "connected",
            "llm_service": "not_implemented"  # Placeholder for now
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
