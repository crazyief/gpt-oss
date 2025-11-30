"""
FastAPI router for project management endpoints.

Provides REST API for creating, reading, updating, and listing projects.
"""

import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.project_service import ProjectService
from app.services.project_service_extensions import ProjectServiceExtensions
from app.services.conversation_service import ConversationService
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectWithStats,
    ProjectListResponse,
    ProjectReorderRequest,
    DeleteProjectResponse
)
from app.schemas.conversation import ConversationListResponse
from app.exceptions import (
    ProjectNotFoundError,
    DatabaseError,
    handle_database_error
)

logger = logging.getLogger(__name__)

# Create router instance
# WHY separate router: Follows FastAPI best practice of organizing endpoints
# by resource type. Makes code modular and allows independent testing.
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

    Example:
        GET /api/projects/default

        Response 200:
        {
            "id": 1,
            "name": "Default Project",
            "description": "Your default workspace for conversations",
            "created_at": "2025-11-17T10:00:00Z",
            "updated_at": "2025-11-17T10:00:00Z",
            "metadata": {}
        }
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

    Example:
        GET /api/projects/list?sort=recent&limit=10&offset=0

        Response 200:
        {
            "projects": [
                {
                    "id": 1,
                    "name": "IEC 62443 Analysis",
                    "description": "Security standard",
                    "color": "blue",
                    "icon": "shield",
                    "is_default": false,
                    "sort_order": 0,
                    "conversation_count": 5,
                    "document_count": 3,
                    "last_used_at": "2025-11-30T10:00:00Z",
                    "created_at": "2025-11-17T10:00:00Z",
                    "updated_at": "2025-11-30T10:00:00Z"
                }
            ],
            "total": 1
        }
    """
    try:
        # Stage 3: Enhanced with document counts, last_used_at, and sorting
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
        raise ProjectNotFoundError(project_id)
    return project


@router.delete("/projects/{project_id}", response_model=DeleteProjectResponse)
async def delete_project(
    project_id: int,
    action: str = Query(..., regex="^(move|delete)$"),
    db: Annotated[Session, Depends(get_db)]
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

    Note:
        STAGE 3 UPDATES:
        - Added action parameter: "move" or "delete"
        - "move": Moves all conversations/docs to Default, then deletes project
        - "delete": Permanently removes project and ALL contents
        - Cannot delete default project (is_default=True)

        WHY hard delete: Stage 2 requirement for complete data removal including
        uploaded files. This cannot be undone. For audit compliance, use export
        features before deletion.

    Examples:
        DELETE /api/projects/2?action=move

        Response 200:
        {
            "message": "Project deleted successfully",
            "action": "move",
            "moved_conversations": 3,
            "moved_documents": 12
        }

        DELETE /api/projects/2?action=delete

        Response 200:
        {
            "message": "Project deleted successfully",
            "action": "delete",
            "deleted_conversations": 3,
            "deleted_documents": 12
        }
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
        # Raised when trying to delete default project
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        handle_database_error("delete project", e)


@router.get("/projects/{project_id}/stats", response_model=dict)
async def get_project_stats(
    project_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Get project statistics.

    Args:
        project_id: Project ID
        db: Database session (injected)

    Returns:
        Dict with project statistics

    Raises:
        HTTPException 404: If project not found

    Example:
        GET /api/projects/1/stats

        Response 200:
        {
            "document_count": 5,
            "conversation_count": 3,
            "message_count": 42,
            "total_document_size": 15728640,
            "last_activity_at": "2025-11-29T14:30:00Z"
        }
    """
    stats = ProjectService.get_project_stats(db, project_id)
    if not stats:
        raise ProjectNotFoundError(project_id)
    return stats


@router.get("/projects/{project_id}/conversations", response_model=ConversationListResponse)
async def get_project_conversations(
    project_id: int,
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get all conversations for a project.

    Args:
        project_id: Project ID to fetch conversations for
        db: Database session (injected)
        limit: Maximum number of conversations (1-100, default: 50)
        offset: Number of conversations to skip (default: 0)

    Returns:
        Dict with 'conversations' array and 'total_count'

    Raises:
        HTTPException 404: If project not found

    Example:
        GET /api/projects/1/conversations
        GET /api/projects/1/conversations?limit=10&offset=0

        Response 200:
        {
            "conversations": [
                {
                    "id": 1,
                    "project_id": 1,
                    "title": "Security Analysis",
                    "created_at": "2025-11-29T10:00:00Z",
                    "updated_at": "2025-11-29T14:30:00Z"
                }
            ],
            "total_count": 1
        }
    """
    # Verify project exists
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise ProjectNotFoundError(project_id)

    # Get conversations for project
    conversations, total_count = ConversationService.list_conversations(
        db, project_id=project_id, limit=limit, offset=offset
    )

    return ConversationListResponse(
        conversations=conversations,
        total_count=total_count
    )


@router.get("/projects/{project_id}/details", response_model=dict)
async def get_project_details(
    project_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Get detailed project information with conversations and documents.

    Stage 3 endpoint for ProjectsTab detail view.

    Args:
        project_id: Project ID
        db: Database session (injected)

    Returns:
        Dict with project info, conversations, documents, and counts

    Raises:
        HTTPException 404: If project not found

    Example:
        GET /api/projects/1/details

        Response 200:
        {
            "project": {
                "id": 1,
                "name": "Security Audit",
                "description": "IEC 62443 compliance",
                "color": "blue",
                "icon": "shield",
                "is_default": false,
                "created_at": "2025-11-30T10:00:00Z",
                "updated_at": "2025-11-30T10:00:00Z"
            },
            "conversations": [
                {
                    "id": 10,
                    "title": "Zone analysis",
                    "message_count": 15,
                    "created_at": "2025-11-20T10:00:00Z",
                    "updated_at": "2025-11-30T09:00:00Z"
                }
            ],
            "documents": [
                {
                    "id": 5,
                    "original_filename": "IEC62443-4-2.pdf",
                    "file_size": 2048576,
                    "file_type": "pdf",
                    "uploaded_at": "2025-11-15T10:30:00Z"
                }
            ],
            "conversation_count": 1,
            "document_count": 1
        }
    """
    details = ProjectServiceExtensions.get_project_details(db, project_id)
    if not details:
        raise ProjectNotFoundError(project_id)
    return details


@router.patch("/projects/reorder", response_model=dict)
async def reorder_projects(
    reorder_data: ProjectReorderRequest,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Reorder projects (for drag-and-drop UI).

    Stage 3 endpoint for manual project ordering.

    Args:
        reorder_data: Array of project IDs in new order
        db: Database session (injected)

    Returns:
        Dict with updated projects

    Raises:
        HTTPException 400: If project_ids is invalid

    Example:
        PATCH /api/projects/reorder
        {
            "project_ids": [3, 2, 1]
        }

        Response 200:
        {
            "message": "Projects reordered successfully",
            "projects": [
                { "id": 3, "name": "Project C", "sort_order": 0 },
                { "id": 2, "name": "Project B", "sort_order": 1 },
                { "id": 1, "name": "Default", "sort_order": 2 }
            ]
        }
    """
    try:
        updated_projects = ProjectServiceExtensions.reorder_projects(
            db, reorder_data.project_ids
        )

        return {
            "message": "Projects reordered successfully",
            "projects": [
                {
                    "id": p.id,
                    "name": p.name,
                    "sort_order": p.sort_order
                }
                for p in updated_projects
            ]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        handle_database_error("reorder projects", e)
