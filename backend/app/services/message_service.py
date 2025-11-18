"""
Message service layer for business logic.

Handles CRUD operations for messages, including reactions and regeneration.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.database import Message
from app.schemas.message import MessageCreate, MessageReactionUpdate


class MessageService:
    """
    Service class for message-related business logic.

    Encapsulates database operations for messages in conversations.
    """

    @staticmethod
    def create_message(db: Session, message_data: MessageCreate) -> Message:
        """
        Create a new message.

        Args:
            db: Database session
            message_data: Validated message creation data

        Returns:
            Created message instance

        Note:
            This updates the parent conversation's message_count and last_message_at.
            WHY update conversation: Denormalized stats must stay in sync.
            This is done in the same transaction for consistency.
        """
        # Create message instance
        message = Message(
            conversation_id=message_data.conversation_id,
            role=message_data.role,
            content=message_data.content,
            parent_message_id=message_data.parent_message_id,
            token_count=0,  # Will be updated after generation
            meta={}
        )

        # Add to session
        db.add(message)

        # Update conversation stats
        # WHY import here: Avoids circular imports (Conversation imports Message)
        from app.services.conversation_service import ConversationService
        ConversationService.update_message_stats(
            db, message_data.conversation_id, increment_count=True
        )

        # Commit and refresh
        db.commit()
        db.refresh(message)

        return message

    @staticmethod
    def get_message_by_id(db: Session, message_id: int) -> Optional[Message]:
        """
        Get a message by ID.

        Args:
            db: Database session
            message_id: Message ID to retrieve

        Returns:
            Message instance or None if not found

        Note:
            Messages are NOT soft-deleted (no deleted_at field).
            Once created, messages are permanent for audit trail.
        """
        stmt = select(Message).where(Message.id == message_id)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def list_messages(
        db: Session,
        conversation_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[list[Message], int]:
        """
        List messages in a conversation with pagination.

        Args:
            db: Database session
            conversation_id: Conversation ID to fetch messages from
            limit: Maximum number of messages (default: 50, max: 100)
            offset: Number of messages to skip

        Returns:
            Tuple of (messages list, total count)

        Note:
            Messages are ordered by created_at ASC (chronological order).
            WHY ascending: Chat UI displays messages from oldest to newest.
            This matches user expectations (like WhatsApp, Slack, etc.).
        """
        # Enforce max limit
        limit = min(limit, 100)

        # Build base query
        base_query = select(Message).where(Message.conversation_id == conversation_id)

        # Get total count
        count_stmt = select(func.count()).select_from(base_query.subquery())
        total_count = db.execute(count_stmt).scalar_one()

        # Get paginated results (oldest first)
        stmt = base_query.order_by(Message.created_at.asc()).limit(limit).offset(offset)
        messages = db.execute(stmt).scalars().all()

        return list(messages), total_count

    @staticmethod
    def update_reaction(
        db: Session,
        message_id: int,
        reaction_data: MessageReactionUpdate
    ) -> Optional[Message]:
        """
        Update a message's reaction.

        Args:
            db: Database session
            message_id: Message ID to update
            reaction_data: Reaction data (thumbs_up, thumbs_down, or null)

        Returns:
            Updated message or None if not found

        Note:
            Setting reaction to null removes the reaction.
            WHY allow null: Users should be able to undo reactions.
        """
        # Get existing message
        message = MessageService.get_message_by_id(db, message_id)
        if not message:
            return None

        # Update reaction
        message.reaction = reaction_data.reaction

        # Commit changes
        db.commit()
        db.refresh(message)

        return message

    @staticmethod
    def update_message_metadata(
        db: Session,
        message_id: int,
        token_count: int,
        model_name: str,
        completion_time_ms: int,
        content: str = None
    ) -> Optional[Message]:
        """
        Update message metadata after LLM generation.

        Args:
            db: Database session
            message_id: Message ID to update
            token_count: Number of tokens generated
            model_name: Name of LLM model used
            completion_time_ms: Time taken to generate (milliseconds)
            content: Message content (optional, for updating streamed content)

        Returns:
            Updated message or None if not found

        Note:
            This is called after streaming completes to record generation metrics.
            WHY separate method: Message is created before streaming starts,
            but metrics are only available after streaming completes.
        """
        message = MessageService.get_message_by_id(db, message_id)
        if not message:
            return None

        # Update metadata fields
        message.token_count = token_count
        message.model_name = model_name
        message.completion_time_ms = completion_time_ms

        # Update content if provided
        if content is not None:
            message.content = content

        # Commit changes
        db.commit()
        db.refresh(message)

        return message

    @staticmethod
    def get_conversation_history(
        db: Session,
        conversation_id: int,
        max_messages: int = 10
    ) -> list[dict]:
        """
        Get recent conversation history for LLM context.

        Args:
            db: Database session
            conversation_id: Conversation ID
            max_messages: Maximum number of recent messages to include

        Returns:
            List of message dicts with 'role' and 'content' keys

        Note:
            Returns messages in chronological order (oldest first).
            WHY limit to 10: LLM context window is limited. For initial version,
            we use a simple sliding window of last N messages. In Stage 2+,
            we'll implement smarter context management (summarization, RAG, etc.).
        """
        # Get recent messages (ordered oldest to newest)
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(max_messages)
        )
        messages = db.execute(stmt).scalars().all()

        # Reverse to get chronological order (oldest first)
        # WHY reverse: We queried DESC LIMIT N to get last N messages,
        # but LLM needs them in chronological order for context.
        messages = list(reversed(messages))

        # Format for LLM
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
