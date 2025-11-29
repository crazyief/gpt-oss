"""
Pydantic schemas for Document API requests and responses.

Defines validation models for document upload, retrieval, and metadata.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class DocumentBase(BaseModel):
    """
    Base schema for Document with common fields.

    Used as a parent class for response schemas.
    """
    filename: str = Field(..., description="Stored filename (with UUID prefix)")
    original_filename: str = Field(..., description="Original filename from user")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type (e.g., application/pdf)")


class DocumentResponse(DocumentBase):
    """
    Schema for document API responses.

    Includes all database fields including ID, project_id, and timestamp.
    """
    id: int = Field(..., description="Unique document ID")
    project_id: int = Field(..., description="Parent project ID")
    uploaded_at: datetime = Field(..., description="Upload timestamp")

    # Pydantic v2 configuration
    # from_attributes allows creating from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    """
    Schema for document list API response.

    Returns array of documents and total count for pagination.
    """
    documents: list[DocumentResponse] = Field(
        default_factory=list,
        description="Array of document objects"
    )
    total_count: int = Field(0, description="Total number of documents")


class FailedUpload(BaseModel):
    """
    Schema for failed upload information.

    Returned when a file upload fails validation or processing.
    """
    filename: str = Field(..., description="Name of the file that failed")
    error: str = Field(..., description="Error message describing why upload failed")


class DocumentUploadResponse(BaseModel):
    """
    Schema for document upload API response.

    Returns successfully uploaded documents and any failures.
    """
    documents: list[DocumentResponse] = Field(
        default_factory=list,
        description="Successfully uploaded documents"
    )
    failed: list[FailedUpload] = Field(
        default_factory=list,
        description="Files that failed to upload"
    )
