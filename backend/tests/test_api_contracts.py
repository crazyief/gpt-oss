"""
API Contract Tests - Comprehensive endpoint validation.

Verifies that all API endpoints follow the contract specifications:
- Request/response schemas
- HTTP status codes
- Error response formats
- Header validation
- Authentication (when applicable)

These tests ensure frontend-backend compatibility.
"""

import io
import pytest
from app.services.project_service import ProjectService
from app.schemas.project import ProjectCreate


class TestProjectEndpointContracts:
    """Contract tests for /api/projects endpoints."""

    def test_create_project_response_schema(self, client):
        """Verify POST /api/projects/create response matches schema."""
        response = client.post(
            "/api/projects/create",
            json={"name": "Contract Test", "description": "Test desc"}
        )

        assert response.status_code == 201
        assert response.headers["content-type"] == "application/json"

        data = response.json()
        # Required fields
        assert "id" in data
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert "metadata" in data

        # Type validation
        assert isinstance(data["id"], int)
        assert isinstance(data["name"], str)
        assert isinstance(data["description"], (str, type(None)))
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)
        assert isinstance(data["metadata"], dict)

        # Value validation
        assert data["name"] == "Contract Test"
        assert data["description"] == "Test desc"

    def test_list_projects_response_schema(self, client):
        """Verify GET /api/projects/list response matches schema."""
        response = client.get("/api/projects/list")

        assert response.status_code == 200
        data = response.json()

        # Required root fields
        assert "projects" in data
        assert "total_count" in data

        # Type validation
        assert isinstance(data["projects"], list)
        assert isinstance(data["total_count"], int)

    def test_get_project_response_schema(self, client):
        """Verify GET /api/projects/{id} response matches schema."""
        create_response = client.post(
            "/api/projects/create",
            json={"name": "Test"}
        )
        project_id = create_response.json()["id"]

        response = client.get(f"/api/projects/{project_id}")

        assert response.status_code == 200
        data = response.json()

        # All required fields present
        assert "id" in data
        assert "name" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert "metadata" in data

    def test_get_project_stats_response_schema(self, client):
        """Verify GET /api/projects/{id}/stats response matches schema."""
        create_response = client.post(
            "/api/projects/create",
            json={"name": "Test"}
        )
        project_id = create_response.json()["id"]

        response = client.get(f"/api/projects/{project_id}/stats")

        assert response.status_code == 200
        data = response.json()

        # Required stats fields
        assert "document_count" in data
        assert "conversation_count" in data
        assert "message_count" in data
        assert "total_document_size" in data
        assert "last_activity_at" in data

        # Type validation
        assert isinstance(data["document_count"], int)
        assert isinstance(data["conversation_count"], int)
        assert isinstance(data["message_count"], int)
        assert isinstance(data["total_document_size"], int)
        assert isinstance(data["last_activity_at"], (str, type(None)))

    def test_get_project_conversations_response_schema(self, client):
        """Verify GET /api/projects/{id}/conversations response matches schema."""
        create_response = client.post(
            "/api/projects/create",
            json={"name": "Test"}
        )
        project_id = create_response.json()["id"]

        response = client.get(f"/api/projects/{project_id}/conversations")

        assert response.status_code == 200
        data = response.json()

        # Required fields
        assert "conversations" in data
        assert "total_count" in data

        # Type validation
        assert isinstance(data["conversations"], list)
        assert isinstance(data["total_count"], int)

    def test_update_project_response_schema(self, client):
        """Verify PATCH /api/projects/{id} response matches schema."""
        create_response = client.post(
            "/api/projects/create",
            json={"name": "Original"}
        )
        project_id = create_response.json()["id"]

        response = client.patch(
            f"/api/projects/{project_id}",
            json={"name": "Updated"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert "name" in data
        assert data["name"] == "Updated"

    def test_delete_project_response(self, client):
        """Verify DELETE /api/projects/{id} response."""
        create_response = client.post(
            "/api/projects/create",
            json={"name": "To Delete"}
        )
        project_id = create_response.json()["id"]

        response = client.delete(f"/api/projects/{project_id}")

        assert response.status_code == 204
        assert response.content == b""


class TestConversationEndpointContracts:
    """Contract tests for /api/conversations endpoints."""

    def test_create_conversation_response_schema(self, client):
        """Verify POST /api/conversations/create response matches schema."""
        response = client.post(
            "/api/conversations/create",
            json={"title": "Contract Test"}
        )

        assert response.status_code == 201
        data = response.json()

        # Required fields
        assert "id" in data
        assert "project_id" in data
        assert "title" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert "last_message_at" in data
        assert "message_count" in data
        assert "metadata" in data

        # Type validation
        assert isinstance(data["id"], int)
        assert isinstance(data["project_id"], (int, type(None)))
        assert isinstance(data["title"], str)
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)
        assert isinstance(data["last_message_at"], (str, type(None)))
        assert isinstance(data["message_count"], int)
        assert isinstance(data["metadata"], dict)

    def test_list_conversations_response_schema(self, client):
        """Verify GET /api/conversations/list response matches schema."""
        response = client.get("/api/conversations/list")

        assert response.status_code == 200
        data = response.json()

        assert "conversations" in data
        assert "total_count" in data
        assert isinstance(data["conversations"], list)
        assert isinstance(data["total_count"], int)

    def test_search_conversations_response_schema(self, client):
        """Verify GET /api/conversations/search response matches schema."""
        response = client.get("/api/conversations/search?q=test")

        assert response.status_code == 200
        data = response.json()

        assert "conversations" in data
        assert "total_count" in data
        assert isinstance(data["conversations"], list)
        assert isinstance(data["total_count"], int)

    def test_get_conversation_response_schema(self, client):
        """Verify GET /api/conversations/{id} response matches schema."""
        create_response = client.post(
            "/api/conversations/create",
            json={"title": "Test"}
        )
        conversation_id = create_response.json()["id"]

        response = client.get(f"/api/conversations/{conversation_id}")

        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert "title" in data
        assert "created_at" in data
        assert "updated_at" in data


class TestMessageEndpointContracts:
    """Contract tests for /api/messages endpoints."""

    def test_get_messages_response_schema(self, client):
        """Verify GET /api/messages/{conversation_id} response matches schema."""
        conv_response = client.post(
            "/api/conversations/create",
            json={"title": "Test"}
        )
        conversation_id = conv_response.json()["id"]

        response = client.get(f"/api/messages/{conversation_id}")

        assert response.status_code == 200
        data = response.json()

        # Required root fields
        assert "messages" in data
        assert "total_count" in data

        # Type validation
        assert isinstance(data["messages"], list)
        assert isinstance(data["total_count"], int)

    def test_update_reaction_response_schema(self, client, test_db):
        """Verify POST /api/messages/{id}/reaction response matches schema."""
        from app.models.database import Message

        conv_response = client.post(
            "/api/conversations/create",
            json={"title": "Test"}
        )
        conversation_id = conv_response.json()["id"]

        # Create a message
        msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content="Test response",
            token_count=10
        )
        test_db.add(msg)
        test_db.commit()
        test_db.refresh(msg)

        response = client.post(
            f"/api/messages/{msg.id}/reaction",
            json={"reaction": "thumbs_up"}
        )

        assert response.status_code == 200
        data = response.json()

        # Required fields
        assert "message_id" in data
        assert "reaction" in data

        # Type validation
        assert isinstance(data["message_id"], int)
        assert isinstance(data["reaction"], (str, type(None)))
        assert data["reaction"] in ["thumbs_up", "thumbs_down", None]


