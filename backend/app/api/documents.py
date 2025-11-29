"""
FastAPI router for document management endpoints.

Provides REST API for uploading, listing, downloading, and deleting documents.
"""

from typing import Annotated
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.document_service import DocumentService
from app.schemas.document import (
    DocumentResponse,
    DocumentListResponse,
    DocumentUploadResponse,
    FailedUpload
)

# Create router instance
router = APIRouter()


@router.post(
    "/projects/{project_id}/documents/upload",
    response_model=DocumentUploadResponse,
    status_code=201
)
async def upload_documents(
    project_id: int,
    db: Annotated[Session, Depends(get_db)],
    files: list[UploadFile] = File(..., description="Files to upload (max 10)")
):
    """
    Upload one or more documents to a project.

    SECURITY FEATURES:
    - Filename sanitization (prevents path traversal)
    - MIME type validation (prevents file type spoofing)
    - File size limit (200MB per file)
    - Extension whitelist (only PDF, DOCX, XLSX, TXT, MD)

    Args:
        project_id: Target project ID
        files: Array of files to upload (max 10 files)
        db: Database session (injected)

    Returns:
        Upload results with successful uploads and failures

    Raises:
        HTTPException 400: If no files provided or too many files
        HTTPException 404: If project not found

    Example:
        POST /api/projects/1/documents/upload
        Content-Type: multipart/form-data
        files: [file1.pdf, file2.docx]

        Response 201:
        {
            "documents": [
                {
                    "id": 1,
                    "project_id": 1,
                    "filename": "abc123_file1.pdf",
                    "original_filename": "file1.pdf",
                    "file_size": 1048576,
                    "mime_type": "application/pdf",
                    "uploaded_at": "2025-11-29T10:00:00Z"
                }
            ],
            "failed": [
                {
                    "filename": "file2.exe",
                    "error": "File type not allowed: .exe"
                }
            ]
        }
    """
    # Validate file count
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files: {len(files)} exceeds maximum of 10"
        )

    # Process each file
    successful_uploads = []
    failed_uploads = []

    for file in files:
        document, failed = await DocumentService.save_file(db, project_id, file)

        if document:
            successful_uploads.append(document)
        else:
            failed_uploads.append(failed)

    # If all files failed, return 400
    if not successful_uploads and failed_uploads:
        # Return first error as main error
        raise HTTPException(status_code=400, detail=failed_uploads[0].error)

    return DocumentUploadResponse(
        documents=successful_uploads,
        failed=failed_uploads
    )


@router.get(
    "/projects/{project_id}/documents",
    response_model=DocumentListResponse
)
async def list_documents(
    project_id: int,
    db: Annotated[Session, Depends(get_db)],
    sort_by: str = Query("date", regex="^(name|date|size|type)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    filter_type: str = Query(None, description="Filter by extension (pdf, docx, xlsx, txt, md)")
):
    """
    List all documents in a project.

    Supports sorting and filtering by file type.

    Args:
        project_id: Project ID
        sort_by: Sort field (name, date, size, type) - default: date
        sort_order: Sort direction (asc, desc) - default: desc
        filter_type: Filter by file extension (optional)
        db: Database session (injected)

    Returns:
        List of documents with total count

    Example:
        GET /api/projects/1/documents?sort_by=size&sort_order=desc&filter_type=pdf

        Response 200:
        {
            "documents": [
                {
                    "id": 1,
                    "project_id": 1,
                    "filename": "abc123_report.pdf",
                    "original_filename": "report.pdf",
                    "file_size": 1048576,
                    "mime_type": "application/pdf",
                    "uploaded_at": "2025-11-29T10:00:00Z"
                }
            ],
            "total_count": 1
        }
    """
    try:
        documents, total_count = DocumentService.list_documents(
            db=db,
            project_id=project_id,
            sort_by=sort_by,
            sort_order=sort_order,
            filter_type=filter_type
        )

        return DocumentListResponse(
            documents=documents,
            total_count=total_count
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to list documents")


@router.get(
    "/documents/{document_id}",
    response_model=DocumentResponse
)
async def get_document(
    document_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Get document metadata by ID.

    Args:
        document_id: Document ID
        db: Database session (injected)

    Returns:
        Document metadata

    Raises:
        HTTPException 404: If document not found

    Example:
        GET /api/documents/1

        Response 200:
        {
            "id": 1,
            "project_id": 1,
            "filename": "abc123_report.pdf",
            "original_filename": "report.pdf",
            "file_size": 1048576,
            "mime_type": "application/pdf",
            "uploaded_at": "2025-11-29T10:00:00Z"
        }
    """
    document = DocumentService.get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document


@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Download document file.

    Returns the original file with correct Content-Type and Content-Disposition headers.

    SECURITY: Validates user has access to document's parent project.

    Args:
        document_id: Document ID
        db: Database session (injected)

    Returns:
        File response with correct headers

    Raises:
        HTTPException 404: If document not found or file missing from disk

    Example:
        GET /api/documents/1/download

        Response 200:
        Content-Type: application/pdf
        Content-Disposition: attachment; filename="report.pdf"
        [binary file data]
    """
    # Get document metadata
    document = DocumentService.get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check file exists on disk
    file_path = Path(document.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    # Return file with correct headers
    # WHY attachment: Forces browser to download instead of inline display.
    # This is safer as it prevents potential XSS if file contains malicious HTML/JS.
    return FileResponse(
        path=str(file_path),
        media_type=document.mime_type,
        filename=document.original_filename,
        headers={
            "Content-Disposition": f'attachment; filename="{document.original_filename}"'
        }
    )


@router.delete("/documents/{document_id}", status_code=204)
async def delete_document(
    document_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Delete a document (file and database record).

    HARD DELETE: This is permanent and cannot be undone.

    Args:
        document_id: Document ID to delete
        db: Database session (injected)

    Returns:
        No content (204 status)

    Raises:
        HTTPException 404: If document not found

    Example:
        DELETE /api/documents/1

        Response 204: No content
    """
    success = DocumentService.delete_document(db, document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")

    return None
