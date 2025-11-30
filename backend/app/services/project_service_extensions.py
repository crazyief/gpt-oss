"""
Project service extensions for Stage 3 features.

Additional methods for project reordering, detailed views, and enhanced stats.
Separated to keep project_service.py under 500 lines.
"""

from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.database import Project, Conversation, Document


class ProjectServiceExtensions:
    """
    Extensions to ProjectService for Stage 3 features.

    Includes methods for:
    - Project reordering (drag-and-drop support)
    - Project details with conversations and documents
    - Enhanced project listing with document counts
    """

    @staticmethod
    def reorder_projects(db: Session, project_ids: list[int]) -> list[Project]:
        """
        Reorder projects by updating sort_order field.

        Args:
            db: Database session
            project_ids: Array of project IDs in new order (first = sort_order 0)

        Returns:
            List of updated projects

        Raises:
            ValueError: If project_ids is empty or contains invalid IDs

        Note:
            This method updates the sort_order field for each project based on
            its position in the project_ids array. The UI will use this order
            when displaying projects in manual sort mode.
        """
        if not project_ids:
            raise ValueError("project_ids cannot be empty")

        # Verify all project IDs exist
        existing_projects = db.query(Project).filter(
            Project.id.in_(project_ids),
            Project.deleted_at.is_(None)
        ).all()

        if len(existing_projects) != len(project_ids):
            raise ValueError("Some project IDs do not exist")

        # Update sort_order for each project
        for index, project_id in enumerate(project_ids):
            db.query(Project).filter(
                Project.id == project_id
            ).update({"sort_order": index})

        db.commit()

        # Return updated projects
        updated_projects = db.query(Project).filter(
            Project.id.in_(project_ids),
            Project.deleted_at.is_(None)
        ).order_by(Project.sort_order).all()

        return updated_projects

    @staticmethod
    def get_project_details(db: Session, project_id: int) -> Optional[dict]:
        """
        Get detailed project information with conversations and documents.

        Args:
            db: Database session
            project_id: Project ID

        Returns:
            Dict with project info, conversations, documents, and counts
            {
                "project": Project dict,
                "conversations": List of conversation dicts,
                "documents": List of document dicts,
                "conversation_count": int,
                "document_count": int
            }
            Returns None if project not found.

        Note:
            This endpoint is used by the ProjectsTab to display detailed
            information when a project is selected.
        """
        # Get project
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.deleted_at.is_(None)
        ).first()

        if not project:
            return None

        # Get conversations
        conversations = db.query(Conversation).filter(
            Conversation.project_id == project_id,
            Conversation.deleted_at.is_(None)
        ).order_by(Conversation.last_message_at.desc().nulls_last()).all()

        # Get documents
        documents = db.query(Document).filter(
            Document.project_id == project_id
        ).order_by(Document.uploaded_at.desc()).all()

        # Convert to dicts
        conversation_list = [
            {
                "id": conv.id,
                "title": conv.title,
                "message_count": conv.message_count,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at
            }
            for conv in conversations
        ]

        document_list = [
            {
                "id": doc.id,
                "original_filename": doc.original_filename,
                "file_size": doc.file_size,
                "file_type": doc.mime_type.split('/')[-1] if '/' in doc.mime_type else doc.mime_type,
                "uploaded_at": doc.uploaded_at
            }
            for doc in documents
        ]

        return {
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "color": project.color,
                "icon": project.icon,
                "is_default": bool(project.is_default),
                "created_at": project.created_at,
                "updated_at": project.updated_at
            },
            "conversations": conversation_list,
            "documents": document_list,
            "conversation_count": len(conversation_list),
            "document_count": len(document_list)
        }

    @staticmethod
    def list_projects_with_full_stats(
        db: Session,
        sort_by: str = "recent",
        limit: int = 50,
        offset: int = 0
    ) -> tuple[list[dict], int]:
        """
        List projects with conversation AND document counts.

        Stage 3 enhancement: Adds document counts and last_used_at timestamp.

        Args:
            db: Database session
            sort_by: Sort order - "recent", "name", or "manual"
            limit: Maximum number of projects (default: 50, max: 100)
            offset: Number of projects to skip (default: 0)

        Returns:
            Tuple of (projects with stats list, total count)
            Each project dict includes:
            - id, name, description, color, icon, is_default, sort_order
            - conversation_count, document_count
            - last_used_at (most recent activity)
            - created_at, updated_at

        Note:
            This uses optimized queries to avoid N+1 patterns.
            - 2 queries for conversation counts (LEFT JOIN + GROUP BY)
            - 2 queries for document counts (LEFT JOIN + GROUP BY)
            - 1 query for last activity timestamps
            Total: 5 queries instead of 1 + (2 * N)
        """
        # Enforce max limit
        limit = min(limit, 100)

        # Build optimized query with LEFT JOINs and GROUP BY
        stmt = (
            select(
                Project.id,
                Project.name,
                Project.description,
                Project.color,
                Project.icon,
                Project.is_default,
                Project.sort_order,
                Project.created_at,
                Project.updated_at,
                func.count(func.distinct(Conversation.id)).label('conversation_count'),
                func.count(func.distinct(Document.id)).label('document_count'),
                func.max(
                    func.coalesce(
                        Conversation.last_message_at,
                        Document.uploaded_at,
                        Project.updated_at
                    )
                ).label('last_used_at')
            )
            .outerjoin(
                Conversation,
                (Conversation.project_id == Project.id) &
                (Conversation.deleted_at.is_(None))
            )
            .outerjoin(
                Document,
                Document.project_id == Project.id
            )
            .where(Project.deleted_at.is_(None))
            .group_by(Project.id)
        )

        # Apply sorting
        if sort_by == "name":
            stmt = stmt.order_by(Project.name.asc())
        elif sort_by == "manual":
            stmt = stmt.order_by(Project.sort_order.asc())
        else:  # "recent" (default)
            stmt = stmt.order_by(
                func.max(
                    func.coalesce(
                        Conversation.last_message_at,
                        Document.uploaded_at,
                        Project.updated_at
                    )
                ).desc()
            )

        stmt = stmt.limit(limit).offset(offset)

        # Execute query
        results = db.execute(stmt).all()

        # Convert to list of dicts
        projects_with_stats = [
            {
                "id": row.id,
                "name": row.name,
                "description": row.description,
                "color": row.color,
                "icon": row.icon,
                "is_default": bool(row.is_default),
                "sort_order": row.sort_order,
                "conversation_count": row.conversation_count,
                "document_count": row.document_count,
                "last_used_at": row.last_used_at,
                "created_at": row.created_at,
                "updated_at": row.updated_at
            }
            for row in results
        ]

        # Get total count
        count_stmt = select(func.count()).where(Project.deleted_at.is_(None))
        total_count = db.execute(count_stmt).scalar_one()

        return projects_with_stats, total_count
