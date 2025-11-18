"""
FastAPI router for message management endpoints.

Provides REST API for fetching messages, adding reactions, and regenerating responses.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse
from app.db.session import get_db
from app.services.message_service import MessageService
from app.services.conversation_service import ConversationService
from app.schemas.message import (
    MessageResponse,
    MessageListResponse,
    MessageReactionUpdate
)

# Import chat stream logic for regenerate
from app.api.chat import stream_chat
from app.schemas.message import ChatStreamRequest

logger = __import__('logging').getLogger(__name__)

# Create router instance
router = APIRouter()


@router.get("/messages/{conversation_id}", response_model=MessageListResponse)
async def get_messages(
    conversation_id: int,
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get messages in a conversation with pagination.

    Args:
        conversation_id: Conversation ID to fetch messages from
        limit: Maximum number of messages (1-100, default: 50)
        offset: Number of messages to skip (default: 0)
        db: Database session (injected)

    Returns:
        Dict with 'messages' array and 'total_count'

    Raises:
        HTTPException 404: If conversation not found

    Note:
        Messages are returned in chronological order (oldest first).
        This is the natural order for displaying a chat conversation.

    Example:
        GET /api/messages/1?limit=50&offset=0

        Response 200:
        {
            "messages": [
                {
                    "id": 1,
                    "conversation_id": 1,
                    "role": "user",
                    "content": "What is IEC 62443?",
                    "created_at": "2025-11-17T10:00:00Z",
                    "reaction": null,
                    "parent_message_id": null,
                    "token_count": 5,
                    "model_name": null,
                    "completion_time_ms": null,
                    "metadata": {}
                },
                {
                    "id": 2,
                    "conversation_id": 1,
                    "role": "assistant",
                    "content": "IEC 62443 is a cybersecurity standard...",
                    "created_at": "2025-11-17T10:00:05Z",
                    "reaction": "thumbs_up",
                    "parent_message_id": 1,
                    "token_count": 150,
                    "model_name": "gpt-oss-20b",
                    "completion_time_ms": 3500,
                    "metadata": {}
                }
            ],
            "total_count": 2
        }
    """
    # Verify conversation exists
    # WHY check first: Better UX to return 404 immediately if conversation
    # doesn't exist, rather than returning empty message list.
    conversation = ConversationService.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    try:
        # Get messages from service
        messages, total_count = MessageService.list_messages(
            db, conversation_id, limit, offset
        )

        return MessageListResponse(
            messages=messages,
            total_count=total_count
        )
    except Exception as e:
        logger.error(f"Failed to fetch messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch messages")


@router.post("/messages/{message_id}/reaction", response_model=dict)
async def update_message_reaction(
    message_id: int,
    reaction_data: MessageReactionUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Add or update a reaction to a message.

    Args:
        message_id: Message ID to react to
        reaction_data: Reaction data (thumbs_up, thumbs_down, or null to remove)
        db: Database session (injected)

    Returns:
        Dict with message_id and updated reaction

    Raises:
        HTTPException 404: If message not found

    Example:
        POST /api/messages/2/reaction
        {
            "reaction": "thumbs_up"
        }

        Response 200:
        {
            "message_id": 2,
            "reaction": "thumbs_up"
        }

        To remove reaction:
        POST /api/messages/2/reaction
        {
            "reaction": null
        }

        Response 200:
        {
            "message_id": 2,
            "reaction": null
        }
    """
    # Update reaction
    message = MessageService.update_reaction(db, message_id, reaction_data)

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    return {
        "message_id": message.id,
        "reaction": message.reaction
    }


@router.post("/messages/{message_id}/regenerate")
async def regenerate_message(
    message_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Regenerate an assistant's response to a user message.

    Args:
        message_id: ID of the USER message to regenerate response for
        db: Database session (injected)

    Returns:
        EventSourceResponse with SSE stream (same as /chat/stream)

    Raises:
        HTTPException 404: If message not found or not a user message

    Note:
        This creates a NEW assistant message with the same parent_message_id.
        The old assistant message remains in the database for comparison.
        WHY keep old: Allows users to compare different AI responses to the
        same prompt. This is valuable for evaluating model quality.

    Example:
        POST /api/messages/1/regenerate

        Response 200 (SSE stream):
        Same format as /api/chat/stream endpoint
    """
    # Get the message to regenerate
    message = MessageService.get_message_by_id(db, message_id)

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Verify it's a user message
    # WHY user only: Regenerating only makes sense for user messages.
    # The idea is to generate a new assistant response to the user's prompt.
    if message.role != "user":
        raise HTTPException(
            status_code=400,
            detail="Can only regenerate responses to user messages"
        )

    # Build chat stream request using the original user message
    # WHY reuse stream_chat: Regenerate is essentially the same as /chat/stream,
    # just with an existing user message instead of a new one.
    request = ChatStreamRequest(
        conversation_id=message.conversation_id,
        message=message.content
    )

    # Call the stream_chat endpoint
    # WHY call directly: Avoids code duplication. The streaming logic is
    # identical to /chat/stream, we just skip creating a new user message.
    return await stream_chat(request, db)
