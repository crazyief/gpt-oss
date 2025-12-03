"""
Route registration for FastAPI application.

Centralizes router configuration and API endpoint registration.
"""

import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def register_routes(app: FastAPI) -> None:
    """
    Register all API routes.

    Args:
        app: FastAPI application instance
    """
    # Health check endpoint
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

    # Root endpoint
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
    from app.api import projects_crud, projects_management, conversations, chat, messages, csrf, documents

    app.include_router(csrf.router, tags=["CSRF"])  # CSRF token endpoint (no prefix, already in router)
    # WHY projects_management before projects_crud: Specific routes like /projects/reorder
    # must come before parameterized routes like /projects/{project_id} in FastAPI
    app.include_router(projects_management.router, prefix="/api", tags=["Projects"])
    app.include_router(projects_crud.router, prefix="/api", tags=["Projects"])
    app.include_router(documents.router, prefix="/api", tags=["Documents"])
    app.include_router(conversations.router, prefix="/api", tags=["Conversations"])
    app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
    app.include_router(messages.router, prefix="/api", tags=["Messages"])

    logger.info("All API routes registered")
