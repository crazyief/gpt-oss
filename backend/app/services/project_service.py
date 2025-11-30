"""
Project service layer for business logic.

Handles CRUD operations for projects with pagination, filtering,
and soft-delete support.

Stats methods moved to project_stats_service.py to comply with 400-line limit.
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.database import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """
    Service class for project-related business logic.

    Encapsulates database operations and business rules for projects.
    All queries automatically filter soft-deleted projects.
    """

    # Default project name constant (Stage 3: updated to "Default")
    DEFAULT_PROJECT_NAME = "Default"

    @staticmethod
    def get_or_create_default_project(db: Session) -> Project:
        """
        Get the default project, creating it if it doesn't exist.

        Stage 3: Looks for project with is_default=True. If not found, creates one.
        This ensures users always have a clearly labeled default workspace.

        WHY this approach:
        - Clear UX: Users see "Default" as their starting point
        - Predictable: Always marked with is_default flag
        - Ensures "New Chat" button is always usable on first load
        - Prevents deletion of default project (enforced in delete_project)

        Args:
            db: Database session

        Returns:
            The default project instance
        """
        # Look for existing default project (by is_default flag)
        stmt = select(Project).where(
            Project.is_default == True,
            Project.deleted_at.is_(None)
        )
        project = db.execute(stmt).scalar_one_or_none()

        if project:
            return project

        # No default project exists - create one
        # Stage 3: Include new fields (color, icon, is_default, sort_order)
        default_project = Project(
            name=ProjectService.DEFAULT_PROJECT_NAME,
            description="Default project for quick chats",
            color="gray",
            icon="folder",
            is_default=True,
            sort_order=0
        )
        db.add(default_project)
        db.commit()
        db.refresh(default_project)

        return default_project

    @staticmethod
    def create_project(db: Session, project_data: ProjectCreate) -> Project:
        """
        Create a new project.

        Args:
            db: Database session
            project_data: Validated project creation data

        Returns:
            Created project instance

        Note:
            The 'meta' field is initialized as empty dict {} by default.
            Timestamps (created_at, updated_at) are set automatically by the database.
        """
        # Create new project instance
        # WHY dict unpacking: Pydantic v2 uses model_dump() instead of dict().
        # This is cleaner than setting each field individually and automatically
        # handles validation and type conversion.
        project = Project(**project_data.model_dump())

        # Add to session and commit
        db.add(project)
        db.commit()
        db.refresh(project)  # Refresh to get auto-generated fields

        return project

    @staticmethod
    def get_project_by_id(db: Session, project_id: int) -> Optional[Project]:
        """
        Get a project by ID.

        Args:
            db: Database session
            project_id: Project ID to retrieve

        Returns:
            Project instance or None if not found or soft-deleted

        Note:
            Returns None for soft-deleted projects (deleted_at IS NOT NULL).
            This enforces soft-delete semantics at the service layer.
        """
        # Build query with soft-delete filter
        # WHY filter deleted_at: All queries must exclude soft-deleted records.
        # This prevents accidentally exposing deleted data to users and ensures
        # consistency across all service methods.
        stmt = select(Project).where(
            Project.id == project_id,
            Project.deleted_at.is_(None)
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def list_projects(
        db: Session,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[list[Project], int]:
        """
        List projects with pagination.

        Args:
            db: Database session
            limit: Maximum number of projects to return (default: 50, max: 100)
            offset: Number of projects to skip (for pagination)

        Returns:
            Tuple of (projects list, total count)

        Note:
            Projects are ordered by created_at DESC (newest first).
            Total count is for pagination UI - it's the count BEFORE applying limit/offset.
        """
        # Enforce max limit to prevent excessive queries
        # WHY cap at 100: Prevents clients from requesting thousands of records
        # at once, which could overwhelm the database and cause memory issues.
        # This is a defensive measure for production stability.
        limit = min(limit, 100)

        # Build base query with soft-delete filter
        base_query = select(Project).where(Project.deleted_at.is_(None))

        # Get total count (before pagination)
        # WHY separate count query: SQLAlchemy needs COUNT to be executed separately
        # from the main query when using limit/offset. This is more efficient than
        # loading all records and counting in Python.
        count_stmt = select(func.count()).select_from(base_query.subquery())
        total_count = db.execute(count_stmt).scalar_one()

        # Get paginated results
        # Order by created_at DESC for "newest first" behavior
        stmt = base_query.order_by(Project.created_at.desc()).limit(limit).offset(offset)
        projects = db.execute(stmt).scalars().all()

        return list(projects), total_count

    @staticmethod
    def update_project(
        db: Session,
        project_id: int,
        update_data: ProjectUpdate
    ) -> Optional[Project]:
        """
        Update a project.

        Args:
            db: Database session
            project_id: Project ID to update
            update_data: Validated update data (only non-None fields are updated)

        Returns:
            Updated project instance or None if not found

        Note:
            This performs a partial update - only fields present in update_data
            are modified. The updated_at timestamp is automatically updated by
            the database via onupdate trigger.
        """
        # Get existing project
        project = ProjectService.get_project_by_id(db, project_id)
        if not project:
            return None

        # Update fields
        # WHY exclude_unset: Only update fields that were explicitly set in the request.
        # This allows partial updates (e.g., updating only the name without touching description).
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(project, key, value)

        # Commit changes
        db.commit()
        db.refresh(project)

        return project

    @staticmethod
    def delete_project(
        db: Session,
        project_id: int,
        hard_delete: bool = False,
        action: str = "delete"
    ) -> tuple[bool, dict]:
        """
        Delete a project (soft or hard delete).

        Args:
            db: Database session
            project_id: Project ID to delete
            hard_delete: If True, permanently delete with cascade. If False, soft delete.
            action: "move" (move to Default) or "delete" (permanently delete)

        Returns:
            Tuple of (success: bool, details: dict)
            details contains: action, moved/deleted counts

        Raises:
            ValueError: If attempting to delete default project

        Note:
            SOFT DELETE (hard_delete=False): Sets deleted_at to current timestamp.
            The project record is never physically removed from the database.
            WHY soft delete: Preserves data for audit trails and allows recovery
            of accidentally deleted projects. Required for compliance with
            cybersecurity audit standards (IEC 62443).

            HARD DELETE (hard_delete=True): Permanently removes project and ALL
            associated data (conversations, messages, documents with files).
            WHY hard delete option: Stage 2 requirement for full cascade deletion
            of documents and files. Cannot be undone.

            STAGE 3 ADDITIONS:
            - Prevent deletion of default project (is_default=True)
            - Support "move" action: move conversations/docs to Default before deletion
        """
        # Get existing project
        project = ProjectService.get_project_by_id(db, project_id)
        if not project:
            return False, {}

        # Stage 3: Prevent deletion of default project
        if project.is_default:
            raise ValueError("Cannot delete the default project")

        # Import here to avoid circular imports
        from app.services.document_service import DocumentService
        from app.models.database import Conversation, Document

        # Count items before deletion
        conversation_count = db.query(Conversation).filter(
            Conversation.project_id == project_id,
            Conversation.deleted_at.is_(None)
        ).count()
        document_count = db.query(Document).filter(
            Document.project_id == project_id
        ).count()

        details = {"action": action}

        if action == "move":
            # Get default project
            default_project = ProjectService.get_or_create_default_project(db)

            # Move all conversations to default project
            db.query(Conversation).filter(
                Conversation.project_id == project_id
            ).update({"project_id": default_project.id})

            # Move all documents to default project
            db.query(Document).filter(
                Document.project_id == project_id
            ).update({"project_id": default_project.id})

            db.commit()

            details["moved_conversations"] = conversation_count
            details["moved_documents"] = document_count

            # Now delete the empty project
            if hard_delete:
                db.delete(project)
                db.commit()
            else:
                project.deleted_at = datetime.now(timezone.utc)
                db.commit()

        else:  # action == "delete"
            if hard_delete:
                # Hard delete: Remove all associated data
                # Delete all documents (files + records)
                DocumentService.delete_project_documents(db, project_id)

                # Delete project record (cascade will delete conversations and messages)
                db.delete(project)
                db.commit()
            else:
                # Soft delete: Set deleted_at timestamp
                project.deleted_at = datetime.now(timezone.utc)
                db.commit()

            details["deleted_conversations"] = conversation_count
            details["deleted_documents"] = document_count

        return True, details

    @staticmethod
    def get_project_stats(db: Session, project_id: int) -> Optional[dict]:
        """
        Get statistics for a project.

        Delegates to ProjectStatsService for the actual implementation.
        """
        from app.services.project_stats_service import ProjectStatsService
        return ProjectStatsService.get_project_stats(db, project_id)

    @staticmethod
    def list_projects_with_stats(
        db: Session,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[list[dict], int]:
        """
        List projects with conversation counts in a single optimized query.

        Delegates to ProjectStatsService for the actual implementation.
        """
        from app.services.project_stats_service import ProjectStatsService
        return ProjectStatsService.list_projects_with_stats(db, limit, offset)
