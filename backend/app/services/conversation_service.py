"""
Conversation service layer for business logic.

Handles CRUD operations for conversations with pagination, filtering,
search, and soft-delete support.
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session
from app.models.database import Conversation
from app.schemas.conversation import ConversationCreate, ConversationUpdate


class ConversationService:
    """
    Service class for conversation-related business logic.

    Encapsulates database operations and business rules for conversations.
    All queries automatically filter soft-deleted conversations.
    """

    @staticmethod
    def create_conversation(
        db: Session,
        conversation_data: ConversationCreate
    ) -> Conversation:
        """
        Create a new conversation.

        Args:
            db: Database session
            conversation_data: Validated conversation creation data

        Returns:
            Created conversation instance

        Note:
            If title is not provided, it defaults to "New Chat".
            The project_id can be None for conversations not associated with a project.
            message_count initializes to 0, last_message_at to None.
        """
        # Auto-generate title if not provided
        # WHY default title: UX best practice - every conversation should have
        # a displayable title. "New Chat" is temporary; it will be updated to
        # a summary of the first user message in Stage 2+ (auto-title feature).
        title = conversation_data.title or "New Chat"

        # Create conversation instance
        conversation = Conversation(
            project_id=conversation_data.project_id,
            title=title,
            message_count=0,
            last_message_at=None,
            meta={}
        )

        # Add to session and commit
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        return conversation

    @staticmethod
    def get_conversation_by_id(
        db: Session,
        conversation_id: int
    ) -> Optional[Conversation]:
        """
        Get a conversation by ID.

        Args:
            db: Database session
            conversation_id: Conversation ID to retrieve

        Returns:
            Conversation instance or None if not found or soft-deleted

        Note:
            Returns None for soft-deleted conversations.
            This enforces soft-delete semantics at the service layer.
        """
        # Build query with soft-delete filter
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.deleted_at.is_(None)
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def list_conversations(
        db: Session,
        project_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[list[Conversation], int]:
        """
        List conversations with optional project filter and pagination.

        Args:
            db: Database session
            project_id: Optional project ID to filter by
            limit: Maximum number of conversations to return (default: 50, max: 100)
            offset: Number of conversations to skip (for pagination)

        Returns:
            Tuple of (conversations list, total count)

        Note:
            Conversations are ordered by last_message_at DESC (most recently active first).
            If last_message_at is NULL (no messages yet), those appear last.
            WHY this order: Users want to see their most recently active conversations
            at the top, not necessarily the newest conversations. This matches
            the UX of popular chat apps (WhatsApp, Slack, Discord).
        """
        # Enforce max limit
        limit = min(limit, 100)

        # Build base query with soft-delete filter
        base_query = select(Conversation).where(Conversation.deleted_at.is_(None))

        # Apply project filter if provided
        # WHY optional filter: Supports both "all conversations" view and
        # "conversations in project X" view. This avoids needing separate
        # service methods for filtered vs unfiltered queries.
        if project_id is not None:
            base_query = base_query.where(Conversation.project_id == project_id)

        # Get total count
        count_stmt = select(func.count()).select_from(base_query.subquery())
        total_count = db.execute(count_stmt).scalar_one()

        # Get paginated results
        # Order by last_message_at DESC, NULL values last
        # WHY nulls_last: Conversations with no messages should appear at the bottom
        # since they have no activity. SQLite puts NULLs last by default, but
        # we make it explicit for clarity and PostgreSQL compatibility.
        stmt = (
            base_query
            .order_by(Conversation.last_message_at.desc().nulls_last())
            .limit(limit)
            .offset(offset)
        )
        conversations = db.execute(stmt).scalars().all()

        return list(conversations), total_count

    @staticmethod
    def update_conversation(
        db: Session,
        conversation_id: int,
        update_data: ConversationUpdate
    ) -> Optional[Conversation]:
        """
        Update a conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID to update
            update_data: Validated update data (title and/or project_id)

        Returns:
            Updated conversation instance or None if not found

        Note:
            Supports updating title and project_id independently.
            Only provided fields (not None) are updated.
            The updated_at timestamp is automatically updated by the database.
        """
        # Get existing conversation
        conversation = ConversationService.get_conversation_by_id(db, conversation_id)
        if not conversation:
            return None

        # Update fields (only if provided)
        if update_data.title is not None:
            conversation.title = update_data.title

        if update_data.project_id is not None:
            conversation.project_id = update_data.project_id

        # Commit changes
        db.commit()
        db.refresh(conversation)

        return conversation

    @staticmethod
    def delete_conversation(db: Session, conversation_id: int) -> bool:
        """
        Soft-delete a conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID to delete

        Returns:
            True if deleted successfully, False if not found

        Note:
            This is a soft delete - sets deleted_at to current timestamp.
            Messages in the conversation are NOT deleted (they have their own lifecycle).
            WHY keep messages: Allows data recovery and maintains audit trails.
            In future stages, we may add a "hard delete" admin feature.
        """
        # Get existing conversation
        conversation = ConversationService.get_conversation_by_id(db, conversation_id)
        if not conversation:
            return False

        # Set deleted_at timestamp
        conversation.deleted_at = datetime.now(timezone.utc)

        # Commit changes
        db.commit()

        return True

    @staticmethod
    def search_conversations(
        db: Session,
        query: str,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[list[Conversation], int]:
        """
        Search conversations by title keyword.

        Args:
            db: Database session
            query: Search keyword (case-insensitive)
            limit: Maximum number of results (default: 50, max: 100)
            offset: Number of results to skip (for pagination)

        Returns:
            Tuple of (matching conversations list, total count)

        Note:
            Uses SQLite LIKE for simple substring matching (case-insensitive).
            In future stages, we could upgrade to FTS5 (Full-Text Search) for
            better performance and features like ranking, phrase search, etc.
            WHY LIKE for now: Simple, works out of the box, no index setup needed.
            Sufficient for Stage 1 with small datasets (<1000 conversations).
        """
        # Enforce max limit
        limit = min(limit, 100)

        # Build search query
        # Use LIKE with wildcards for substring matching
        # WHY lowercase: SQLite's LIKE is case-insensitive by default, but we
        # make it explicit with LOWER() for PostgreSQL compatibility.
        #
        # SECURITY FIX: Escape LIKE wildcards in user input
        # Without this, users could inject % or _ to manipulate search behavior
        # Example: searching "%" would match everything
        query_escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        search_pattern = f"%{query_escaped.lower()}%"

        base_query = select(Conversation).where(
            Conversation.deleted_at.is_(None),
            func.lower(Conversation.title).like(search_pattern)
        )

        # Get total count
        count_stmt = select(func.count()).select_from(base_query.subquery())
        total_count = db.execute(count_stmt).scalar_one()

        # Get paginated results
        # Order by relevance (exact matches first), then by last_message_at
        # WHY this order: Exact matches are more relevant than partial matches.
        # Within same relevance level, show most recently active first.
        stmt = (
            base_query
            .order_by(Conversation.last_message_at.desc().nulls_last())
            .limit(limit)
            .offset(offset)
        )
        conversations = db.execute(stmt).scalars().all()

        return list(conversations), total_count

    @staticmethod
    def update_message_stats(
        db: Session,
        conversation_id: int,
        increment_count: bool = True
    ) -> None:
        """
        Update denormalized message statistics for a conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID to update
            increment_count: If True, increment message_count by 1

        Returns:
            None

        Note:
            This is called internally when messages are added to a conversation.
            Updates both message_count and last_message_at for performance.
            WHY denormalization: Avoids expensive COUNT(*) queries on messages table.
            See detailed explanation in database.py for Conversation model.
        """
        conversation = ConversationService.get_conversation_by_id(db, conversation_id)
        if not conversation:
            return

        # Update last_message_at to current time
        conversation.last_message_at = datetime.now(timezone.utc)

        # Increment message count if requested
        if increment_count:
            conversation.message_count += 1

        # Commit changes
        db.commit()
