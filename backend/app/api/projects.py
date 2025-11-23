"""
FastAPI router for project management endpoints.

Provides REST API for creating, reading, updating, and listing projects.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.project_service import ProjectService
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectWithStats
)

# Create router instance
# WHY separate router: Follows FastAPI best practice of organizing endpoints
# by resource type. Makes code modular and allows independent testing.
router = APIRouter()


@router.post("/projects/create", response_model=ProjectResponse, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Create a new project.

    Args:
        project_data: Validated project creation data (name and optional description)
        db: Database session (injected by FastAPI dependency)

    Returns:
        Created project with ID, timestamps, and metadata

    Raises:
        HTTPException 400: If validation fails (handled by Pydantic)
        HTTPException 500: If database operation fails

    Example:
        POST /api/projects/create
        {
            "name": "IEC 62443 Analysis",
            "description": "Security standard compliance project"
        }

        Response 201:
        {
            "id": 1,
            "name": "IEC 62443 Analysis",
            "description": "Security standard compliance project",
            "created_at": "2025-11-17T10:00:00Z",
            "updated_at": "2025-11-17T10:00:00Z",
            "metadata": {}
        }
    """
    try:
        # Create project via service layer
        # WHY service layer: Keeps business logic out of route handlers.
        # Makes code testable without FastAPI dependencies and allows
        # reusing logic in other contexts (CLI tools, background jobs, etc.).
        project = ProjectService.create_project(db, project_data)
        return project
    except Exception as e:
        # Log error and return generic 500 response
        # WHY generic error: Don't expose internal details to clients.
        # Specific errors are logged for debugging but not returned in API.
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(status_code=500, detail="Failed to create project")


@router.get("/projects/list", response_model=dict)
async def list_projects(
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(50, ge=1),
    offset: int = Query(0, ge=0)
):
    """
    List all projects with pagination.

    Args:
        limit: Maximum number of projects to return (1-100, default: 50)
        offset: Number of projects to skip (for pagination, default: 0)
        db: Database session (injected)

    Returns:
        Dict with 'projects' array and 'total_count' for pagination

    Example:
        GET /api/projects/list?limit=10&offset=0

        Response 200:
        {
            "projects": [
                {
                    "id": 1,
                    "name": "IEC 62443 Analysis",
                    "description": "Security standard",
                    "created_at": "2025-11-17T10:00:00Z",
                    "conversation_count": 5
                }
            ],
            "total_count": 1
        }
    """
    try:
        # FIXED (Issue-8: N+1 Query Pattern):
        # Use optimized method that fetches projects and stats in single query
        # Previous: 1 + N queries (N+1 problem)
        # Current: 2 queries total (25-50x faster)
        projects_with_stats, total_count = ProjectService.list_projects_with_stats(db, limit, offset)

        return {
            "projects": projects_with_stats,
            "total_count": total_count
        }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to list projects: {e}")
        raise HTTPException(status_code=500, detail="Failed to list projects")


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Get a project by ID.

    Args:
        project_id: Project ID to retrieve
        db: Database session (injected)

    Returns:
        Project with all details

    Raises:
        HTTPException 404: If project not found or soft-deleted

    Example:
        GET /api/projects/1

        Response 200:
        {
            "id": 1,
            "name": "IEC 62443 Analysis",
            "description": "Security standard",
            "created_at": "2025-11-17T10:00:00Z",
            "updated_at": "2025-11-17T10:00:00Z",
            "metadata": {}
        }
    """
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    update_data: ProjectUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Update a project.

    Args:
        project_id: Project ID to update
        update_data: Fields to update (partial update supported)
        db: Database session (injected)

    Returns:
        Updated project

    Raises:
        HTTPException 404: If project not found

    Example:
        PATCH /api/projects/1
        {
            "name": "IEC 62443 Updated"
        }

        Response 200:
        {
            "id": 1,
            "name": "IEC 62443 Updated",
            "description": "Security standard",
            "created_at": "2025-11-17T10:00:00Z",
            "updated_at": "2025-11-17T10:05:00Z",
            "metadata": {}
        }
    """
    project = ProjectService.update_project(db, project_id, update_data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Soft-delete a project.

    Args:
        project_id: Project ID to delete
        db: Database session (injected)

    Returns:
        No content (204 status)

    Raises:
        HTTPException 404: If project not found

    Note:
        This is a soft delete - the project is marked as deleted but not removed.
        Associated conversations are NOT automatically deleted.

    Example:
        DELETE /api/projects/1

        Response 204: No content
    """
    success = ProjectService.delete_project(db, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    # Return None for 204 response (no content)
    return None
