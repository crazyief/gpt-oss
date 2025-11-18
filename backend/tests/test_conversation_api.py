"""
Unit tests for Conversation API endpoints.

Tests CRUD operations, search, pagination, and filtering.
Uses shared fixtures from conftest.py for database and client setup.
"""

import pytest


@pytest.fixture
def sample_project(client):
    """Create a sample project for testing."""
    response = client.post(
        "/api/projects/create",
        json={"name": "Test Project"}
    )
    return response.json()["id"]


class TestConversationCreate:
    """Tests for POST /api/conversations/create endpoint."""

    def test_create_conversation_with_project(self, client, sample_project):
        """Test creating conversation with project association."""
        response = client.post(
            "/api/conversations/create",
            json={"project_id": sample_project, "title": "Test Chat"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["project_id"] == sample_project
        assert data["title"] == "Test Chat"
        assert data["message_count"] == 0
        assert data["last_message_at"] is None

    def test_create_conversation_without_project(self, client):
        """Test creating conversation without project (project_id = null)."""
        response = client.post(
            "/api/conversations/create",
            json={"title": "Standalone Chat"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["project_id"] is None
        assert data["title"] == "Standalone Chat"

    def test_create_conversation_auto_title(self, client):
        """Test auto-generated title when not provided."""
        response = client.post(
            "/api/conversations/create",
            json={}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Chat"  # Auto-generated


class TestConversationList:
    """Tests for GET /api/conversations/list endpoint."""

    def test_list_conversations_empty(self, client):
        """Test listing conversations when none exist."""
        response = client.get("/api/conversations/list")
        assert response.status_code == 200
        data = response.json()
        assert data["conversations"] == []
        assert data["total_count"] == 0

    def test_list_conversations_with_data(self, client, sample_project):
        """Test listing conversations."""
        # Create conversations
        client.post("/api/conversations/create", json={"title": "Chat 1"})
        client.post("/api/conversations/create", json={"title": "Chat 2"})

        response = client.get("/api/conversations/list")
        assert response.status_code == 200
        data = response.json()
        assert len(data["conversations"]) == 2
        assert data["total_count"] == 2

    def test_list_conversations_filter_by_project(self, client, sample_project):
        """Test filtering conversations by project_id."""
        # Create conversations in different projects
        client.post(
            "/api/conversations/create",
            json={"project_id": sample_project, "title": "In Project"}
        )
        client.post(
            "/api/conversations/create",
            json={"title": "Not In Project"}
        )

        # Filter by project
        response = client.get(f"/api/conversations/list?project_id={sample_project}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["conversations"]) == 1
        assert data["conversations"][0]["title"] == "In Project"

    def test_list_conversations_pagination(self, client):
        """Test pagination with limit and offset."""
        # Create 5 conversations
        for i in range(5):
            client.post("/api/conversations/create", json={"title": f"Chat {i}"})

        # Get first 2
        response = client.get("/api/conversations/list?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["conversations"]) == 2
        assert data["total_count"] == 5


class TestConversationGet:
    """Tests for GET /api/conversations/{id} endpoint."""

    def test_get_conversation_success(self, client):
        """Test getting a conversation by ID."""
        # Create conversation
        create_response = client.post(
            "/api/conversations/create",
            json={"title": "Test Chat"}
        )
        conversation_id = create_response.json()["id"]

        # Get conversation
        response = client.get(f"/api/conversations/{conversation_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == conversation_id
        assert data["title"] == "Test Chat"

    def test_get_conversation_not_found(self, client):
        """Test 404 for non-existent conversation."""
        response = client.get("/api/conversations/99999")
        assert response.status_code == 404


class TestConversationUpdate:
    """Tests for PATCH /api/conversations/{id} endpoint."""

    def test_update_conversation_title(self, client):
        """Test updating conversation title."""
        # Create conversation
        create_response = client.post(
            "/api/conversations/create",
            json={"title": "Original Title"}
        )
        conversation_id = create_response.json()["id"]

        # Update title
        response = client.patch(
            f"/api/conversations/{conversation_id}",
            json={"title": "Updated Title"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    def test_update_conversation_not_found(self, client):
        """Test 404 for updating non-existent conversation."""
        response = client.patch(
            "/api/conversations/99999",
            json={"title": "New Title"}
        )
        assert response.status_code == 404


class TestConversationDelete:
    """Tests for DELETE /api/conversations/{id} endpoint."""

    def test_delete_conversation_success(self, client):
        """Test soft-deleting a conversation."""
        # Create conversation
        create_response = client.post(
            "/api/conversations/create",
            json={"title": "To Delete"}
        )
        conversation_id = create_response.json()["id"]

        # Delete conversation
        response = client.delete(f"/api/conversations/{conversation_id}")
        assert response.status_code == 204

        # Verify it's gone
        response = client.get(f"/api/conversations/{conversation_id}")
        assert response.status_code == 404

    def test_delete_conversation_not_found(self, client):
        """Test 404 for deleting non-existent conversation."""
        response = client.delete("/api/conversations/99999")
        assert response.status_code == 404


class TestConversationSearch:
    """Tests for GET /api/conversations/search endpoint."""

    def test_search_conversations_found(self, client):
        """Test searching conversations by keyword."""
        # Create conversations
        client.post("/api/conversations/create", json={"title": "IEC 62443 Questions"})
        client.post("/api/conversations/create", json={"title": "ETSI EN 303 645"})
        client.post("/api/conversations/create", json={"title": "Random Chat"})

        # Search for "IEC"
        response = client.get("/api/conversations/search?q=IEC")
        assert response.status_code == 200
        data = response.json()
        assert len(data["conversations"]) == 1
        assert "IEC" in data["conversations"][0]["title"]

    def test_search_conversations_case_insensitive(self, client):
        """Test case-insensitive search."""
        client.post("/api/conversations/create", json={"title": "Test Chat"})

        # Search with lowercase
        response = client.get("/api/conversations/search?q=test")
        assert response.status_code == 200
        assert len(response.json()["conversations"]) == 1

    def test_search_conversations_no_results(self, client):
        """Test search with no matching results."""
        client.post("/api/conversations/create", json={"title": "Test Chat"})

        response = client.get("/api/conversations/search?q=nonexistent")
        assert response.status_code == 200
        data = response.json()
        assert data["conversations"] == []
        assert data["total_count"] == 0

    def test_search_conversations_validation_error(self, client):
        """Test validation error for empty search query."""
        response = client.get("/api/conversations/search?q=")
        assert response.status_code == 422  # Validation error
