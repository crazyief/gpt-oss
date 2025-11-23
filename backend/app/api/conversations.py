"""
FastAPI router for conversation management endpoints.

Provides REST API for creating, reading, updating, deleting, and searching conversations.
"""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.conversation_service import ConversationService
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationListResponse
)

# Create router instance
router = APIRouter()


@router.post("/conversations/create", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    conversation_data: ConversationCreate,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Create a new conversation.

    Args:
        conversation_data: Conversation creation data (project_id and title are optional)
        db: Database session (injected)

    Returns:
        Created conversation with ID, timestamps, and stats

    Example:
        POST /api/conversations/create
        {
            "project_id": 1,
            "title": "IEC 62443 Questions"
        }

        Response 201:
        {
            "id": 1,
            "project_id": 1,
            "title": "IEC 62443 Questions",
            "created_at": "2025-11-17T10:00:00Z",
            "updated_at": "2025-11-17T10:00:00Z",
            "last_message_at": null,
            "message_count": 0,
            "metadata": {}
        }
    """
    try:
        conversation = ConversationService.create_conversation(db, conversation_data)
        return conversation
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to create conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to create conversation")


@router.get("/conversations/list", response_model=ConversationListResponse)
async def list_conversations(
    db: Annotated[Session, Depends(get_db)],
    project_id: Optional[int] = Query(None, gt=0),
    limit: int = Query(50, ge=1),
    offset: int = Query(0, ge=0)
):
    """
    List conversations with optional project filter and pagination.

    Args:
        project_id: Optional project ID to filter by
        limit: Maximum number of conversations (1-100, default: 50)
        offset: Number of conversations to skip (default: 0)
        db: Database session (injected)

    Returns:
        Dict with 'conversations' array and 'total_count'

    Note:
        Conversations are ordered by most recently active (last_message_at DESC).
        Conversations with no messages appear last.

    Example:
        GET /api/conversations/list?project_id=1&limit=10&offset=0

        Response 200:
        {
            "conversations": [
                {
                    "id": 1,
                    "project_id": 1,
                    "title": "IEC 62443 Questions",
                    "created_at": "2025-11-17T10:00:00Z",
                    "updated_at": "2025-11-17T10:00:00Z",
                    "last_message_at": "2025-11-17T10:05:00Z",
                    "message_count": 3,
                    "metadata": {}
                }
            ],
            "total_count": 1
        }
    """
    try:
        conversations, total_count = ConversationService.list_conversations(
            db, project_id, limit, offset
        )

        return ConversationListResponse(
            conversations=conversations,
            total_count=total_count
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to list conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to list conversations")


@router.get("/conversations/search", response_model=ConversationListResponse)
async def search_conversations(
    db: Annotated[Session, Depends(get_db)],
    q: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(50, ge=1),
    offset: int = Query(0, ge=0)
):
    """
    Search conversations by title keyword.

    Args:
        q: Search keyword (1-200 characters, case-insensitive)
        limit: Maximum number of results (1-100, default: 50)
        offset: Number of results to skip (default: 0)
        db: Database session (injected)

    Returns:
        Dict with matching conversations and total count

    Note:
        Uses case-insensitive substring matching on conversation titles.
        Results are ordered by most recently active.

        WHY this route is defined BEFORE /{conversation_id}: FastAPI matches routes
        in order of definition. If we define /{conversation_id} first, FastAPI would
        try to parse "search" as an integer conversation_id and return HTTP 422.
        Static routes must always come before parameterized routes to avoid this conflict.

    Example:
        GET /api/conversations/search?q=IEC&limit=10&offset=0

        Response 200:
        {
            "conversations": [
                {
                    "id": 1,
                    "project_id": 1,
                    "title": "IEC 62443 Questions",
                    "created_at": "2025-11-17T10:00:00Z",
                    "updated_at": "2025-11-17T10:00:00Z",
                    "last_message_at": "2025-11-17T10:05:00Z",
                    "message_count": 3,
                    "metadata": {}
                }
            ],
            "total_count": 1
        }
    """
    try:
        conversations, total_count = ConversationService.search_conversations(
            db, q, limit, offset
        )

        return ConversationListResponse(
            conversations=conversations,
            total_count=total_count
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to search conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to search conversations")


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Get a conversation by ID.

    Args:
        conversation_id: Conversation ID to retrieve
        db: Database session (injected)

    Returns:
        Conversation with all details

    Raises:
        HTTPException 404: If conversation not found or soft-deleted

    Example:
        GET /api/conversations/1

        Response 200:
        {
            "id": 1,
            "project_id": 1,
            "title": "IEC 62443 Questions",
            "created_at": "2025-11-17T10:00:00Z",
            "updated_at": "2025-11-17T10:00:00Z",
            "last_message_at": "2025-11-17T10:05:00Z",
            "message_count": 3,
            "metadata": {}
        }
    """
    conversation = ConversationService.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.patch("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    update_data: ConversationUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Update a conversation.

    Args:
        conversation_id: Conversation ID to update
        update_data: Fields to update (title and/or project_id)
        db: Database session (injected)

    Returns:
        Updated conversation

    Raises:
        HTTPException 404: If conversation not found

    Examples:
        Update title only:
        PATCH /api/conversations/1
        {
            "title": "Updated Title"
        }

        Update project only (move conversation to different project):
        PATCH /api/conversations/1
        {
            "project_id": 3
        }

        Update both:
        PATCH /api/conversations/1
        {
            "title": "Updated Title",
            "project_id": 3
        }

        Response 200:
        {
            "id": 1,
            "project_id": 3,
            "title": "Updated Title",
            "created_at": "2025-11-17T10:00:00Z",
            "updated_at": "2025-11-17T10:10:00Z",
            "last_message_at": "2025-11-17T10:05:00Z",
            "message_count": 3,
            "metadata": {}
        }
    """
    conversation = ConversationService.update_conversation(
        db, conversation_id, update_data
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Soft-delete a conversation.

    Args:
        conversation_id: Conversation ID to delete
        db: Database session (injected)

    Returns:
        No content (204 status)

    Raises:
        HTTPException 404: If conversation not found

    Note:
        This is a soft delete - the conversation is marked as deleted but not removed.
        Messages in the conversation remain accessible (they have their own lifecycle).

    Example:
        DELETE /api/conversations/1

        Response 204: No content
    """
    success = ConversationService.delete_conversation(db, conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return None
