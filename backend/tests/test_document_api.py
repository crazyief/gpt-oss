"""
Integration tests for Document API endpoints.

Tests document upload, list, download, and delete operations.
"""

import io
import pytest
from pathlib import Path
from app.models.database import Project, Document
from app.services.project_service import ProjectService
from app.schemas.project import ProjectCreate


class TestDocumentUpload:
    """Test POST /api/projects/{id}/documents/upload"""

    def test_upload_single_pdf(self, client, test_db):
        """Test uploading a single PDF file"""
        # Create project
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        # Create fake PDF file
        pdf_content = b"%PDF-1.4\n%Test PDF content"
        files = {
            "files": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")
        }

        # Upload file
        response = client.post(
            f"/api/projects/{project.id}/documents/upload",
            files=files
        )

        assert response.status_code == 201
        data = response.json()
        assert len(data["documents"]) == 1
        assert len(data["failed"]) == 0

        doc = data["documents"][0]
        assert doc["original_filename"] == "test.pdf"
        assert doc["mime_type"] == "application/pdf"
        assert doc["file_size"] == len(pdf_content)
        assert doc["project_id"] == project.id

    def test_upload_multiple_files(self, client, test_db):
        """Test uploading multiple files at once"""
        # Create project
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        # Create multiple files
        pdf_content = b"%PDF-1.4\n%Test PDF"
        txt_content = b"Hello world"

        files = [
            ("files", ("test.pdf", io.BytesIO(pdf_content), "application/pdf")),
            ("files", ("test.txt", io.BytesIO(txt_content), "text/plain"))
        ]

        # Upload files
        response = client.post(
            f"/api/projects/{project.id}/documents/upload",
            files=files
        )

        assert response.status_code == 201
        data = response.json()
        assert len(data["documents"]) == 2
        assert len(data["failed"]) == 0

    def test_upload_invalid_file_type(self, client, test_db):
        """Test uploading disallowed file type returns error"""
        # Create project
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        # Create .exe file (not allowed)
        files = {
            "files": ("malware.exe", io.BytesIO(b"MZ\x90\x00"), "application/x-msdownload")
        }

        # Upload file
        response = client.post(
            f"/api/projects/{project.id}/documents/upload",
            files=files
        )

        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"].lower()

    def test_upload_oversized_file(self, client, test_db):
        """Test uploading file exceeding 200MB limit"""
        # Create project
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        # Create file > 200MB (simulate with size check)
        # Note: We can't actually create 200MB in memory for test
        # This would fail at service layer validation
        large_content = b"X" * (200 * 1024 * 1024 + 1)  # 200MB + 1 byte

        files = {
            "files": ("huge.pdf", io.BytesIO(large_content), "application/pdf")
        }

        response = client.post(
            f"/api/projects/{project.id}/documents/upload",
            files=files
        )

        assert response.status_code == 400
        assert "too large" in response.json()["detail"].lower()

    def test_upload_path_traversal_attempt(self, client, test_db):
        """Test uploading file with path traversal in filename"""
        # Create project
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        # Attempt path traversal
        files = {
            "files": ("../../../etc/passwd.txt", io.BytesIO(b"root:x:0:0"), "text/plain")
        }

        response = client.post(
            f"/api/projects/{project.id}/documents/upload",
            files=files
        )

        assert response.status_code == 400
        assert "illegal" in response.json()["detail"].lower() or "path" in response.json()["detail"].lower()

    def test_upload_null_byte_in_filename(self, client, test_db):
        """Test uploading file with null byte in filename"""
        # Create project
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        # Null byte injection attempt
        files = {
            "files": ("test\x00.pdf.txt", io.BytesIO(b"content"), "text/plain")
        }

        response = client.post(
            f"/api/projects/{project.id}/documents/upload",
            files=files
        )

        assert response.status_code == 400
        assert "null byte" in response.json()["detail"].lower()

    def test_upload_mime_type_mismatch(self, client, test_db):
        """Test uploading file where MIME type doesn't match extension"""
        # Create project
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        # Claim PDF but use .exe extension
        files = {
            "files": ("malware.exe", io.BytesIO(b"%PDF-1.4"), "application/pdf")
        }

        response = client.post(
            f"/api/projects/{project.id}/documents/upload",
            files=files
        )

        assert response.status_code == 400
        assert "mime" in response.json()["detail"].lower() or "extension" in response.json()["detail"].lower()

    def test_upload_to_nonexistent_project(self, client, test_db):
        """Test uploading to non-existent project returns 400"""
        files = {
            "files": ("test.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")
        }

        response = client.post(
            "/api/projects/99999/documents/upload",
            files=files
        )

        assert response.status_code == 400
        assert "project not found" in response.json()["detail"].lower()

    def test_upload_no_files(self, client, test_db):
        """Test uploading with no files returns 400"""
        # Create project
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        response = client.post(
            f"/api/projects/{project.id}/documents/upload"
        )

        assert response.status_code == 422  # FastAPI validation error

    def test_upload_too_many_files(self, client, test_db):
        """Test uploading more than 10 files returns 400"""
        # Create project
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        # Create 11 files
        files = [
            ("files", (f"test{i}.txt", io.BytesIO(b"content"), "text/plain"))
            for i in range(11)
        ]

        response = client.post(
            f"/api/projects/{project.id}/documents/upload",
            files=files
        )

        assert response.status_code == 400
        assert "too many" in response.json()["detail"].lower()


