"""
FastAPI router for chat streaming endpoints.

Provides SSE (Server-Sent Events) streaming for real-time chat responses.
"""

import asyncio
import logging
from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse
from app.db.session import get_db
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService
from app.services.llm_service import llm_service
from app.services.stream_manager import stream_manager
from app.schemas.message import (
    ChatStreamRequest,
    MessageCreate,
    SSETokenEvent,
    SSECompleteEvent,
    SSEErrorEvent
)

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter()


@router.post("/stream")
async def initiate_stream(
    request: ChatStreamRequest,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Initiate chat stream session (Step 1 of 2).

    Creates user and assistant messages, returns session ID for streaming.

    Args:
        request: Chat stream request with conversation_id and message
        db: Database session (injected)

    Returns:
        JSON with session_id and message_id

    Raises:
        HTTPException 400: If validation fails
        HTTPException 404: If conversation not found

    Example:
        POST /api/chat/stream
        {
            "conversation_id": 1,
            "message": "What is IEC 62443?"
        }

        Response 200:
        {
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "message_id": 2
        }

    Client should then connect to GET /api/chat/stream/{session_id} for SSE stream.
    """
    # Verify conversation exists
    conversation = ConversationService.get_conversation_by_id(db, request.conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Create user message in database
    user_message = MessageService.create_message(
        db,
        MessageCreate(
            conversation_id=request.conversation_id,
            role="user",
            content=request.message,
            parent_message_id=None
        )
    )

    # Create assistant message placeholder
    assistant_message = MessageService.create_message(
        db,
        MessageCreate(
            conversation_id=request.conversation_id,
            role="assistant",
            content="",  # Will be filled during streaming
            parent_message_id=user_message.id
        )
    )

    # Store session data for streaming endpoint
    # WHY store: The GET /stream/{session_id} endpoint needs this data
    session_data = {
        "conversation_id": request.conversation_id,
        "user_message": request.message,
        "assistant_message_id": assistant_message.id,
        "user_message_id": user_message.id
    }

    # Create streaming session
    session_id = await stream_manager.create_stream_session(session_data)

    return {
        "session_id": session_id,
        "message_id": assistant_message.id
    }


@router.get("/stream/{session_id}")
async def stream_chat(
    session_id: str,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Stream LLM chat response using SSE (Step 2 of 2).

    Args:
        session_id: Session ID from POST /api/chat/stream
        db: Database session (injected)

    Returns:
        EventSourceResponse with SSE stream

    Raises:
        HTTPException 404: If session not found

    Example:
        GET /api/chat/stream/550e8400-e29b-41d4-a716-446655440000

        Response 200 (SSE stream):
        Headers:
            Content-Type: text/event-stream
            Cache-Control: no-cache
            Connection: keep-alive

        Events:
            event: token
            data: {"token": "IEC", "message_id": 2, "session_id": "550e..."}

            event: token
            data: {"token": " 62443", "message_id": 2, "session_id": "550e..."}

            event: complete
            data: {"message_id": 2, "token_count": 150, "completion_time_ms": 3500}
    """
    # Get session data
    session_data = await stream_manager.get_stream_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")

    conversation_id = session_data["conversation_id"]
    user_message = session_data["user_message"]
    assistant_message_id = session_data["assistant_message_id"]

    # Define the streaming generator
    async def event_generator():
        """
        Generate SSE events from LLM stream.

        Yields SSE-formatted events (token, complete, error).
        Handles cleanup and error recovery.
        """
        start_time = datetime.utcnow()
        accumulated_tokens = []
        token_count = 0

        try:
            # Get conversation history for LLM context
            history = MessageService.get_conversation_history(
                db, conversation_id, max_messages=10
            )

            # Add current user message to history
            history.append({"role": "user", "content": user_message})

            # Build prompt from history
            prompt = llm_service.build_chat_prompt(history)

            # Stream tokens
            async for token in llm_service.generate_stream(
                prompt=prompt,
                max_tokens=2048,
                temperature=0.7,
                stop_sequences=["\nUser:"]  # Only stop when next user turn starts
            ):
                # Accumulate token
                accumulated_tokens.append(token)
                token_count += 1

                # Yield token event
                event_data = SSETokenEvent(
                    token=token,
                    message_id=assistant_message_id,
                    session_id=session_id
                )
                yield {
                    "event": "token",
                    "data": event_data.model_dump_json()
                }

            # Calculate completion metrics
            completion_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Update assistant message with complete content
            complete_content = "".join(accumulated_tokens)

            # Update message metadata
            MessageService.update_message_metadata(
                db,
                assistant_message_id,
                token_count=token_count,
                model_name="gpt-oss-20b",
                completion_time_ms=completion_time_ms,
                content=complete_content
            )

            # Yield completion event
            complete_data = SSECompleteEvent(
                message_id=assistant_message_id,
                token_count=token_count,
                completion_time_ms=completion_time_ms
            )
            yield {
                "event": "complete",
                "data": complete_data.model_dump_json()
            }

        except asyncio.CancelledError:
            # Stream was cancelled by user
            logger.info(f"Stream cancelled: session_id={session_id}")
            error_data = SSEErrorEvent(
                error="Stream cancelled by user",
                error_type="cancelled"
            )
            yield {
                "event": "error",
                "data": error_data.model_dump_json()
            }

        except Exception as e:
            # Stream failed due to error
            logger.error(f"Stream failed: {e}")
            error_data = SSEErrorEvent(
                error=str(e),
                error_type="service_error"
            )
            yield {
                "event": "error",
                "data": error_data.model_dump_json()
            }

        finally:
            # Cleanup session
            await stream_manager.cleanup_stream_session(session_id)

    # Return EventSourceResponse
    # WHY EventSourceResponse: This is sse-starlette's helper that handles
    # SSE formatting, headers, and keep-alive pings automatically.
    return EventSourceResponse(
        event_generator(),
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
        ping=30,  # Send keep-alive ping every 30 seconds
    )


@router.post("/cancel/{session_id}")
async def cancel_stream(session_id: str):
    """
    Cancel an ongoing chat stream.

    Args:
        session_id: Session ID to cancel (UUID from X-Session-ID header)

    Returns:
        Success status

    Raises:
        HTTPException 404: If session not found or already completed

    Example:
        POST /api/chat/cancel/550e8400-e29b-41d4-a716-446655440000

        Response 200:
        {
            "status": "cancelled"
        }
    """
    # Attempt to cancel session
    success = await stream_manager.cancel_session(session_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Session not found or already completed"
        )

    return {"status": "cancelled"}
