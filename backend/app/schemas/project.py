"""
Pydantic schemas for Project API requests and responses.

Defines validation models for creating, updating, and retrieving projects.

FIXED (Issue-10: Missing Input Sanitization):
============================================
Added field validators to sanitize all user text inputs.

STAGE 3 ADDITIONS:
==================
Added color, icon, is_default, sort_order fields for project customization.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.utils.validation import sanitize_text_input

# Valid project colors (8 preset colors)
VALID_COLORS = [
    "red", "orange", "yellow", "green", "blue", "purple", "gray", "black"
]

# Valid project icons (8 preset icons)
VALID_ICONS = [
    "folder", "shield", "document", "chart", "flask", "briefcase", "target", "star"
]


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
    color: str = Field(
        "blue",
        description="Project color (red, orange, yellow, green, blue, purple, gray, black)"
    )
    icon: str = Field(
        "folder",
        description="Project icon (folder, shield, document, chart, flask, briefcase, target, star)"
    )


class ProjectCreate(ProjectBase):
    """
    Schema for creating a new project.

    Inherits from ProjectBase, no additional fields needed.

    SECURITY: All text fields are sanitized to prevent XSS attacks.
    """

    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """Sanitize name to prevent XSS (single-line field)"""
        return sanitize_text_input(v, allow_newlines=False)

    @field_validator('description')
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize description to prevent XSS (multi-line allowed)"""
        return sanitize_text_input(v, allow_newlines=True) if v else v

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: str) -> str:
        """Validate color is in allowed list"""
        if v not in VALID_COLORS:
            raise ValueError(f"Color must be one of: {', '.join(VALID_COLORS)}")
        return v

    @field_validator('icon')
    @classmethod
    def validate_icon(cls, v: str) -> str:
        """Validate icon is in allowed list"""
        if v not in VALID_ICONS:
            raise ValueError(f"Icon must be one of: {', '.join(VALID_ICONS)}")
        return v


class ProjectUpdate(BaseModel):
    """
    Schema for updating an existing project.

    All fields are optional to support partial updates.

    SECURITY: All text fields are sanitized to prevent XSS attacks.
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
    color: Optional[str] = Field(
        None,
        description="Updated project color"
    )
    icon: Optional[str] = Field(
        None,
        description="Updated project icon"
    )

    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize name to prevent XSS (single-line field)"""
        return sanitize_text_input(v, allow_newlines=False) if v else v

    @field_validator('description')
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize description to prevent XSS (multi-line allowed)"""
        return sanitize_text_input(v, allow_newlines=True) if v else v

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate color is in allowed list"""
        if v is not None and v not in VALID_COLORS:
            raise ValueError(f"Color must be one of: {', '.join(VALID_COLORS)}")
        return v

    @field_validator('icon')
    @classmethod
    def validate_icon(cls, v: Optional[str]) -> Optional[str]:
        """Validate icon is in allowed list"""
        if v is not None and v not in VALID_ICONS:
            raise ValueError(f"Icon must be one of: {', '.join(VALID_ICONS)}")
        return v


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
    is_default: bool = Field(False, description="True if this is the default project")
    sort_order: int = Field(0, description="Manual sort order (0 = first)")
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
    document_count: int = Field(
        0,
        description="Number of documents in this project"
    )


class ProjectListResponse(BaseModel):
    """
    Schema for listing projects with stats.

    Used by GET /api/projects endpoint.
    """
    projects: list[ProjectWithStats]
    total: int = Field(..., description="Total number of projects")


class ProjectReorderRequest(BaseModel):
    """
    Schema for reordering projects.

    Used by PATCH /api/projects/reorder endpoint.
    """
    project_ids: list[int] = Field(
        ...,
        min_length=1,
        description="Array of project IDs in new order (first = top of list)"
    )


class DeleteProjectResponse(BaseModel):
    """
    Schema for delete project response.

    Used by DELETE /api/projects/{id} endpoint.
    """
    message: str
    action: str = Field(..., description="'move' or 'delete'")
    moved_conversations: Optional[int] = None
    moved_documents: Optional[int] = None
    deleted_conversations: Optional[int] = None
    deleted_documents: Optional[int] = None


class MoveConversationRequest(BaseModel):
    """
    Schema for moving conversation to different project.

    Used by PATCH /api/conversations/{id}/move endpoint.
    """
    project_id: int = Field(..., gt=0, description="Target project ID")
