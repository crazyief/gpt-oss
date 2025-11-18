"""
Integration tests for chat streaming endpoints.

Tests SSE streaming, cancellation, and error handling with mocked LLM.
Uses shared fixtures from conftest.py for database and client setup.
"""

import pytest
from unittest.mock import patch


@pytest.fixture
def sample_conversation(client):
    """Create a sample conversation for testing."""
    response = client.post(
        "/api/conversations/create",
        json={"title": "Test Chat"}
    )
    return response.json()["id"]


class TestChatStreamValidation:
    """Tests for /api/chat/stream endpoint validation."""

    def test_stream_conversation_not_found(self, client):
        """Test 404 when conversation doesn't exist."""
        response = client.post(
            "/api/chat/stream",
            json={"conversation_id": 99999, "message": "Test message"}
        )
        assert response.status_code == 404

    def test_stream_validation_empty_message(self, client, sample_conversation):
        """Test validation error for empty message."""
        response = client.post(
            "/api/chat/stream",
            json={"conversation_id": sample_conversation, "message": ""}
        )
        assert response.status_code == 422  # Validation error

    def test_stream_validation_message_too_long(self, client, sample_conversation):
        """Test validation error for message exceeding max length."""
        response = client.post(
            "/api/chat/stream",
            json={
                "conversation_id": sample_conversation,
                "message": "x" * 10001  # Max is 10000
            }
        )
        assert response.status_code == 422


class TestChatStreamMocked:
    """Tests for chat streaming with mocked LLM service."""

    @patch('app.api.chat.llm_service.generate_stream')
    async def test_stream_basic_flow(self, mock_generate, client, sample_conversation):
        """Test basic streaming flow with mocked LLM."""
        # Mock LLM to return simple tokens
        async def mock_stream(*args, **kwargs):
            yield "Test"
            yield " response"

        mock_generate.return_value = mock_stream()

        # Note: Testing SSE streams with TestClient is complex
        # This test verifies the endpoint is reachable
        # Full SSE testing would require async client
        response = client.post(
            "/api/chat/stream",
            json={
                "conversation_id": sample_conversation,
                "message": "Test message"
            },
            stream=True
        )

        # Verify SSE headers
        # WHY 200: SSE streams start with 200 OK
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")


class TestCancelStream:
    """Tests for POST /api/chat/cancel/{session_id} endpoint."""

    def test_cancel_invalid_session(self, client):
        """Test cancelling non-existent session."""
        response = client.post("/api/chat/cancel/invalid-uuid")
        assert response.status_code == 404

    # Note: Testing actual cancellation requires running a real stream
    # and capturing the session ID, which is complex in sync tests.
    # In production, this would be tested with async integration tests.


class TestStreamErrorHandling:
    """Tests for error handling in streaming."""

    @patch('app.api.chat.llm_service.generate_stream')
    async def test_stream_llm_error(self, mock_generate, client, sample_conversation):
        """Test error handling when LLM service fails."""
        # Mock LLM to raise exception
        async def mock_stream_error(*args, **kwargs):
            raise Exception("LLM service unavailable")

        mock_generate.return_value = mock_stream_error()

        response = client.post(
            "/api/chat/stream",
            json={
                "conversation_id": sample_conversation,
                "message": "Test message"
            },
            stream=True
        )

        # Stream should start successfully (200)
        # Error will be sent as SSE error event
        assert response.status_code == 200


# Note: Comprehensive SSE streaming tests require async test client
# These tests cover validation and basic flow
# For production, use pytest-asyncio with httpx.AsyncClient
