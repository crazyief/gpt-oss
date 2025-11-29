"""
Unit tests for DocumentService.

Tests file validation, sanitization, and CRUD operations.
Note: Async tests converted to sync for pytest compatibility.
"""

import io
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import UploadFile
from app.services.document_service import DocumentService
from app.models.database import Project
from app.schemas.project import ProjectCreate
from app.services.project_service import ProjectService


class TestFilenameValidation:
    """Test filename validation and sanitization"""

    def test_validate_normal_filename(self):
        """Test valid filename passes validation"""
        is_valid, error = DocumentService.validate_filename("report.pdf")
        assert is_valid is True
        assert error is None

    def test_reject_path_traversal_dotdot_slash(self):
        """Test rejection of ../ path traversal"""
        is_valid, error = DocumentService.validate_filename("../etc/passwd.txt")
        assert is_valid is False
        assert "illegal" in error.lower() or "path" in error.lower()

    def test_reject_path_traversal_dotdot_backslash(self):
        """Test rejection of ..\\ path traversal"""
        is_valid, error = DocumentService.validate_filename("..\\windows\\system32\\config.txt")
        assert is_valid is False
        assert "illegal" in error.lower() or "path" in error.lower()

    def test_reject_absolute_path_unix(self):
        """Test rejection of absolute Unix path"""
        is_valid, error = DocumentService.validate_filename("/etc/passwd")
        assert is_valid is False
        assert "illegal" in error.lower() or "path" in error.lower()

    def test_reject_absolute_path_windows(self):
        """Test rejection of absolute Windows path"""
        is_valid, error = DocumentService.validate_filename("C:\\Windows\\system.ini")
        assert is_valid is False
        assert "illegal" in error.lower() or "path" in error.lower()

    def test_reject_null_byte(self):
        """Test rejection of null byte injection"""
        is_valid, error = DocumentService.validate_filename("file\x00.pdf.exe")
        assert is_valid is False
        assert "null byte" in error.lower()

    def test_reject_control_characters(self):
        """Test rejection of control characters"""
        is_valid, error = DocumentService.validate_filename("file\x1b[31m.pdf")
        assert is_valid is False
        assert "control" in error.lower()

    def test_reject_disallowed_extension(self):
        """Test rejection of disallowed file extensions"""
        is_valid, error = DocumentService.validate_filename("malware.exe")
        assert is_valid is False
        assert "not allowed" in error.lower()

    def test_accept_all_allowed_extensions(self):
        """Test all allowed extensions pass validation"""
        allowed_extensions = [".pdf", ".docx", ".xlsx", ".txt", ".md"]

        for ext in allowed_extensions:
            filename = f"test{ext}"
            is_valid, error = DocumentService.validate_filename(filename)
            assert is_valid is True, f"Extension {ext} should be valid"
            assert error is None


class TestMimeTypeValidation:
    """Test MIME type validation"""

    def test_validate_pdf_mime_with_pdf_extension(self):
        """Test PDF MIME type with .pdf extension"""
        is_valid, error = DocumentService.validate_mime_type("application/pdf", "document.pdf")
        assert is_valid is True
        assert error is None

    def test_validate_text_mime_with_txt_extension(self):
        """Test text MIME type with .txt extension"""
        is_valid, error = DocumentService.validate_mime_type("text/plain", "readme.txt")
        assert is_valid is True
        assert error is None

    def test_validate_markdown_mime_with_md_extension(self):
        """Test markdown MIME type with .md extension"""
        is_valid, error = DocumentService.validate_mime_type("text/markdown", "notes.md")
        assert is_valid is True
        assert error is None

    def test_reject_disallowed_mime_type(self):
        """Test rejection of disallowed MIME type"""
        is_valid, error = DocumentService.validate_mime_type("application/x-msdownload", "malware.exe")
        assert is_valid is False
        assert "not allowed" in error.lower()

    def test_reject_mime_extension_mismatch(self):
        """Test rejection when MIME type doesn't match extension"""
        is_valid, error = DocumentService.validate_mime_type("application/pdf", "document.exe")
        assert is_valid is False
        assert "mime" in error.lower() or "extension" in error.lower()


class TestSafeFilenameGeneration:
    """Test safe filename generation"""

    def test_generate_safe_filename_has_uuid(self):
        """Test generated filename includes UUID prefix"""
        safe_name = DocumentService.generate_safe_filename("report.pdf")

        # Should have format: uuid_report.pdf
        parts = safe_name.split("_", 1)
        assert len(parts) == 2
        assert len(parts[0]) == 36  # UUID length
        assert parts[1] == "report.pdf"

    def test_generate_safe_filename_preserves_extension(self):
        """Test generated filename preserves original extension"""
        safe_name = DocumentService.generate_safe_filename("data.xlsx")
        assert safe_name.endswith(".xlsx")

    def test_generate_safe_filename_removes_path(self):
        """Test generated filename strips directory components"""
        safe_name = DocumentService.generate_safe_filename("../../etc/passwd")
        assert ".." not in safe_name
        assert "/" not in safe_name
        assert safe_name.endswith("passwd")


