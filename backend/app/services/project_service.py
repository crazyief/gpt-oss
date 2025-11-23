"""
Project service layer for business logic.

Handles CRUD operations for projects with pagination, filtering,
and soft-delete support.
"""

from datetime import datetime
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
    def delete_project(db: Session, project_id: int) -> bool:
        """
        Soft-delete a project.

        Args:
            db: Database session
            project_id: Project ID to delete

        Returns:
            True if deleted successfully, False if not found

        Note:
            This is a soft delete - sets deleted_at to current timestamp.
            The project record is never physically removed from the database.
            WHY soft delete: Preserves data for audit trails and allows recovery
            of accidentally deleted projects. Required for compliance with
            cybersecurity audit standards (IEC 62443).
        """
        # Get existing project
        project = ProjectService.get_project_by_id(db, project_id)
        if not project:
            return False

        # Set deleted_at timestamp
        project.deleted_at = datetime.utcnow()

        # Commit changes
        db.commit()

        return True

    @staticmethod
    def get_project_stats(db: Session, project_id: int) -> Optional[dict]:
        """
        Get statistics for a project.

        Args:
            db: Database session
            project_id: Project ID

        Returns:
            Dict with conversation_count or None if project not found

        Note:
            This queries the conversations table to get the count.
            In future optimizations, we could denormalize this count
            into the Project model for faster access (similar to
            message_count in Conversation).
        """
        # Get project
        project = ProjectService.get_project_by_id(db, project_id)
        if not project:
            return None

        # Count conversations (filter soft-deleted)
        # WHY import here: Avoids circular import issues. Conversation depends
        # on Project, so we can't import Conversation at the top of this file.
        from app.models.database import Conversation

        count_stmt = select(func.count()).where(
            Conversation.project_id == project_id,
            Conversation.deleted_at.is_(None)
        )
        conversation_count = db.execute(count_stmt).scalar_one()

        return {
            "conversation_count": conversation_count
        }

    @staticmethod
    def list_projects_with_stats(
        db: Session,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[list[dict], int]:
        """
        List projects with conversation counts in a single optimized query.

        FIXED (Issue-8: N+1 Query Pattern):
        ===================================
        This method replaces the N+1 query pattern where we:
        1. Fetch N projects (1 query)
        2. Fetch stats for each project (N queries)

        New approach uses a single LEFT JOIN with GROUP BY:
        - 1 query for all projects + counts
        - 1 query for total count
        Total: 2 queries instead of N+1

        Performance improvement:
        - 50 projects: 51 queries → 2 queries (25x faster)
        - 100 projects: 101 queries → 2 queries (50x faster)

        Args:
            db: Database session
            limit: Maximum number of projects to return (default: 50, max: 100)
            offset: Number of projects to skip (for pagination)

        Returns:
            Tuple of (projects with stats list, total count)
            Each project dict includes: id, name, description, created_at, conversation_count
        """
        from app.models.database import Conversation

        # Enforce max limit
        limit = min(limit, 100)

        # Build optimized query with LEFT JOIN and GROUP BY
        # WHY LEFT JOIN: Includes projects with 0 conversations
        # WHY GROUP BY: Aggregates conversation counts per project
        stmt = (
            select(
                Project.id,
                Project.name,
                Project.description,
                Project.created_at,
                func.count(Conversation.id).label('conversation_count')
            )
            .outerjoin(
                Conversation,
                (Conversation.project_id == Project.id) &
                (Conversation.deleted_at.is_(None))  # Filter soft-deleted conversations
            )
            .where(Project.deleted_at.is_(None))  # Filter soft-deleted projects
            .group_by(Project.id)  # Group by project for count aggregation
            .order_by(Project.created_at.desc())  # Newest first
            .limit(limit)
            .offset(offset)
        )

        # Execute query and get results
        results = db.execute(stmt).all()

        # Convert to list of dicts
        projects_with_stats = [
            {
                "id": row.id,
                "name": row.name,
                "description": row.description,
                "created_at": row.created_at,
                "conversation_count": row.conversation_count
            }
            for row in results
        ]

        # Get total count (separate query, but still only 2 queries total)
        count_stmt = select(func.count()).where(Project.deleted_at.is_(None))
        total_count = db.execute(count_stmt).scalar_one()

        return projects_with_stats, total_count
