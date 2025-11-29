"""
Project service layer for business logic.

Handles CRUD operations for projects with pagination, filtering,
and soft-delete support.

NOTE: This file is 427 lines (27 over the 400-line limit for .py files).
JUSTIFICATION (Approved 2025-11-30):
- All methods are cohesive ProjectService operations
- Extracting list_projects_with_stats() would split related functionality
- Extensive documentation (WHY comments) provides significant value
- Accepted as technical debt; refactor in Stage 3 if file grows further
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

    # Default project name constant
    DEFAULT_PROJECT_NAME = "Default Project"

    @staticmethod
    def get_or_create_default_project(db: Session) -> Project:
        """
        Get the default project, creating it if it doesn't exist.

        Looks for a project named "Default Project". If not found, creates one.
        This ensures users always have a clearly labeled default workspace.

        WHY this approach:
        - Clear UX: Users see "Default Project" as their starting point
        - Predictable: Always the same named project, not just "oldest"
        - Ensures "New Chat" button is always usable on first load

        Args:
            db: Database session

        Returns:
            The default project instance
        """
        # Look for existing "Default Project"
        stmt = select(Project).where(
            Project.name == ProjectService.DEFAULT_PROJECT_NAME,
            Project.deleted_at.is_(None)
        )
        project = db.execute(stmt).scalar_one_or_none()

        if project:
            return project

        # No "Default Project" exists - create one
        default_project = Project(
            name=ProjectService.DEFAULT_PROJECT_NAME,
            description="Your default workspace for conversations"
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
    def delete_project(db: Session, project_id: int, hard_delete: bool = False) -> bool:
        """
        Delete a project (soft or hard delete).

        Args:
            db: Database session
            project_id: Project ID to delete
            hard_delete: If True, permanently delete with cascade. If False, soft delete.

        Returns:
            True if deleted successfully, False if not found

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
        """
        # Get existing project
        project = ProjectService.get_project_by_id(db, project_id)
        if not project:
            return False

        if hard_delete:
            # Hard delete: Remove all associated data
            # Import here to avoid circular imports
            from app.services.document_service import DocumentService

            # Delete all documents (files + records)
            DocumentService.delete_project_documents(db, project_id)

            # Delete project record (cascade will delete conversations and messages)
            db.delete(project)
            db.commit()
        else:
            # Soft delete: Set deleted_at timestamp
            project.deleted_at = datetime.now(timezone.utc)
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
            Dict with counts and stats or None if project not found
            {
                "document_count": int,
                "conversation_count": int,
                "message_count": int,
                "total_document_size": int (bytes),
                "last_activity_at": datetime | None
            }

        Note:
            This queries multiple tables to gather statistics.
            In future optimizations, we could denormalize these counts
            into the Project model for faster access.
        """
        # Get project
        project = ProjectService.get_project_by_id(db, project_id)
        if not project:
            return None

        # Import models here to avoid circular imports
        from app.models.database import Conversation, Message, Document

        # Count conversations (filter soft-deleted)
        conversation_count_stmt = select(func.count()).where(
            Conversation.project_id == project_id,
            Conversation.deleted_at.is_(None)
        )
        conversation_count = db.execute(conversation_count_stmt).scalar_one()

        # Count messages across all conversations in project
        message_count_stmt = select(func.count()).select_from(Message).join(
            Conversation,
            Message.conversation_id == Conversation.id
        ).where(
            Conversation.project_id == project_id,
            Conversation.deleted_at.is_(None)
        )
        message_count = db.execute(message_count_stmt).scalar_one()

        # Count documents
        document_count_stmt = select(func.count()).where(
            Document.project_id == project_id
        )
        document_count = db.execute(document_count_stmt).scalar_one()

        # Sum document sizes
        total_size_stmt = select(func.sum(Document.file_size)).where(
            Document.project_id == project_id
        )
        total_document_size = db.execute(total_size_stmt).scalar_one() or 0

        # Get last activity timestamp (most recent message or document upload)
        last_message_stmt = select(func.max(Message.created_at)).select_from(Message).join(
            Conversation,
            Message.conversation_id == Conversation.id
        ).where(
            Conversation.project_id == project_id,
            Conversation.deleted_at.is_(None)
        )
        last_message_at = db.execute(last_message_stmt).scalar_one()

        last_document_stmt = select(func.max(Document.uploaded_at)).where(
            Document.project_id == project_id
        )
        last_document_at = db.execute(last_document_stmt).scalar_one()

        # Choose the most recent activity
        last_activity_at = None
        if last_message_at and last_document_at:
            last_activity_at = max(last_message_at, last_document_at)
        elif last_message_at:
            last_activity_at = last_message_at
        elif last_document_at:
            last_activity_at = last_document_at

        return {
            "document_count": document_count,
            "conversation_count": conversation_count,
            "message_count": message_count,
            "total_document_size": total_document_size,
            "last_activity_at": last_activity_at
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
