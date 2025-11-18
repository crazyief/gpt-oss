"""
Pydantic schemas for Project API requests and responses.

Defines validation models for creating, updating, and retrieving projects.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ProjectBase(BaseModel):
    """
    Base schema for Project with common fields.

    Used as a parent class for request/response schemas.
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Project name (1-100 characters)"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional project description (max 500 characters)"
    )


class ProjectCreate(ProjectBase):
    """
    Schema for creating a new project.

    Inherits from ProjectBase, no additional fields needed.
    """
    pass


class ProjectUpdate(BaseModel):
    """
    Schema for updating an existing project.

    All fields are optional to support partial updates.
    """
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Updated project name"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Updated project description"
    )


class ProjectResponse(ProjectBase):
    """
    Schema for project API responses.

    Includes all database fields including timestamps and metadata.

    WHY metadata alias: The database column is named 'meta' (because 'metadata'
    is reserved by SQLAlchemy's DeclarativeBase), but the API contract uses
    'metadata' for consistency with REST conventions. Pydantic's Field(alias=...)
    handles the mapping automatically when from_attributes=True.
    """
    id: int = Field(..., description="Unique project ID")
    created_at: datetime = Field(..., description="Timestamp of creation")
    updated_at: datetime = Field(..., description="Timestamp of last update")
    metadata: dict = Field(
        default_factory=dict,
        validation_alias="meta",
        serialization_alias="metadata",
        description="Additional metadata"
    )

    # Pydantic v2 configuration
    # from_attributes allows creating from SQLAlchemy models
    # populate_by_name allows both 'meta' and 'metadata' as input
    # WHY validation_alias vs serialization_alias: When reading from the database,
    # we use 'meta' (validation_alias matches the SQLAlchemy column name). When
    # serializing to JSON response, we use 'metadata' (serialization_alias matches
    # the API contract). This provides clean API while avoiding SQLAlchemy reserved names.
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ProjectWithStats(ProjectResponse):
    """
    Schema for project response with conversation statistics.

    Extends ProjectResponse with denormalized conversation count.
    Used in list views where stats are needed without extra queries.
    """
    conversation_count: int = Field(
        0,
        description="Number of conversations in this project"
    )
