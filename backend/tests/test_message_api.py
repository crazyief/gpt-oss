"""
Unit tests for Message API endpoints.

Tests message fetching, reactions, and regeneration.
Uses shared fixtures from conftest.py for database and client setup.
"""

import pytest
from app.models.database import Message


@pytest.fixture
def sample_conversation(client):
    """Create a sample conversation for testing."""
    response = client.post(
        "/api/conversations/create",
        json={"title": "Test Chat"}
    )
    return response.json()["id"]


@pytest.fixture
def sample_messages(test_db, sample_conversation):
    """Create sample messages in the conversation."""
    # Create user message
    user_msg = Message(
        conversation_id=sample_conversation,
        role="user",
        content="What is IEC 62443?",
        token_count=5
    )
    test_db.add(user_msg)
    test_db.commit()
    test_db.refresh(user_msg)

    # Create assistant message
    assistant_msg = Message(
        conversation_id=sample_conversation,
        role="assistant",
        content="IEC 62443 is a cybersecurity standard...",
        parent_message_id=user_msg.id,
        token_count=150,
        model_name="gpt-oss-20b",
        completion_time_ms=3500
    )
    test_db.add(assistant_msg)
    test_db.commit()
    test_db.refresh(assistant_msg)

    return {"user": user_msg, "assistant": assistant_msg}


class TestGetMessages:
    """Tests for GET /api/messages/{conversation_id} endpoint."""

    def test_get_messages_empty(self, client, sample_conversation):
        """Test getting messages from empty conversation."""
        response = client.get(f"/api/messages/{sample_conversation}")
        assert response.status_code == 200
        data = response.json()
        assert data["messages"] == []
        assert data["total_count"] == 0

    def test_get_messages_with_data(self, client, sample_conversation, sample_messages):
        """Test getting messages with data."""
        response = client.get(f"/api/messages/{sample_conversation}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == 2
        assert data["total_count"] == 2

        # Verify chronological order (oldest first)
        assert data["messages"][0]["role"] == "user"
        assert data["messages"][1]["role"] == "assistant"

    def test_get_messages_pagination(self, client, sample_conversation, test_db):
        """Test pagination with limit and offset."""
        # Create 5 messages
        for i in range(5):
            msg = Message(
                conversation_id=sample_conversation,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                token_count=5
            )
            test_db.add(msg)
        test_db.commit()

        # Get first 2
        response = client.get(f"/api/messages/{sample_conversation}?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == 2
        assert data["total_count"] == 5

    def test_get_messages_conversation_not_found(self, client):
        """Test 404 for non-existent conversation."""
        response = client.get("/api/messages/99999")
        assert response.status_code == 404

    def test_get_messages_response_structure(self, client, sample_conversation, sample_messages):
        """Test message response structure includes all fields."""
        response = client.get(f"/api/messages/{sample_conversation}")
        assert response.status_code == 200
        data = response.json()

        user_msg = data["messages"][0]
        assert "id" in user_msg
        assert "conversation_id" in user_msg
        assert "role" in user_msg
        assert "content" in user_msg
        assert "created_at" in user_msg
        assert "reaction" in user_msg
        assert "parent_message_id" in user_msg
        assert "token_count" in user_msg
        assert "model_name" in user_msg
        assert "completion_time_ms" in user_msg
        assert "metadata" in user_msg


class TestMessageReaction:
    """Tests for POST /api/messages/{id}/reaction endpoint."""

    def test_add_reaction_thumbs_up(self, client, sample_messages):
        """Test adding thumbs_up reaction."""
        message_id = sample_messages["assistant"].id

        response = client.post(
            f"/api/messages/{message_id}/reaction",
            json={"reaction": "thumbs_up"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message_id"] == message_id
        assert data["reaction"] == "thumbs_up"

    def test_add_reaction_thumbs_down(self, client, sample_messages):
        """Test adding thumbs_down reaction."""
        message_id = sample_messages["assistant"].id

        response = client.post(
            f"/api/messages/{message_id}/reaction",
            json={"reaction": "thumbs_down"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["reaction"] == "thumbs_down"

    def test_remove_reaction(self, client, sample_messages, test_db):
        """Test removing reaction by setting to null."""
        message_id = sample_messages["assistant"].id

        # First add a reaction
        client.post(
            f"/api/messages/{message_id}/reaction",
            json={"reaction": "thumbs_up"}
        )

        # Then remove it
        response = client.post(
            f"/api/messages/{message_id}/reaction",
            json={"reaction": None}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["reaction"] is None

    def test_update_existing_reaction(self, client, sample_messages):
        """Test updating existing reaction."""
        message_id = sample_messages["assistant"].id

        # Add thumbs_up
        client.post(
            f"/api/messages/{message_id}/reaction",
            json={"reaction": "thumbs_up"}
        )

        # Change to thumbs_down
        response = client.post(
            f"/api/messages/{message_id}/reaction",
            json={"reaction": "thumbs_down"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["reaction"] == "thumbs_down"

    def test_reaction_message_not_found(self, client):
        """Test 404 for non-existent message."""
        response = client.post(
            "/api/messages/99999/reaction",
            json={"reaction": "thumbs_up"}
        )
        assert response.status_code == 404

    def test_reaction_invalid_value(self, client, sample_messages):
        """Test validation error for invalid reaction value."""
        message_id = sample_messages["assistant"].id

        response = client.post(
            f"/api/messages/{message_id}/reaction",
            json={"reaction": "invalid"}
        )
        assert response.status_code == 422  # Validation error


class TestMessageRegenerate:
    """Tests for POST /api/messages/{id}/regenerate endpoint."""

    def test_regenerate_validation_user_message_only(self, client, sample_messages):
        """Test that regenerate only works on user messages."""
        # Try to regenerate assistant message (should fail)
        assistant_id = sample_messages["assistant"].id
        response = client.post(f"/api/messages/{assistant_id}/regenerate")
        assert response.status_code == 400
        assert "user messages" in response.json()["detail"]

    def test_regenerate_message_not_found(self, client):
        """Test 404 for non-existent message."""
        response = client.post("/api/messages/99999/regenerate")
        assert response.status_code == 404

    # Note: Full SSE streaming tests for regenerate are in test_chat_streaming.py
    # These tests focus on validation and error handling
