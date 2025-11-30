"""
FastAPI router for project CRUD endpoints.

Basic Create, Read, Update, Delete operations for projects.
"""

import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.project_service import ProjectService
from app.services.project_service_extensions import ProjectServiceExtensions
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    DeleteProjectResponse
)
from app.exceptions import (
    ProjectNotFoundError,
    handle_database_error
)

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter()


@router.get("/projects/default", response_model=ProjectResponse)
async def get_default_project(
    db: Annotated[Session, Depends(get_db)]
):
    """
    Get the default project, creating it if it doesn't exist.

    This endpoint is used on initial page load to ensure there's always
    a project selected, enabling the "New Chat" button immediately.

    Returns:
        The default project (oldest project, or newly created "Default Project")
    """
    try:
        project = ProjectService.get_or_create_default_project(db)
        return project
    except Exception as e:
        handle_database_error("get or create default project", e)


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
    """
    try:
        project = ProjectService.create_project(db, project_data)
        return project
    except Exception as e:
        handle_database_error("create project", e)


@router.get("/projects/list", response_model=ProjectListResponse)
async def list_projects(
    db: Annotated[Session, Depends(get_db)],
    sort: str = Query("recent", regex="^(recent|name|manual)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    List all projects with pagination and sorting.

    Args:
        sort: Sort order - "recent" (default), "name", or "manual"
        limit: Maximum number of projects to return (1-100, default: 50)
        offset: Number of projects to skip (for pagination, default: 0)
        db: Database session (injected)

    Returns:
        Dict with 'projects' array and 'total' count for pagination
    """
    try:
        projects_with_stats, total_count = ProjectServiceExtensions.list_projects_with_full_stats(
            db, sort_by=sort, limit=limit, offset=offset
        )

        return ProjectListResponse(
            projects=projects_with_stats,
            total=total_count
        )
    except Exception as e:
        handle_database_error("list projects", e)


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
    """
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise ProjectNotFoundError(project_id)
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
    """
    project = ProjectService.update_project(db, project_id, update_data)
    if not project:
        raise ProjectNotFoundError(project_id)
    return project


@router.delete("/projects/{project_id}", response_model=DeleteProjectResponse)
async def delete_project(
    project_id: int,
    db: Annotated[Session, Depends(get_db)],
    action: str = Query(..., regex="^(move|delete)$")
):
    """
    Delete a project with options for handling contents.

    Args:
        project_id: Project ID to delete
        action: "move" (to Default) or "delete" (permanently)
        db: Database session (injected)

    Returns:
        DeleteProjectResponse with counts of moved/deleted items

    Raises:
        HTTPException 400: If trying to delete default project
        HTTPException 404: If project not found
    """
    try:
        success, details = ProjectService.delete_project(
            db, project_id, hard_delete=True, action=action
        )
        if not success:
            raise ProjectNotFoundError(project_id)

        return DeleteProjectResponse(
            message="Project deleted successfully",
            **details
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        handle_database_error("delete project", e)