class TestChatEndpointContracts:
    """Contract tests for /api/chat endpoints."""

    def test_initiate_stream_response_schema(self, client):
        """Verify POST /api/chat/stream response matches schema."""
        conv_response = client.post(
            "/api/conversations/create",
            json={"title": "Test"}
        )
        conversation_id = conv_response.json()["id"]

        response = client.post(
            "/api/chat/stream",
            json={
                "conversation_id": conversation_id,
                "message": "Test message"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Required fields
        assert "session_id" in data
        assert "message_id" in data

        # Type validation
        assert isinstance(data["session_id"], str)
        assert isinstance(data["message_id"], int)

    def test_stream_sse_headers(self, client):
        """Verify GET /api/chat/stream/{session_id} returns correct SSE headers."""
        conv_response = client.post(
            "/api/conversations/create",
            json={"title": "Test"}
        )
        conversation_id = conv_response.json()["id"]

        # Initiate stream
        init_response = client.post(
            "/api/chat/stream",
            json={
                "conversation_id": conversation_id,
                "message": "Test"
            }
        )
        session_id = init_response.json()["session_id"]

        # Connect to stream
        response = client.get(
            f"/api/chat/stream/{session_id}",
            stream=True
        )

        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")
        assert response.headers.get("cache-control") == "no-cache"


class TestDocumentEndpointContracts:
    """Contract tests for /api/documents endpoints."""

    def test_upload_response_schema(self, client, test_db):
        """Verify POST /api/projects/{id}/documents/upload response matches schema."""
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        files = {
            "files": ("test.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")
        }

        response = client.post(
            f"/api/projects/{project.id}/documents/upload",
            files=files
        )

        assert response.status_code == 201
        data = response.json()

        # Required root fields
        assert "documents" in data
        assert "failed" in data

        # Type validation
        assert isinstance(data["documents"], list)
        assert isinstance(data["failed"], list)

        # Document schema
        if len(data["documents"]) > 0:
            doc = data["documents"][0]
            assert "id" in doc
            assert "project_id" in doc
            assert "filename" in doc
            assert "original_filename" in doc
            assert "file_size" in doc
            assert "mime_type" in doc
            assert "uploaded_at" in doc

            assert isinstance(doc["id"], int)
            assert isinstance(doc["project_id"], int)
            assert isinstance(doc["filename"], str)
            assert isinstance(doc["original_filename"], str)
            assert isinstance(doc["file_size"], int)
            assert isinstance(doc["mime_type"], str)
            assert isinstance(doc["uploaded_at"], str)

    def test_list_documents_response_schema(self, client, test_db):
        """Verify GET /api/projects/{id}/documents response matches schema."""
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        response = client.get(f"/api/projects/{project.id}/documents")

        assert response.status_code == 200
        data = response.json()

        assert "documents" in data
        assert "total_count" in data
        assert isinstance(data["documents"], list)
        assert isinstance(data["total_count"], int)

    def test_get_document_response_schema(self, client, test_db):
        """Verify GET /api/documents/{id} response matches schema."""
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

        assert "id" in data
        assert "project_id" in data
        assert "filename" in data
        assert "original_filename" in data
        assert "file_size" in data
        assert "mime_type" in data
        assert "uploaded_at" in data

    def test_download_document_headers(self, client, test_db):
        """Verify GET /api/documents/{id}/download headers."""
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        files = {
            "files": ("report.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")
        }

        upload_response = client.post(
            f"/api/projects/{project.id}/documents/upload",
            files=files
        )
        doc_id = upload_response.json()["documents"][0]["id"]

        response = client.get(f"/api/documents/{doc_id}/download")

        assert response.status_code == 200
        assert "application/pdf" in response.headers["content-type"]
        assert "attachment" in response.headers["content-disposition"]
        assert "report.pdf" in response.headers["content-disposition"]

    def test_delete_document_response(self, client, test_db):
        """Verify DELETE /api/documents/{id} response."""
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
        assert response.content == b""


class TestErrorResponseContracts:
    """Contract tests for error responses."""

    def test_404_error_format(self, client):
        """Verify 404 errors return consistent format."""
        response = client.get("/api/projects/99999")

        assert response.status_code == 404
        data = response.json()

        assert "detail" in data
        assert isinstance(data["detail"], str)

    def test_422_validation_error_format(self, client):
        """Verify 422 validation errors return consistent format."""
        response = client.post(
            "/api/projects/create",
            json={"description": "Missing name"}
        )

        assert response.status_code == 422
        data = response.json()

        assert "detail" in data
        # Pydantic validation errors return list of error objects
        assert isinstance(data["detail"], list)

    def test_400_bad_request_format(self, client, test_db):
        """Verify 400 errors return consistent format."""
        response = client.post(
            "/api/projects/99999/documents/upload",
            files={"files": ("test.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")}
        )

        assert response.status_code == 400
        data = response.json()

        assert "detail" in data
        assert isinstance(data["detail"], str)

    def test_500_server_error_format(self, client):
        """Verify 500 errors return consistent format (if triggered)."""
        # NOTE: Hard to trigger 500 without breaking the app
        # This test documents expected format
        # In production, all 500s should have:
        # {"detail": "Error message"}
        pass


class TestPaginationContracts:
    """Contract tests for pagination parameters."""

    def test_project_list_pagination_defaults(self, client):
        """Verify pagination defaults for project list."""
        response = client.get("/api/projects/list")

        assert response.status_code == 200
        # Default limit is 50, offset is 0
        # These are applied server-side

    def test_conversation_list_pagination_validation(self, client):
        """Verify pagination validation for conversation list."""
        # Negative offset rejected
        response = client.get("/api/conversations/list?offset=-1")
        assert response.status_code == 422

        # Zero limit rejected
        response = client.get("/api/conversations/list?limit=0")
        assert response.status_code == 422

    def test_message_list_pagination_max_limit(self, client):
        """Verify max limit for message list."""
        conv_response = client.post(
            "/api/conversations/create",
            json={"title": "Test"}
        )
        conversation_id = conv_response.json()["id"]

        # Limit > 100 rejected
        response = client.get(f"/api/messages/{conversation_id}?limit=200")
        assert response.status_code == 422


class TestSortingFilteringContracts:
    """Contract tests for sorting and filtering parameters."""

    def test_document_sort_by_validation(self, client, test_db):
        """Verify sort_by parameter validation for documents."""
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        # Valid sort_by values
        for sort_by in ["name", "date", "size", "type"]:
            response = client.get(
                f"/api/projects/{project.id}/documents?sort_by={sort_by}"
            )
            assert response.status_code == 200

        # Invalid sort_by value
        response = client.get(
            f"/api/projects/{project.id}/documents?sort_by=invalid"
        )
        assert response.status_code == 422

    def test_document_sort_order_validation(self, client, test_db):
        """Verify sort_order parameter validation for documents."""
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        # Valid sort_order values
        for sort_order in ["asc", "desc"]:
            response = client.get(
                f"/api/projects/{project.id}/documents?sort_order={sort_order}"
            )
            assert response.status_code == 200

        # Invalid sort_order value
        response = client.get(
            f"/api/projects/{project.id}/documents?sort_order=invalid"
        )
        assert response.status_code == 422

    def test_document_filter_type_validation(self, client, test_db):
        """Verify filter_type parameter accepts valid extensions."""
        project_data = ProjectCreate(name="Test Project")
        project = ProjectService.create_project(test_db, project_data)

        # Valid filter types
        for filter_type in ["pdf", "docx", "xlsx", "txt", "md"]:
            response = client.get(
                f"/api/projects/{project.id}/documents?filter_type={filter_type}"
            )
            assert response.status_code == 200
