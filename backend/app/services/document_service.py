"""
Document service layer for file management.

Handles document upload, storage, retrieval, and deletion.
Validation logic is delegated to document_validation module.
"""

from typing import Optional
from pathlib import Path
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.models.database import Document, Project
from app.schemas.document import FailedUpload
from app.services.document_validation import (
    validate_filename,
    validate_mime_type,
    validate_file_size,
    generate_safe_filename,
    ALLOWED_TYPES,
    MAX_FILE_SIZE,
    UPLOAD_BASE_DIR,
)


class DocumentService:
    """
    Service class for document CRUD and storage operations.

    Validation is delegated to document_validation module.
    This class handles database and filesystem operations.
    """

    # Re-export constants for backward compatibility
    MAX_FILE_SIZE = MAX_FILE_SIZE
    UPLOAD_BASE_DIR = UPLOAD_BASE_DIR
    ALLOWED_TYPES = ALLOWED_TYPES

    # Delegate validation methods for backward compatibility
    validate_filename = staticmethod(validate_filename)
    validate_mime_type = staticmethod(validate_mime_type)
    generate_safe_filename = staticmethod(generate_safe_filename)

    @staticmethod
    async def save_file(
        db: Session,
        project_id: int,
        file: UploadFile
    ) -> tuple[Optional[Document], Optional[FailedUpload]]:
        """
        Save uploaded file to disk and create database record.

        Args:
            db: Database session
            project_id: Target project ID
            file: Uploaded file object

        Returns:
            Tuple of (document, failed_upload)
            Success: (Document instance, None)
            Failure: (None, FailedUpload instance)
        """
        # Validate project exists
        project = db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.deleted_at.is_(None)
            )
        ).scalar_one_or_none()

        if not project:
            return None, FailedUpload(
                filename=file.filename or "unknown",
                error="Project not found"
            )

        # Get file info
        original_filename = file.filename or "unnamed"
        mime_type = file.content_type or "application/octet-stream"

        # Validate filename
        is_valid, error = validate_filename(original_filename)
        if not is_valid:
            return None, FailedUpload(
                filename=original_filename,
                error=error or "Invalid filename"
            )

        # Validate MIME type
        is_valid, error = validate_mime_type(mime_type, original_filename)
        if not is_valid:
            return None, FailedUpload(
                filename=original_filename,
                error=error or "Invalid MIME type"
            )

        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Validate file size
        is_valid, error = validate_file_size(file_size)
        if not is_valid:
            return None, FailedUpload(
                filename=original_filename,
                error=error or "File too large"
            )

        # Generate safe filename
        safe_filename = generate_safe_filename(original_filename)

        # Create project directory if not exists
        project_dir = Path(UPLOAD_BASE_DIR) / str(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)

        # Full file path
        file_path = project_dir / safe_filename

        try:
            # Write file to disk
            with open(file_path, "wb") as f:
                f.write(file_content)

            # Create database record
            document = Document(
                project_id=project_id,
                filename=safe_filename,
                original_filename=original_filename,
                file_path=str(file_path),
                file_size=file_size,
                mime_type=mime_type
            )

            db.add(document)
            db.commit()
            db.refresh(document)

            return document, None

        except Exception as e:
            # Cleanup: delete file if database insert fails
            if file_path.exists():
                file_path.unlink()

            return None, FailedUpload(
                filename=original_filename,
                error=f"Failed to save file: {str(e)}"
            )

    @staticmethod
    def get_document_by_id(db: Session, document_id: int) -> Optional[Document]:
        """
        Get a document by ID.

        Returns None if document not found or parent project is deleted.
        """
        stmt = select(Document).join(Document.project).where(
            Document.id == document_id,
            Project.deleted_at.is_(None)
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def list_documents(
        db: Session,
        project_id: int,
        sort_by: str = "date",
        sort_order: str = "desc",
        filter_type: Optional[str] = None
    ) -> tuple[list[Document], int]:
        """
        List documents in a project with sorting and filtering.

        Args:
            db: Database session
            project_id: Project ID
            sort_by: Sort field (name, date, size, type)
            sort_order: Sort direction (asc, desc)
            filter_type: Filter by extension (e.g., "pdf")

        Returns:
            Tuple of (documents list, total count)
        """
        # Build base query
        query = select(Document).where(Document.project_id == project_id)

        # Apply filter by type
        if filter_type:
            ext = f".{filter_type.lower()}"
            matching_mimes = [
                mime for mime, exts in ALLOWED_TYPES.items()
                if ext in exts
            ]
            if matching_mimes:
                query = query.where(Document.mime_type.in_(matching_mimes))

        # Get total count
        count_stmt = select(func.count()).select_from(query.subquery())
        total_count = db.execute(count_stmt).scalar_one()

        # Apply sorting
        sort_column_map = {
            "name": Document.original_filename,
            "date": Document.uploaded_at,
            "size": Document.file_size,
            "type": Document.mime_type
        }

        sort_column = sort_column_map.get(sort_by, Document.uploaded_at)

        if sort_order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        documents = db.execute(query).scalars().all()
        return list(documents), total_count

    @staticmethod
    def delete_document(db: Session, document_id: int) -> bool:
        """
        Delete document (file and database record).

        HARD DELETE: Permanently removes file and record.

        Returns:
            True if deleted, False if not found
        """
        document = DocumentService.get_document_by_id(db, document_id)
        if not document:
            return False

        # Delete file from disk
        file_path = Path(document.file_path)
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                pass  # Continue with DB deletion

        db.delete(document)
        db.commit()
        return True

    @staticmethod
    def delete_project_documents(db: Session, project_id: int) -> int:
        """
        Delete all documents for a project (cascade delete).

        Returns:
            Number of documents deleted
        """
        documents = db.execute(
            select(Document).where(Document.project_id == project_id)
        ).scalars().all()

        # Delete files
        for document in documents:
            file_path = Path(document.file_path)
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception:
                    pass

        # Delete database records
        count = len(documents)
        for document in documents:
            db.delete(document)

        db.commit()

        # Remove project directory if empty
        project_dir = Path(UPLOAD_BASE_DIR) / str(project_id)
        if project_dir.exists():
            try:
                project_dir.rmdir()
            except Exception:
                pass

        return count
