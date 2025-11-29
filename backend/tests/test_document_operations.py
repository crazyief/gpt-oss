"""
Integration tests for Document Operations API.

Tests list, get, download, and delete endpoints.
"""

import io
import pytest
from app.services.project_service import ProjectService
from app.schemas.project import ProjectCreate


class TestDocumentList:
    """Test GET /api/projects/{id}/documents"""

    def test_list_empty_documents(self, client, test_db):
        """Test listing documents in project with no documents"""
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        response = client.get(f"/api/projects/{project.id}/documents")

        assert response.status_code == 200
        data = response.json()
        assert data["documents"] == []
        assert data["total_count"] == 0

    def test_list_documents_with_sorting(self, client, test_db):
        """Test listing documents with different sort options"""
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

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
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        files = [
            ("files", ("test.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")),
            ("files", ("test.txt", io.BytesIO(b"text"), "text/plain"))
        ]

        client.post(f"/api/projects/{project.id}/documents/upload", files=files)

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
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        files = [
            ("files", ("small.txt", io.BytesIO(b"small"), "text/plain")),
            ("files", ("large.txt", io.BytesIO(b"large content"), "text/plain"))
        ]

        client.post(f"/api/projects/{project.id}/documents/upload", files=files)

        response = client.get(f"/api/projects/{project.id}/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["document_count"] == 2
        assert data["total_document_size"] == 5 + 13
        assert data["last_activity_at"] is not None


class TestProjectDeleteCascade:
    """Test DELETE /api/projects/{id} with cascade to documents"""

    def test_delete_project_removes_documents(self, client, test_db):
        """Test deleting project also deletes all documents"""
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

        response = client.delete(f"/api/projects/{project.id}")
        assert response.status_code == 204

        # Verify document is also gone
        doc_response = client.get(f"/api/documents/{doc_id}")
        assert doc_response.status_code == 404
