"""
SQLAlchemy database models for GPT-OSS application.

Defines the schema for projects, conversations, and messages with proper
relationships, indexes, and soft-delete support.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class Project(Base):
    """
    Project model for organizing conversations.

    A project is a top-level organizational unit that groups related
    conversations. For example, a project could be for analyzing a specific
    standard (IEC 62443) or a product line.

    Attributes:
        id: Primary key
        name: Project name (max 100 chars)
        description: Optional detailed description (max 500 chars)
        color: Project color (default: "blue")
        icon: Project icon (default: "folder")
        is_default: True for default project (cannot be deleted)
        sort_order: Manual ordering index (0 = first)
        created_at: Timestamp of creation
        updated_at: Timestamp of last update (auto-updated)
        deleted_at: Soft delete timestamp (NULL if not deleted)
        metadata: JSON field for extensible data storage
        conversations: Relationship to child conversations
    """

    __tablename__ = "projects"

    # Primary key
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)

    # Core fields
    name: Mapped[str] = Column(String(100), nullable=False)
    description: Mapped[Optional[str]] = Column(String(500), nullable=True)

    # Stage 3: UI customization fields
    # color: Visual color for project icon/label (8 preset colors)
    # icon: Icon identifier for project (8 preset icons)
    # WHY these fields: Improves UX by allowing users to visually organize
    # projects. Color coding and icons enable quick recognition in list views.
    color: Mapped[str] = Column(String(20), nullable=False, default="blue")
    icon: Mapped[str] = Column(String(20), nullable=False, default="folder")

    # Stage 3: Project management fields
    # is_default: Marks the default project (prevents deletion)
    # sort_order: Manual ordering for custom project list arrangement
    # WHY is_default: Ensures users always have a default workspace.
    # WHY sort_order: Allows drag-and-drop reordering of projects in UI.
    is_default: Mapped[bool] = Column(Integer, nullable=False, default=0)
    sort_order: Mapped[int] = Column(Integer, nullable=False, default=0)

    # Timestamps
    # created_at uses server_default for database-level timestamp
    # updated_at uses onupdate to automatically update on changes
    created_at: Mapped[datetime] = Column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Soft delete support
    # NULL means not deleted, timestamp means deleted at that time
    # WHY soft delete: We never physically delete data for audit compliance.
    # This allows recovery of accidentally deleted projects and preserves
    # historical data for analytics. Hard deletes are irreversible and
    # violate cybersecurity audit requirements (IEC 62443 compliance).
    deleted_at: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)

    # Extensible metadata storage
    # Store arbitrary JSON data without schema changes
    # Note: Named 'meta' instead of 'metadata' because 'metadata' is reserved
    # by SQLAlchemy's DeclarativeBase (holds the MetaData object)
    meta: Mapped[dict] = Column(JSON, nullable=False, default=dict)

    # Relationships
    # Cascade delete ensures conversations are deleted when project is deleted
    # Use lazy='selectin' to avoid N+1 queries when loading projects
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # Indexes for performance
    # Index on deleted_at for filtering non-deleted projects
    # Index on created_at DESC for sorting by creation date
    # Index on sort_order for manual ordering (Stage 3)
    # WHY these indexes: Every project list query filters by deleted_at IS NULL,
    # making this index critical for performance (avoids full table scan).
    # The created_at index supports "ORDER BY created_at DESC" for showing
    # most recent projects first. Without this, SQLite would need to sort
    # the entire result set in memory, which becomes expensive with 1000+ projects.
    # Index selectivity: deleted_at is highly selective (most rows are NULL),
    # created_at provides good ordering performance for time-based queries.
    # sort_order index enables efficient manual ordering for drag-and-drop UX.
    __table_args__ = (
        Index("idx_projects_deleted_at", "deleted_at"),
        Index("idx_projects_created_at", "created_at"),
        Index("idx_projects_sort_order", "sort_order"),
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Project(id={self.id}, name='{self.name}')>"


class Conversation(Base):
    """
    Conversation model for chat sessions.

    A conversation is a thread of messages between the user and the AI assistant.
    Each conversation belongs to a project and contains multiple messages.

    Attributes:
        id: Primary key
        project_id: Foreign key to parent project (nullable)
        title: Conversation title (max 200 chars)
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
        deleted_at: Soft delete timestamp
        last_message_at: Timestamp of most recent message (for sorting)
        message_count: Denormalized count of messages (performance optimization)
        meta: JSON field for extensible data
        project: Relationship to parent project
        messages: Relationship to child messages
    """

    __tablename__ = "conversations"

    # Primary key
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to project (nullable to support project-less conversations)
    project_id: Mapped[Optional[int]] = Column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True
    )

    # Core fields
    title: Mapped[str] = Column(String(200), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = Column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Soft delete support
    deleted_at: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)

    # Denormalized fields for performance
    # last_message_at is updated when messages are added (used for sorting)
    # message_count is updated when messages are added/deleted (avoid COUNT(*))
    # WHY denormalization: COUNT(*) queries are expensive on large tables.
    # In Stage 2+, conversations may have thousands of messages, making
    # real-time counting prohibitively slow. Denormalizing message_count
    # trades write complexity (updating counter) for read speed (instant access).
    # This is a classic space-time tradeoff favoring query performance.
    # Similarly, last_message_at enables efficient "sort by activity" without
    # joining to the messages table and running MAX(created_at) aggregations.
    last_message_at: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)
    message_count: Mapped[int] = Column(Integer, nullable=False, default=0)

    # Extensible metadata
    # Note: Named 'meta' instead of 'metadata' (reserved by SQLAlchemy)
    meta: Mapped[dict] = Column(JSON, nullable=False, default=dict)

    # Relationships
    project: Mapped[Optional["Project"]] = relationship(
        "Project", back_populates="conversations"
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # Indexes for performance
    # Index on project_id for filtering conversations by project
    # Index on deleted_at for filtering non-deleted conversations
    # Index on last_message_at DESC for sorting by activity
    # WHY these indexes: project_id is used in every "get conversations for project"
    # query and as a foreign key, making this index mandatory for join performance.
    # deleted_at enables fast filtering of active conversations (soft delete pattern).
    # last_message_at supports "sort by most recently active" which is the default
    # UI behavior - users want to see conversations they recently interacted with.
    # Combined, these indexes support the query: "get active conversations in project X
    # ordered by most recent activity" without table scans or expensive sorts.
    __table_args__ = (
        Index("idx_conversations_project_id", "project_id"),
        Index("idx_conversations_deleted_at", "deleted_at"),
        Index("idx_conversations_last_message_at", "last_message_at"),
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Conversation(id={self.id}, title='{self.title}')>"


class Message(Base):
    """
    Message model for user and assistant chat messages.

    Each message belongs to a conversation and has a role (user or assistant).
    Messages support reactions and regeneration via parent_message_id.

    Attributes:
        id: Primary key
        conversation_id: Foreign key to parent conversation
        role: Message role (user or assistant)
        content: Message content (text)
        created_at: Timestamp of creation
        reaction: User reaction to message (thumbs_up, thumbs_down, null)
        parent_message_id: Self-referential FK for regenerate feature
        token_count: Number of tokens in message (for stats)
        model_name: Name of LLM model used (for assistant messages)
        completion_time_ms: Time taken to generate response (milliseconds)
        meta: JSON field for extensible data
        conversation: Relationship to parent conversation
        parent_message: Relationship to parent message (for regeneration)
        child_messages: Relationship to child messages (regenerations)
    """

    __tablename__ = "messages"

    # Primary key
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to conversation
    conversation_id: Mapped[int] = Column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )

    # Message content
    # Role must be either 'user' or 'assistant'
    # Content is unlimited text (use Text type instead of String)
    role: Mapped[str] = Column(String(20), nullable=False)
    content: Mapped[str] = Column(Text, nullable=False)

    # Timestamp
    created_at: Mapped[datetime] = Column(
        DateTime, server_default=func.now(), nullable=False
    )

    # User feedback
    # Reaction can be 'thumbs_up', 'thumbs_down', or NULL
    reaction: Mapped[Optional[str]] = Column(String(20), nullable=True)

    # Self-referential foreign key for regenerate feature
    # When user clicks "regenerate", new assistant message is created
    # with parent_message_id pointing to the user's message
    # WHY self-referential FK: This creates a tree structure for message variations.
    # When a user regenerates an assistant's response, we create a new message
    # that points back to the original user message via parent_message_id.
    # This allows tracking multiple AI response attempts for the same prompt,
    # critical for comparing model outputs and improving responses.
    # ondelete="SET NULL" ensures if parent is deleted, child messages persist
    # as orphans rather than cascading delete (preserves conversation history).
    parent_message_id: Mapped[Optional[int]] = Column(
        Integer, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True
    )

    # LLM metadata (for assistant messages)
    # token_count is the number of tokens in the message
    # model_name is the LLM model used (e.g., 'gpt-oss-20b')
    # completion_time_ms is the time taken to generate the response
    token_count: Mapped[int] = Column(Integer, nullable=False, default=0)
    model_name: Mapped[Optional[str]] = Column(String(100), nullable=True)
    completion_time_ms: Mapped[Optional[int]] = Column(Integer, nullable=True)

    # Extensible metadata
    # Note: Named 'meta' instead of 'metadata' (reserved by SQLAlchemy)
    meta: Mapped[dict] = Column(JSON, nullable=False, default=dict)

    # Relationships
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )
    parent_message: Mapped[Optional["Message"]] = relationship(
        "Message", remote_side=[id], foreign_keys=[parent_message_id]
    )

    # Indexes for performance
    # Index on conversation_id for fetching messages in a conversation
    # Index on created_at ASC for ordering messages chronologically
    # Index on parent_message_id for finding regenerated responses
    # WHY these indexes: conversation_id is the primary access pattern - every
    # chat view loads "all messages for conversation X". This index is critical.
    # created_at supports chronological ordering (messages appear in time sequence).
    # parent_message_id enables the "find all regenerations of this user message"
    # query, used when displaying message variations in the UI (Stage 3+ feature).
    # Note: We don't index 'role' because it has low cardinality (only 2 values),
    # making it ineffective for filtering. The database can scan faster than index lookup.
    __table_args__ = (
        Index("idx_messages_conversation_id", "conversation_id"),
        Index("idx_messages_created_at", "created_at"),
        Index("idx_messages_parent_message_id", "parent_message_id"),
        # Constraint to ensure role is either 'user' or 'assistant'
        CheckConstraint(
            "role IN ('user', 'assistant')",
            name="check_message_role"
        ),
        # Constraint to ensure reaction is valid or NULL
        CheckConstraint(
            "reaction IS NULL OR reaction IN ('thumbs_up', 'thumbs_down')",
            name="check_message_reaction"
        ),
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Message(id={self.id}, role='{self.role}', conversation_id={self.conversation_id})>"


class Document(Base):
    """
    Document model for uploaded files.

    Documents are files uploaded to a project (PDFs, Word docs, Excel files, etc.).
    Files are stored on the filesystem, while metadata is stored in the database.

    Attributes:
        id: Primary key
        project_id: Foreign key to parent project
        filename: Stored filename on disk (with UUID prefix)
        original_filename: User's original filename
        file_path: Full filesystem path to the file
        file_size: File size in bytes
        mime_type: MIME type (e.g., application/pdf)
        uploaded_at: Timestamp of upload
        project: Relationship to parent project
    """

    __tablename__ = "documents"

    # Primary key
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to project
    # ON DELETE CASCADE ensures documents are deleted when project is deleted
    project_id: Mapped[int] = Column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )

    # File metadata
    # filename: stored name with UUID prefix (e.g., "abc123_report.pdf")
    # original_filename: user's original name (e.g., "report.pdf")
    # file_path: full path on disk (e.g., "uploads/1/abc123_report.pdf")
    filename: Mapped[str] = Column(String(500), nullable=False)
    original_filename: Mapped[str] = Column(String(255), nullable=False)
    file_path: Mapped[str] = Column(String(1000), nullable=False)

    # File properties
    # file_size: size in bytes for storage tracking and UI display
    # mime_type: MIME type for correct Content-Type header on download
    file_size: Mapped[int] = Column(Integer, nullable=False)
    mime_type: Mapped[str] = Column(String(100), nullable=False)

    # Timestamp
    uploaded_at: Mapped[datetime] = Column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project", back_populates="documents"
    )

    # Indexes for performance
    # Index on project_id for fetching documents in a project
    # Index on uploaded_at for sorting by upload date
    # Index on mime_type for filtering by file type
    # WHY these indexes: project_id is the primary access pattern - every
    # document list query filters by project. uploaded_at supports chronological
    # sorting (newest first). mime_type enables filtering by file type
    # (e.g., "show only PDFs") which is a common UI feature.
    __table_args__ = (
        Index("idx_documents_project_id", "project_id"),
        Index("idx_documents_uploaded_at", "uploaded_at"),
        Index("idx_documents_mime_type", "mime_type"),
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Document(id={self.id}, filename='{self.filename}', project_id={self.project_id})>"
