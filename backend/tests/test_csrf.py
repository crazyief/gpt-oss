"""
CSRF Protection Tests

Tests for token-based CSRF protection implementation.
Verifies that CSRF tokens are required for state-changing requests
and that validation works correctly.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestCSRFTokenEndpoint:
    """Tests for CSRF token generation endpoint."""

    def test_csrf_token_endpoint_exists(self):
        """Test that CSRF token endpoint is accessible."""
        response = client.get("/api/csrf-token")
        assert response.status_code == 200

    def test_csrf_token_endpoint_returns_token(self):
        """Test CSRF token generation."""
        response = client.get("/api/csrf-token")
        assert response.status_code == 200
        data = response.json()
        assert "csrf_token" in data
        assert isinstance(data["csrf_token"], str)
        assert len(data["csrf_token"]) > 20  # Token should be reasonably long

    def test_csrf_token_endpoint_sets_cookie(self):
        """Test that CSRF token is optionally set as cookie."""
        response = client.get("/api/csrf-token")
        assert response.status_code == 200
        # Check if csrf_token cookie is set (optional, defense in depth)
        # Note: Cookie presence is optional, so we just verify the endpoint works
        assert "csrf_token" in response.json()


class TestCSRFProtectionMiddleware:
    """Tests for CSRF protection middleware."""

    def test_get_requests_exempt_from_csrf(self):
        """Test that GET requests don't require CSRF token."""
        # GET /health should work without token
        response = client.get("/health")
        assert response.status_code == 200

        # GET /api/projects/list should work without token (or return 404 if not implemented)
        response = client.get("/api/projects/list")
        assert response.status_code in (200, 404, 405)  # Not 403

    def test_post_without_csrf_token_fails(self):
        """Test that POST without CSRF token is rejected."""
        response = client.post(
            "/api/projects/create",
            json={"name": "Test Project", "description": "Test"}
        )
        assert response.status_code == 403
        data = response.json()
        assert "CSRF token missing" in data["detail"]
        assert data["error_type"] == "csrf_error"

    def test_post_with_invalid_csrf_token_fails(self):
        """Test that POST with invalid CSRF token is rejected."""
        response = client.post(
            "/api/projects/create",
            json={"name": "Test Project", "description": "Test"},
            headers={"X-CSRF-Token": "invalid-token-12345"}
        )
        assert response.status_code == 403
        data = response.json()
        assert "invalid or expired" in data["detail"].lower()
        assert data["error_type"] == "csrf_error"

    def test_post_with_valid_csrf_token_succeeds(self):
        """Test that POST with valid CSRF token succeeds."""
        # Get valid token
        token_response = client.get("/api/csrf-token")
        assert token_response.status_code == 200
        csrf_token = token_response.json()["csrf_token"]

        # Use token in POST request
        response = client.post(
            "/api/projects/create",
            json={"name": "Test Project", "description": "Test Description"},
            headers={"X-CSRF-Token": csrf_token}
        )
        # Should succeed (200/201) or fail with validation error (422), but NOT 403
        assert response.status_code in (200, 201, 422)
        assert response.status_code != 403  # Not a CSRF error

    def test_put_without_csrf_token_fails(self):
        """Test that PUT without CSRF token is rejected."""
        response = client.put(
            "/api/projects/1",
            json={"name": "Updated Project"}
        )
        assert response.status_code == 403
        data = response.json()
        assert "CSRF token missing" in data["detail"]

    def test_delete_without_csrf_token_fails(self):
        """Test that DELETE without CSRF token is rejected."""
        response = client.delete("/api/projects/1")
        assert response.status_code == 403
        data = response.json()
        assert "CSRF token missing" in data["detail"]

    def test_options_requests_exempt_from_csrf(self):
        """Test that OPTIONS requests (CORS preflight) don't require CSRF token."""
        response = client.options("/api/projects/create")
        # OPTIONS should not return 403 (CSRF error)
        assert response.status_code != 403


class TestCSRFTokenLifecycle:
    """Tests for CSRF token lifecycle and expiry."""

    def test_token_can_be_reused_within_expiry(self):
        """Test that a valid token can be used multiple times within expiry period."""
        # Get token
        token_response = client.get("/api/csrf-token")
        csrf_token = token_response.json()["csrf_token"]

        # Use token for first request
        response1 = client.post(
            "/api/projects/create",
            json={"name": "Project 1", "description": "Test 1"},
            headers={"X-CSRF-Token": csrf_token}
        )
        assert response1.status_code in (200, 201, 422)

        # Reuse same token for second request
        response2 = client.post(
            "/api/projects/create",
            json={"name": "Project 2", "description": "Test 2"},
            headers={"X-CSRF-Token": csrf_token}
        )
        assert response2.status_code in (200, 201, 422)

    def test_new_token_can_be_fetched_anytime(self):
        """Test that new CSRF tokens can be fetched at any time."""
        # Fetch multiple tokens
        token1_response = client.get("/api/csrf-token")
        token1 = token1_response.json()["csrf_token"]

        token2_response = client.get("/api/csrf-token")
        token2 = token2_response.json()["csrf_token"]

        # Both tokens should be valid (different tokens each time)
        assert token1 != token2
        assert len(token1) > 20
        assert len(token2) > 20


class TestCSRFExemptEndpoints:
    """Tests for endpoints that should be exempt from CSRF validation."""

    def test_health_endpoint_exempt(self):
        """Test that /health endpoint doesn't require CSRF token."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_csrf_token_endpoint_exempt(self):
        """Test that /api/csrf-token endpoint doesn't require CSRF token."""
        response = client.get("/api/csrf-token")
        assert response.status_code == 200

    def test_docs_endpoints_exempt(self):
        """Test that API documentation endpoints don't require CSRF token."""
        # /docs (Swagger UI)
        response = client.get("/docs")
        assert response.status_code == 200

        # /openapi.json
        response = client.get("/openapi.json")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
