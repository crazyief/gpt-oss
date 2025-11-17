"""
Pydantic schemas for Conversation API requests and responses.

Defines validation models for creating, updating, and retrieving conversations.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ConversationBase(BaseModel):
    """
    Base schema for Conversation with common fields.
    """
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Conversation title (1-200 characters)"
    )


class ConversationCreate(BaseModel):
    """
    Schema for creating a new conversation.

    Both fields are optional:
    - project_id: If not provided, conversation is not associated with a project
    - title: If not provided, title is auto-generated (e.g., "New Chat")
    """
    project_id: Optional[int] = Field(
        None,
        gt=0,
        description="Optional project ID to associate with"
    )
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Optional conversation title (auto-generated if not provided)"
    )


class ConversationUpdate(BaseModel):
    """
    Schema for updating an existing conversation.

    Currently only supports updating the title.
    """
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Updated conversation title"
    )


class ConversationResponse(ConversationBase):
    """
    Schema for conversation API responses.

    Includes all database fields and denormalized statistics.
    """
    id: int = Field(..., description="Unique conversation ID")
    project_id: Optional[int] = Field(None, description="Associated project ID")
    created_at: datetime = Field(..., description="Timestamp of creation")
    updated_at: datetime = Field(..., description="Timestamp of last update")
    last_message_at: Optional[datetime] = Field(
        None,
        description="Timestamp of most recent message"
    )
    message_count: int = Field(
        0,
        description="Total number of messages in conversation"
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Additional metadata"
    )

    # Pydantic v2 configuration
    model_config = ConfigDict(from_attributes=True)


class ConversationListResponse(BaseModel):
    """
    Schema for paginated conversation list responses.

    Includes array of conversations and total count for pagination UI.
    """
    conversations: list[ConversationResponse] = Field(
        ...,
        description="Array of conversations"
    )
    total_count: int = Field(
        ...,
        description="Total number of conversations (for pagination)"
    )