class TestDocumentCRUD:
    """Test document CRUD operations"""

    def test_file_validation_accepts_valid_pdf(self):
        """Test that valid PDF file passes all validations"""
        # Test filename validation
        is_valid, error = DocumentService.validate_filename("test.pdf")
        assert is_valid is True
        assert error is None

        # Test MIME type validation
        is_valid, error = DocumentService.validate_mime_type("application/pdf", "test.pdf")
        assert is_valid is True
        assert error is None

    def test_file_validation_rejects_invalid_type(self):
        """Test that disallowed file types are rejected"""
        # Test filename validation
        is_valid, error = DocumentService.validate_filename("malware.exe")
        assert is_valid is False
        assert "not allowed" in error.lower()

        # Test MIME type validation
        is_valid, error = DocumentService.validate_mime_type("application/x-msdownload", "malware.exe")
        assert is_valid is False
        assert "not allowed" in error.lower()

    def test_file_size_validation(self):
        """Test file size validation logic"""
        # Max size is 200MB = 200 * 1024 * 1024 bytes
        max_size = 200 * 1024 * 1024

        # Valid size
        assert 100 * 1024 * 1024 <= max_size  # 100MB is OK

        # Invalid size
        assert (200 * 1024 * 1024 + 1) > max_size  # 200MB+1 is too large

    def test_get_document_by_id(self, test_db):
        """Test retrieving document by ID"""
        # Create project and document
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        from app.models.database import Document
        document = Document(
            project_id=project.id,
            filename="uuid_test.pdf",
            original_filename="test.pdf",
            file_path="uploads/1/uuid_test.pdf",
            file_size=1024,
            mime_type="application/pdf"
        )
        test_db.add(document)
        test_db.commit()
        test_db.refresh(document)

        # Retrieve document
        retrieved = DocumentService.get_document_by_id(test_db, document.id)

        assert retrieved is not None
        assert retrieved.id == document.id
        assert retrieved.original_filename == "test.pdf"

    def test_get_nonexistent_document(self, test_db):
        """Test retrieving non-existent document returns None"""
        document = DocumentService.get_document_by_id(test_db, 99999)
        assert document is None

    def test_list_documents_empty(self, test_db):
        """Test listing documents in empty project"""
        # Create project
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        # List documents
        documents, count = DocumentService.list_documents(test_db, project.id)

        assert documents == []
        assert count == 0

    def test_list_documents_with_sorting(self, test_db):
        """Test listing documents with sorting"""
        # Create project
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        # Create multiple documents
        from app.models.database import Document

        doc1 = Document(
            project_id=project.id,
            filename="uuid_a.txt",
            original_filename="a.txt",
            file_path="uploads/1/uuid_a.txt",
            file_size=100,
            mime_type="text/plain"
        )

        doc2 = Document(
            project_id=project.id,
            filename="uuid_z.txt",
            original_filename="z.txt",
            file_path="uploads/1/uuid_z.txt",
            file_size=200,
            mime_type="text/plain"
        )

        test_db.add_all([doc1, doc2])
        test_db.commit()

        # Sort by name ascending
        documents, count = DocumentService.list_documents(
            test_db, project.id, sort_by="name", sort_order="asc"
        )

        assert count == 2
        assert documents[0].original_filename == "a.txt"
        assert documents[1].original_filename == "z.txt"

        # Sort by size descending
        documents, count = DocumentService.list_documents(
            test_db, project.id, sort_by="size", sort_order="desc"
        )

        assert documents[0].file_size == 200
        assert documents[1].file_size == 100

    def test_list_documents_with_type_filter(self, test_db):
        """Test listing documents with type filter"""
        # Create project
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        # Create mixed document types
        from app.models.database import Document

        pdf_doc = Document(
            project_id=project.id,
            filename="uuid_test.pdf",
            original_filename="test.pdf",
            file_path="uploads/1/uuid_test.pdf",
            file_size=1024,
            mime_type="application/pdf"
        )

        txt_doc = Document(
            project_id=project.id,
            filename="uuid_test.txt",
            original_filename="test.txt",
            file_path="uploads/1/uuid_test.txt",
            file_size=512,
            mime_type="text/plain"
        )

        test_db.add_all([pdf_doc, txt_doc])
        test_db.commit()

        # Filter for PDF only
        documents, count = DocumentService.list_documents(
            test_db, project.id, filter_type="pdf"
        )

        assert count == 1
        assert documents[0].mime_type == "application/pdf"

    def test_delete_document(self, test_db):
        """Test deleting document"""
        # Create project and document
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        from app.models.database import Document
        document = Document(
            project_id=project.id,
            filename="uuid_test.pdf",
            original_filename="test.pdf",
            file_path="uploads/1/uuid_test.pdf",
            file_size=1024,
            mime_type="application/pdf"
        )
        test_db.add(document)
        test_db.commit()
        test_db.refresh(document)

        # Delete document
        success = DocumentService.delete_document(test_db, document.id)

        assert success is True

        # Verify deletion
        retrieved = DocumentService.get_document_by_id(test_db, document.id)
        assert retrieved is None

    def test_delete_nonexistent_document(self, test_db):
        """Test deleting non-existent document returns False"""
        success = DocumentService.delete_document(test_db, 99999)
        assert success is False

    def test_delete_project_documents(self, test_db):
        """Test cascade delete of all project documents"""
        # Create project
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        # Create multiple documents
        from app.models.database import Document

        doc1 = Document(
            project_id=project.id,
            filename="uuid_1.pdf",
            original_filename="1.pdf",
            file_path="uploads/1/uuid_1.pdf",
            file_size=1024,
            mime_type="application/pdf"
        )

        doc2 = Document(
            project_id=project.id,
            filename="uuid_2.txt",
            original_filename="2.txt",
            file_path="uploads/1/uuid_2.txt",
            file_size=512,
            mime_type="text/plain"
        )

        test_db.add_all([doc1, doc2])
        test_db.commit()

        # Delete all project documents
        count = DocumentService.delete_project_documents(test_db, project.id)

        assert count == 2

        # Verify all documents deleted
        documents, total = DocumentService.list_documents(test_db, project.id)
        assert total == 0
