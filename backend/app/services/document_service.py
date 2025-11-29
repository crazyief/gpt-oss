"""
Document service layer for file management.

Handles document upload, storage, retrieval, and deletion with
security validation and filesystem operations.
"""

import os
import re
import uuid
import shutil
from typing import Optional
from pathlib import Path
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.models.database import Document, Project
from app.schemas.document import FailedUpload


class DocumentService:
    """
    Service class for document-related business logic.

    Encapsulates file upload validation, storage, and database operations.
    All file operations are performed securely with validation.
    """

    # Configuration constants
    MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB in bytes
    UPLOAD_BASE_DIR = "uploads"

    # Allowed MIME types and extensions
    # WHY this mapping: Validates both MIME type (from browser) and extension
    # (from filename) to prevent file type spoofing attacks.
    ALLOWED_TYPES = {
        "application/pdf": [".pdf"],
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
        "text/plain": [".txt"],
        "text/markdown": [".md"],
    }

    @staticmethod
    def validate_filename(filename: str) -> tuple[bool, Optional[str]]:
        """
        Validate and sanitize filename for security.

        SECURITY CHECKS:
        - Reject path traversal attempts (../, ..\, absolute paths)
        - Reject null bytes (filesystem injection)
        - Reject control characters (terminal injection)
        - Check extension is allowed

        Args:
            filename: Original filename from upload

        Returns:
            Tuple of (is_valid, error_message)
            If valid: (True, None)
            If invalid: (False, "Error description")

        Examples:
            validate_filename("report.pdf") → (True, None)
            validate_filename("../etc/passwd") → (False, "Illegal path characters")
            validate_filename("file\x00.pdf") → (False, "Null byte detected")
        """
        # Check for null bytes (filesystem injection)
        if "\x00" in filename:
            return False, "Null byte detected in filename"

        # Check for path traversal attempts
        # WHY this regex: Catches ../, ..\, /../, \..\, and absolute paths
        if re.search(r'(\.\.[/\\]|^[/\\]|^[A-Za-z]:)', filename):
            return False, "Illegal path characters in filename"

        # Check for control characters (ASCII 0-31, 127)
        # WHY: Prevents terminal injection and filename display corruption
        if re.search(r'[\x00-\x1f\x7f]', filename):
            return False, "Control characters in filename"

        # Extract extension
        ext = Path(filename).suffix.lower()

        # Check extension is allowed
        allowed_extensions = [ext for exts in DocumentService.ALLOWED_TYPES.values() for ext in exts]
        if ext not in allowed_extensions:
            return False, f"File type not allowed: {ext}"

        return True, None

    @staticmethod
    def validate_mime_type(mime_type: str, filename: str) -> tuple[bool, Optional[str]]:
        """
        Validate MIME type matches file extension.

        SECURITY: Prevents file type spoofing where malicious files
        claim to be safe types via MIME type.

        Args:
            mime_type: Content-Type from upload
            filename: Original filename

        Returns:
            Tuple of (is_valid, error_message)

        Example:
            validate_mime_type("application/pdf", "doc.pdf") → (True, None)
            validate_mime_type("application/pdf", "doc.exe") → (False, "Extension mismatch")
        """
        # Check MIME type is allowed
        if mime_type not in DocumentService.ALLOWED_TYPES:
            return False, f"MIME type not allowed: {mime_type}"

        # Extract extension
        ext = Path(filename).suffix.lower()

        # Check extension matches MIME type
        allowed_extensions = DocumentService.ALLOWED_TYPES[mime_type]
        if ext not in allowed_extensions:
            return False, f"MIME type {mime_type} does not match extension {ext}"

        return True, None

    @staticmethod
    def generate_safe_filename(original_filename: str) -> str:
        """
        Generate safe filename with UUID prefix.

        WHY UUID prefix: Prevents filename collisions and makes filenames
        unpredictable (security through obscurity for direct access attempts).

        Args:
            original_filename: User's original filename

        Returns:
            Safe filename with UUID prefix (e.g., "abc123-def456_report.pdf")

        Example:
            generate_safe_filename("report.pdf") → "abc123-def456_report.pdf"
        """
        # Generate UUID
        file_uuid = str(uuid.uuid4())

        # Sanitize original filename (remove any remaining path separators)
        safe_original = os.path.basename(original_filename)

        # Combine: uuid_originalname
        return f"{file_uuid}_{safe_original}"

    @staticmethod
    async def save_file(
        db: Session,
        project_id: int,
        file: UploadFile
    ) -> tuple[Optional[Document], Optional[FailedUpload]]:
        """
        Save uploaded file to disk and create database record.

        SECURITY VALIDATIONS:
        - Filename sanitization (no path traversal)
        - MIME type validation
        - File size limit (200MB)
        - Project existence check

        Args:
            db: Database session
            project_id: Target project ID
            file: Uploaded file object

        Returns:
            Tuple of (document, failed_upload)
            Success: (Document instance, None)
            Failure: (None, FailedUpload instance)

        Side Effects:
            - Creates uploads/{project_id}/ directory if not exists
            - Writes file to disk
            - Creates database record
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
        is_valid, error = DocumentService.validate_filename(original_filename)
        if not is_valid:
            return None, FailedUpload(
                filename=original_filename,
                error=error or "Invalid filename"
            )

        # Validate MIME type
        is_valid, error = DocumentService.validate_mime_type(mime_type, original_filename)
        if not is_valid:
            return None, FailedUpload(
                filename=original_filename,
                error=error or "Invalid MIME type"
            )

        # Read file into memory (to check size and write to disk)
        # WHY read entire file: Need to validate size before committing to disk.
        # 200MB max means this is safe (won't OOM with reasonable RAM).
        file_content = await file.read()
        file_size = len(file_content)

        # Validate file size
        if file_size > DocumentService.MAX_FILE_SIZE:
            return None, FailedUpload(
                filename=original_filename,
                error=f"File too large: {file_size} bytes exceeds {DocumentService.MAX_FILE_SIZE} bytes limit"
            )

        # Generate safe filename
        safe_filename = DocumentService.generate_safe_filename(original_filename)

        # Create project directory if not exists
        project_dir = Path(DocumentService.UPLOAD_BASE_DIR) / str(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)

        # Full file path
        file_path = project_dir / safe_filename

        try:
            # Write file to disk
            # WHY write binary: Preserves exact file content without encoding issues
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

        Args:
            db: Database session
            document_id: Document ID to retrieve

        Returns:
            Document instance or None if not found

        Note:
            Returns None if parent project is soft-deleted.
        """
        stmt = select(Document).join(Document.project).where(
            Document.id == document_id,
            Project.deleted_at.is_(None)  # Exclude documents from deleted projects
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
            project_id: Project ID to list documents for
            sort_by: Sort field (name, date, size, type)
            sort_order: Sort direction (asc, desc)
            filter_type: Filter by file extension (e.g., "pdf", "docx")

        Returns:
            Tuple of (documents list, total count)

        Example:
            list_documents(db, 1, "size", "desc", "pdf")
            → Returns all PDFs in project 1, sorted by size descending
        """
        # Build base query
        query = select(Document).where(Document.project_id == project_id)

        # Apply filter by type (extension)
        if filter_type:
            # Convert filter_type to extension (e.g., "pdf" → ".pdf")
            ext = f".{filter_type.lower()}"
            # Find matching MIME types
            matching_mimes = [
                mime for mime, exts in DocumentService.ALLOWED_TYPES.items()
                if ext in exts
            ]
            if matching_mimes:
                query = query.where(Document.mime_type.in_(matching_mimes))

        # Get total count (before sorting)
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

        # Execute query
        documents = db.execute(query).scalars().all()

        return list(documents), total_count

    @staticmethod
    def delete_document(db: Session, document_id: int) -> bool:
        """
        Delete document (file and database record).

        HARD DELETE: This is a permanent deletion, not soft delete.
        WHY hard delete: Document files are user-uploaded content, not system data.
        Users expect deletion to actually remove files from disk to free space.

        Args:
            db: Database session
            document_id: Document ID to delete

        Returns:
            True if deleted successfully, False if not found

        Side Effects:
            - Deletes file from filesystem
            - Deletes database record
        """
        # Get document
        document = DocumentService.get_document_by_id(db, document_id)
        if not document:
            return False

        # Delete file from disk
        file_path = Path(document.file_path)
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                # Log error but continue with database deletion
                # WHY continue: Database record becomes stale if file is already gone
                pass

        # Delete database record
        db.delete(document)
        db.commit()

        return True

    @staticmethod
    def delete_project_documents(db: Session, project_id: int) -> int:
        """
        Delete all documents for a project (cascade delete).

        Used when deleting a project to clean up all associated files.

        Args:
            db: Database session
            project_id: Project ID

        Returns:
            Number of documents deleted

        Side Effects:
            - Deletes all files from uploads/{project_id}/
            - Deletes all database records
            - Removes project directory
        """
        # Get all documents for project
        documents = db.execute(
            select(Document).where(Document.project_id == project_id)
        ).scalars().all()

        # Delete each file
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
        project_dir = Path(DocumentService.UPLOAD_BASE_DIR) / str(project_id)
        if project_dir.exists():
            try:
                project_dir.rmdir()  # Only succeeds if directory is empty
            except Exception:
                # Directory not empty or other error - ignore
                pass

        return count
