"""
Unit tests for Stage 3 Project Features.

Tests new functionality:
- Project color and icon customization
- Default project protection
- Project reordering (drag-and-drop)
- Move conversation between projects
- Project details endpoint
- Enhanced project listing with document counts
"""

import pytest


class TestProjectCustomization:
    """Tests for project color and icon fields."""

    def test_create_project_with_color_and_icon(self, client):
        """Test creating project with custom color and icon."""
        response = client.post(
            "/api/projects/create",
            json={
                "name": "Security Audit",
                "description": "IEC 62443 compliance",
                "color": "blue",
                "icon": "shield"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Security Audit"
        assert data["color"] == "blue"
        assert data["icon"] == "shield"
        assert data["is_default"] is False
        assert data["sort_order"] == 0

    def test_create_project_default_color_and_icon(self, client):
        """Test creating project uses default color and icon."""
        response = client.post(
            "/api/projects/create",
            json={"name": "Test Project"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["color"] == "blue"
        assert data["icon"] == "folder"

    def test_create_project_invalid_color(self, client):
        """Test validation error for invalid color."""
        response = client.post(
            "/api/projects/create",
            json={
                "name": "Test Project",
                "color": "invalid_color"
            }
        )
        assert response.status_code == 422

    def test_create_project_invalid_icon(self, client):
        """Test validation error for invalid icon."""
        response = client.post(
            "/api/projects/create",
            json={
                "name": "Test Project",
                "icon": "invalid_icon"
            }
        )
        assert response.status_code == 422

    def test_update_project_color_and_icon(self, client):
        """Test updating project color and icon."""
        # Create project
        create_response = client.post(
            "/api/projects/create",
            json={"name": "Test Project"}
        )
        project_id = create_response.json()["id"]

        # Update color and icon
        update_response = client.patch(
            f"/api/projects/{project_id}",
            json={"color": "red", "icon": "star"}
        )
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["color"] == "red"
        assert data["icon"] == "star"


class TestDefaultProject:
    """Tests for default project creation and protection."""

    def test_default_project_auto_created(self, client):
        """Test default project is auto-created on first request."""
        response = client.get("/api/projects/default")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Default"
        assert data["is_default"] is True
        assert data["color"] == "gray"
        assert data["icon"] == "folder"

    def test_cannot_delete_default_project(self, client):
        """Test deletion of default project is prevented."""
        # Get default project
        default_response = client.get("/api/projects/default")
        default_id = default_response.json()["id"]

        # Attempt to delete
        delete_response = client.delete(
            f"/api/projects/{default_id}?action=delete"
        )
        assert delete_response.status_code == 400
        assert "cannot delete" in delete_response.json()["detail"].lower()

    def test_only_one_default_project(self, client):
        """Test only one project can be marked as default."""
        # Get default project
        response1 = client.get("/api/projects/default")
        default_id_1 = response1.json()["id"]

        # Call again - should return same project
        response2 = client.get("/api/projects/default")
        default_id_2 = response2.json()["id"]

        assert default_id_1 == default_id_2


class TestProjectReordering:
    """Tests for project reordering (drag-and-drop)."""

    def test_reorder_projects_success(self, client):
        """Test successful project reordering."""
        # Create 3 projects
        p1 = client.post("/api/projects/create", json={"name": "Project 1"}).json()
        p2 = client.post("/api/projects/create", json={"name": "Project 2"}).json()
        p3 = client.post("/api/projects/create", json={"name": "Project 3"}).json()

        # Reorder: 3, 1, 2
        response = client.patch(
            "/api/projects/reorder",
            json={"project_ids": [p3["id"], p1["id"], p2["id"]]}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Projects reordered successfully"

        # Verify sort_order
        projects = data["projects"]
        assert projects[0]["id"] == p3["id"]
        assert projects[0]["sort_order"] == 0
        assert projects[1]["id"] == p1["id"]
        assert projects[1]["sort_order"] == 1
        assert projects[2]["id"] == p2["id"]
        assert projects[2]["sort_order"] == 2

    def test_reorder_projects_empty_array(self, client):
        """Test error for empty project_ids array."""
        response = client.patch(
            "/api/projects/reorder",
            json={"project_ids": []}
        )
        assert response.status_code == 422

    def test_reorder_projects_invalid_ids(self, client):
        """Test error for invalid project IDs."""
        response = client.patch(
            "/api/projects/reorder",
            json={"project_ids": [999, 998, 997]}
        )
        assert response.status_code == 400


class TestMoveConversation:
    """Tests for moving conversations between projects."""

    def test_move_conversation_success(self, client):
        """Test successfully moving conversation to different project."""
        # Create 2 projects
        p1 = client.post("/api/projects/create", json={"name": "Project 1"}).json()
        p2 = client.post("/api/projects/create", json={"name": "Project 2"}).json()

        # Create conversation in project 1
        conv = client.post(
            "/api/conversations/create",
            json={"project_id": p1["id"], "title": "Test Chat"}
        ).json()

        # Move to project 2
        response = client.patch(
            f"/api/conversations/{conv['id']}/move",
            json={"project_id": p2["id"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == p2["id"]
        assert data["title"] == "Test Chat"

    def test_move_conversation_invalid_target(self, client):
        """Test error when moving to non-existent project."""
        # Create conversation
        p1 = client.post("/api/projects/create", json={"name": "Project 1"}).json()
        conv = client.post(
            "/api/conversations/create",
            json={"project_id": p1["id"], "title": "Test Chat"}
        ).json()

        # Try to move to invalid project
        response = client.patch(
            f"/api/conversations/{conv['id']}/move",
            json={"project_id": 999}
        )
        assert response.status_code == 404

    def test_move_nonexistent_conversation(self, client):
        """Test error when moving non-existent conversation."""
        # Create project
        p1 = client.post("/api/projects/create", json={"name": "Project 1"}).json()

        # Try to move non-existent conversation
        response = client.patch(
            "/api/conversations/999/move",
            json={"project_id": p1["id"]}
        )
        assert response.status_code == 404


class TestProjectDetails:
    """Tests for project details endpoint."""

    def test_get_project_details_success(self, client):
        """Test getting detailed project information."""
        # Create project
        project = client.post(
            "/api/projects/create",
            json={"name": "Test Project", "description": "Test description"}
        ).json()

        # Create conversations and documents (if upload endpoint exists)
        client.post(
            "/api/conversations/create",
            json={"project_id": project["id"], "title": "Chat 1"}
        )
        client.post(
            "/api/conversations/create",
            json={"project_id": project["id"], "title": "Chat 2"}
        )

        # Get details
        response = client.get(f"/api/projects/{project['id']}/details")
        assert response.status_code == 200
        data = response.json()

        # Verify project info
        assert data["project"]["id"] == project["id"]
        assert data["project"]["name"] == "Test Project"
        assert data["project"]["color"] == "blue"
        assert data["project"]["icon"] == "folder"

        # Verify conversations
        assert data["conversation_count"] == 2
        assert len(data["conversations"]) == 2

        # Verify documents
        assert "documents" in data
        assert "document_count" in data

    def test_get_project_details_not_found(self, client):
        """Test error for non-existent project."""
        response = client.get("/api/projects/999/details")
        assert response.status_code == 404


class TestDeleteProjectWithAction:
    """Tests for delete project with move/delete action."""

    def test_delete_project_with_move_action(self, client):
        """Test deleting project with move action."""
        # Get default project
        default = client.get("/api/projects/default").json()

        # Create project with conversations
        project = client.post(
            "/api/projects/create",
            json={"name": "Test Project"}
        ).json()
        client.post(
            "/api/conversations/create",
            json={"project_id": project["id"], "title": "Chat 1"}
        )
        client.post(
            "/api/conversations/create",
            json={"project_id": project["id"], "title": "Chat 2"}
        )

        # Delete with move action
        response = client.delete(
            f"/api/projects/{project['id']}?action=move"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "move"
        assert data["moved_conversations"] == 2

        # Verify conversations moved to default project
        convs_response = client.get(f"/api/projects/{default['id']}/conversations")
        assert convs_response.json()["total_count"] == 2

    def test_delete_project_with_delete_action(self, client):
        """Test deleting project with delete action."""
        # Create project with conversations
        project = client.post(
            "/api/projects/create",
            json={"name": "Test Project"}
        ).json()
        client.post(
            "/api/conversations/create",
            json={"project_id": project["id"], "title": "Chat 1"}
        )

        # Delete with delete action (permanent)
        response = client.delete(
            f"/api/projects/{project['id']}?action=delete"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "delete"
        assert data["deleted_conversations"] == 1

        # Verify project is gone
        get_response = client.get(f"/api/projects/{project['id']}")
        assert get_response.status_code == 404

    def test_delete_project_missing_action(self, client):
        """Test error when action parameter is missing."""
        # Create project
        project = client.post(
            "/api/projects/create",
            json={"name": "Test Project"}
        ).json()

        # Try to delete without action
        response = client.delete(f"/api/projects/{project['id']}")
        assert response.status_code == 422


class TestProjectListWithFullStats:
    """Tests for enhanced project listing."""

    def test_list_projects_with_stats(self, client):
        """Test listing projects with conversation and document counts."""
        # Create project with conversations
        project = client.post(
            "/api/projects/create",
            json={"name": "Test Project", "color": "red", "icon": "shield"}
        ).json()
        client.post(
            "/api/conversations/create",
            json={"project_id": project["id"], "title": "Chat 1"}
        )
        client.post(
            "/api/conversations/create",
            json={"project_id": project["id"], "title": "Chat 2"}
        )

        # List projects
        response = client.get("/api/projects/list")
        assert response.status_code == 200
        data = response.json()

        # Find our project
        test_project = next(p for p in data["projects"] if p["name"] == "Test Project")
        assert test_project["conversation_count"] == 2
        assert test_project["document_count"] == 0
        assert test_project["color"] == "red"
        assert test_project["icon"] == "shield"
        assert "last_used_at" in test_project

    def test_list_projects_sort_by_name(self, client):
        """Test sorting projects by name."""
        # Create projects
        client.post("/api/projects/create", json={"name": "Zebra Project"})
        client.post("/api/projects/create", json={"name": "Alpha Project"})

        # List with sort=name
        response = client.get("/api/projects/list?sort=name")
        assert response.status_code == 200
        data = response.json()

        # Verify alphabetical order
        names = [p["name"] for p in data["projects"]]
        assert names == sorted(names)

    def test_list_projects_sort_by_manual(self, client):
        """Test sorting projects by manual order."""
        # Create projects
        p1 = client.post("/api/projects/create", json={"name": "Project 1"}).json()
        p2 = client.post("/api/projects/create", json={"name": "Project 2"}).json()

        # Reorder
        client.patch(
            "/api/projects/reorder",
            json={"project_ids": [p2["id"], p1["id"]]}
        )

        # List with sort=manual
        response = client.get("/api/projects/list?sort=manual")
        assert response.status_code == 200
        data = response.json()

        # Verify manual order
        assert data["projects"][0]["id"] == p2["id"]
        assert data["projects"][1]["id"] == p1["id"]
