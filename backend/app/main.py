"""
Main FastAPI application entry point.

Initializes the FastAPI app, configures middleware, and registers routes.
"""

import logging
from fastapi import FastAPI

from app.config import settings
from app.core import lifespan, register_middleware, register_routes

# Configure logging
# Format: timestamp - logger name - level - message
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# OpenAPI metadata for better documentation
OPENAPI_TAGS = [
    {
        "name": "Health",
        "description": "Health check endpoints for monitoring and container orchestration.",
    },
    {
        "name": "CSRF",
        "description": "CSRF token management. All state-changing requests (POST, PUT, PATCH, DELETE) require a valid CSRF token.",
    },
    {
        "name": "Projects",
        "description": "Project management endpoints. Projects are containers for conversations and documents.",
    },
    {
        "name": "Conversations",
        "description": "Conversation CRUD operations. Conversations belong to projects and contain messages.",
    },
    {
        "name": "Chat",
        "description": "Real-time chat with LLM using Server-Sent Events (SSE) streaming.",
    },
    {
        "name": "Messages",
        "description": "Message operations including reactions and regeneration.",
    },
    {
        "name": "Documents",
        "description": "Document upload, management, and retrieval for RAG-enhanced responses.",
    },
]

# Create FastAPI application instance
app = FastAPI(
    title="GPT-OSS API",
    description="""
## GPT-OSS Backend API

A local AI knowledge assistant with LightRAG for cybersecurity document analysis.

### Features

- **Project Management**: Organize conversations and documents into projects
- **Real-time Chat**: SSE-based streaming responses from local LLM
- **Document RAG**: Upload documents for retrieval-augmented generation
- **Full Audit Trail**: Track all interactions with timestamps

### Authentication

This API uses CSRF tokens for protection against cross-site request forgery:

1. Fetch a token from `GET /api/csrf-token`
2. Include the token in `X-CSRF-Token` header for all state-changing requests

### Rate Limits

| Endpoint | Limit |
|----------|-------|
| `/api/chat/*` | 30 req/min |
| `/api/projects/*` | 120 req/min |
| `/api/conversations/*` | 120 req/min |
| `/api/documents/*` | 60 req/min |
| Default | 200 req/min |

### Error Responses

All errors follow a consistent format:
```json
{
  "detail": "Error description",
  "error_type": "error_category"
}
```
    """,
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
    openapi_tags=OPENAPI_TAGS,
    contact={
        "name": "GPT-OSS Team",
        "url": "https://github.com/gpt-oss/gpt-oss",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
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


# Register middleware (order matters!)
register_middleware(app)

# Register routes
register_routes(app)


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
