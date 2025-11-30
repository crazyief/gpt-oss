"""
FastAPI router for project management endpoints.

Extended operations: stats, details, reorder, and conversation listing.
"""

import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.project_service import ProjectService
from app.services.project_service_extensions import ProjectServiceExtensions
from app.services.conversation_service import ConversationService
from app.schemas.project import ProjectReorderRequest
from app.schemas.conversation import ConversationListResponse
from app.exceptions import (
    ProjectNotFoundError,
    handle_database_error
)

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter()


@router.patch("/projects/reorder", response_model=dict)
async def reorder_projects(
    reorder_data: ProjectReorderRequest,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Reorder projects (for drag-and-drop UI).

    Stage 3 endpoint for manual project ordering.
    WHY before {project_id}: Specific routes must come before parameterized routes
    in FastAPI, otherwise "reorder" would be parsed as a project_id.

    Args:
        reorder_data: Array of project IDs in new order
        db: Database session (injected)

    Returns:
        Dict with updated projects

    Raises:
        HTTPException 400: If project_ids is invalid
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
        Dict with project statistics including:
        - document_count
        - conversation_count
        - message_count
        - total_document_size
        - last_activity_at

    Raises:
        HTTPException 404: If project not found
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
    """
    details = ProjectServiceExtensions.get_project_details(db, project_id)
    if not details:
        raise ProjectNotFoundError(project_id)
    return details
