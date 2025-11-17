"""
Unit tests for Project API endpoints.

Tests CRUD operations, pagination, validation, and error handling.
Uses shared fixtures from conftest.py for database and client setup.
"""

import pytest


class TestProjectCreate:
    """Tests for POST /api/projects/create endpoint."""

    def test_create_project_success(self, client):
        """Test successful project creation."""
        response = client.post(
            "/api/projects/create",
            json={"name": "Test Project", "description": "Test description"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["description"] == "Test description"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert data["metadata"] == {}

    def test_create_project_without_description(self, client):
        """Test creating project without optional description."""
        response = client.post(
            "/api/projects/create",
            json={"name": "Minimal Project"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Project"
        assert data["description"] is None

    def test_create_project_validation_error(self, client):
        """Test validation error for missing required field."""
        response = client.post(
            "/api/projects/create",
            json={"description": "Missing name"}
        )
        assert response.status_code == 422  # Pydantic validation error

    def test_create_project_name_too_long(self, client):
        """Test validation error for name exceeding max length."""
        response = client.post(
            "/api/projects/create",
            json={"name": "x" * 101}  # Max is 100
        )
        assert response.status_code == 422


class TestProjectList:
    """Tests for GET /api/projects/list endpoint."""

    def test_list_projects_empty(self, client):
        """Test listing projects when none exist."""
        response = client.get("/api/projects/list")
        assert response.status_code == 200
        data = response.json()
        assert data["projects"] == []
        assert data["total_count"] == 0

    def test_list_projects_with_data(self, client):
        """Test listing projects with data."""
        # Create test projects
        client.post("/api/projects/create", json={"name": "Project 1"})
        client.post("/api/projects/create", json={"name": "Project 2"})

        response = client.get("/api/projects/list")
        assert response.status_code == 200
        data = response.json()
        assert len(data["projects"]) == 2
        assert data["total_count"] == 2

    def test_list_projects_pagination(self, client):
        """Test pagination with limit and offset."""
        # Create 5 projects
        for i in range(5):
            client.post("/api/projects/create", json={"name": f"Project {i}"})

        # Get first 2
        response = client.get("/api/projects/list?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["projects"]) == 2
        assert data["total_count"] == 5

        # Get next 2
        response = client.get("/api/projects/list?limit=2&offset=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["projects"]) == 2
        assert data["total_count"] == 5

    def test_list_projects_max_limit(self, client):
        """Test that limit is capped at 100."""
        response = client.get("/api/projects/list?limit=200")
        assert response.status_code == 200  # Should work but cap at 100


class TestProjectGet:
    """Tests for GET /api/projects/{id} endpoint."""

    def test_get_project_success(self, client):
        """Test getting a project by ID."""
        # Create project
        create_response = client.post(
            "/api/projects/create",
            json={"name": "Test Project"}
        )
        project_id = create_response.json()["id"]

        # Get project
        response = client.get(f"/api/projects/{project_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
        assert data["name"] == "Test Project"

    def test_get_project_not_found(self, client):
        """Test 404 for non-existent project."""
        response = client.get("/api/projects/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Project not found"


class TestProjectUpdate:
    """Tests for PATCH /api/projects/{id} endpoint."""

    def test_update_project_name(self, client):
        """Test updating project name."""
        # Create project
        create_response = client.post(
            "/api/projects/create",
            json={"name": "Original Name"}
        )
        project_id = create_response.json()["id"]

        # Update name
        response = client.patch(
            f"/api/projects/{project_id}",
            json={"name": "Updated Name"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    def test_update_project_not_found(self, client):
        """Test 404 for updating non-existent project."""
        response = client.patch(
            "/api/projects/99999",
            json={"name": "New Name"}
        )
        assert response.status_code == 404


class TestProjectDelete:
    """Tests for DELETE /api/projects/{id} endpoint."""

    def test_delete_project_success(self, client):
        """Test soft-deleting a project."""
        # Create project
        create_response = client.post(
            "/api/projects/create",
            json={"name": "To Delete"}
        )
        project_id = create_response.json()["id"]

        # Delete project
        response = client.delete(f"/api/projects/{project_id}")
        assert response.status_code == 204

        # Verify it's gone (soft-deleted)
        response = client.get(f"/api/projects/{project_id}")
        assert response.status_code == 404

    def test_delete_project_not_found(self, client):
        """Test 404 for deleting non-existent project."""
        response = client.delete("/api/projects/99999")
        assert response.status_code == 404