class TestDocumentList:
    """Test GET /api/projects/{id}/documents"""

    def test_list_empty_documents(self, client, test_db):
        """Test listing documents in project with no documents"""
        # Create project
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        response = client.get(f"/api/projects/{project.id}/documents")

        assert response.status_code == 200
        data = response.json()
        assert data["documents"] == []
        assert data["total_count"] == 0

    def test_list_documents_with_sorting(self, client, test_db):
        """Test listing documents with different sort options"""
        # Create project
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        # Upload multiple documents
        files = [
            ("files", ("a.txt", io.BytesIO(b"small"), "text/plain")),
            ("files", ("z.txt", io.BytesIO(b"large content here"), "text/plain"))
        ]

        client.post(f"/api/projects/{project.id}/documents/upload", files=files)

        # Test sort by name ascending
        response = client.get(
            f"/api/projects/{project.id}/documents?sort_by=name&sort_order=asc"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["documents"]) == 2
        assert data["documents"][0]["original_filename"] == "a.txt"
        assert data["documents"][1]["original_filename"] == "z.txt"

        # Test sort by size descending
        response = client.get(
            f"/api/projects/{project.id}/documents?sort_by=size&sort_order=desc"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["documents"][0]["file_size"] > data["documents"][1]["file_size"]

    def test_list_documents_with_type_filter(self, client, test_db):
        """Test filtering documents by file type"""
        # Create project
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        # Upload mixed file types
        files = [
            ("files", ("test.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")),
            ("files", ("test.txt", io.BytesIO(b"text"), "text/plain"))
        ]

        client.post(f"/api/projects/{project.id}/documents/upload", files=files)

        # Filter for PDF only
        response = client.get(
            f"/api/projects/{project.id}/documents?filter_type=pdf"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["documents"]) == 1
        assert data["documents"][0]["mime_type"] == "application/pdf"


class TestDocumentGet:
    """Test GET /api/documents/{id}"""

    def test_get_document_metadata(self, client, test_db):
        """Test getting document metadata"""
        # Create project and upload document
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        files = {
            "files": ("test.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")
        }

        upload_response = client.post(
            f"/api/projects/{project.id}/documents/upload",
            files=files
        )

        doc_id = upload_response.json()["documents"][0]["id"]

        # Get document metadata
        response = client.get(f"/api/documents/{doc_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == doc_id
        assert data["original_filename"] == "test.pdf"
        assert data["mime_type"] == "application/pdf"

    def test_get_nonexistent_document(self, client, test_db):
        """Test getting non-existent document returns 404"""
        response = client.get("/api/documents/99999")

        assert response.status_code == 404


class TestDocumentDownload:
    """Test GET /api/documents/{id}/download"""

    def test_download_document(self, client, test_db):
        """Test downloading a document file"""
        # Create project and upload document
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        pdf_content = b"%PDF-1.4\n%Test PDF content"
        files = {
            "files": ("report.pdf", io.BytesIO(pdf_content), "application/pdf")
        }

        upload_response = client.post(
            f"/api/projects/{project.id}/documents/upload",
            files=files
        )

        doc_id = upload_response.json()["documents"][0]["id"]

        # Download document
        response = client.get(f"/api/documents/{doc_id}/download")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert 'attachment; filename="report.pdf"' in response.headers["content-disposition"]
        assert response.content == pdf_content

    def test_download_nonexistent_document(self, client, test_db):
        """Test downloading non-existent document returns 404"""
        response = client.get("/api/documents/99999/download")

        assert response.status_code == 404


class TestDocumentDelete:
    """Test DELETE /api/documents/{id}"""

    def test_delete_document(self, client, test_db):
        """Test deleting a document"""
        # Create project and upload document
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        files = {
            "files": ("test.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")
        }

        upload_response = client.post(
            f"/api/projects/{project.id}/documents/upload",
            files=files
        )

        doc_id = upload_response.json()["documents"][0]["id"]

        # Delete document
        response = client.delete(f"/api/documents/{doc_id}")

        assert response.status_code == 204

        # Verify document is gone
        get_response = client.get(f"/api/documents/{doc_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_document(self, client, test_db):
        """Test deleting non-existent document returns 404"""
        response = client.delete("/api/documents/99999")

        assert response.status_code == 404


class TestProjectStatsWithDocuments:
    """Test GET /api/projects/{id}/stats with documents"""

    def test_project_stats_includes_documents(self, client, test_db):
        """Test project stats include document count and size"""
        # Create project
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        # Upload documents
        files = [
            ("files", ("small.txt", io.BytesIO(b"small"), "text/plain")),
            ("files", ("large.txt", io.BytesIO(b"large content"), "text/plain"))
        ]

        client.post(f"/api/projects/{project.id}/documents/upload", files=files)

        # Get stats
        response = client.get(f"/api/projects/{project.id}/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["document_count"] == 2
        assert data["total_document_size"] == 5 + 13  # "small" + "large content"
        assert data["last_activity_at"] is not None


class TestProjectDeleteCascade:
    """Test DELETE /api/projects/{id} with cascade to documents"""

    def test_delete_project_removes_documents(self, client, test_db):
        """Test deleting project also deletes all documents"""
        # Create project
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        # Upload document
        files = {
            "files": ("test.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")
        }

        upload_response = client.post(
            f"/api/projects/{project.id}/documents/upload",
            files=files
        )

        doc_id = upload_response.json()["documents"][0]["id"]

        # Delete project
        response = client.delete(f"/api/projects/{project.id}")

        assert response.status_code == 204

        # Verify document is also gone
        doc_response = client.get(f"/api/documents/{doc_id}")
        assert doc_response.status_code == 404
