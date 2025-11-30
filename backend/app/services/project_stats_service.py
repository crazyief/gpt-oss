"""
Project statistics service.

Handles stats queries and aggregations for projects.
Extracted from project_service.py to comply with 400-line limit.
"""

from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.database import Project, Conversation, Message, Document


class ProjectStatsService:
    """
    Service class for project statistics and aggregations.
    """

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
        # Get project (check it exists and isn't deleted)
        project_stmt = select(Project).where(
            Project.id == project_id,
            Project.deleted_at.is_(None)
        )
        project = db.execute(project_stmt).scalar_one_or_none()
        if not project:
            return None

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
