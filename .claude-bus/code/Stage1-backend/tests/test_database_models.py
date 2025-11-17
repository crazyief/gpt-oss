"""
Unit tests for database models.

Tests SQLAlchemy models for projects, conversations, and messages.
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models.database import Base, Project, Conversation, Message


@pytest.fixture
def test_db() -> Session:
    """
    Create an in-memory SQLite database for testing.

    Returns:
        Session: SQLAlchemy session connected to test database
    """
    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:")

    # Create all tables
    Base.metadata.create_all(engine)

    # Create session factory
    TestSessionLocal = sessionmaker(bind=engine)

    # Create session
    session = TestSessionLocal()

    yield session

    # Cleanup: close session and drop all tables
    session.close()
    Base.metadata.drop_all(engine)


def test_create_project(test_db: Session):
    """
    Test creating a project in the database.

    Verifies that:
    - Project can be created with required fields
    - Auto-generated fields (id, timestamps) are populated
    - Default values (metadata) are set correctly
    """
    # Create a new project
    project = Project(
        name="Test Project",
        description="Test Description"
    )

    # Add to database
    test_db.add(project)
    test_db.commit()
    test_db.refresh(project)

    # Assertions
    assert project.id is not None
    assert project.name == "Test Project"
    assert project.description == "Test Description"
    assert project.created_at is not None
    assert project.updated_at is not None
    assert project.deleted_at is None
    assert project.meta == {}


def test_soft_delete_project(test_db: Session):
    """
    Test soft delete functionality for projects.

    Verifies that:
    - Setting deleted_at marks project as deleted
    - Project can still be queried if explicitly included
    """
    # Create project
    project = Project(name="To Delete")
    test_db.add(project)
    test_db.commit()

    # Soft delete by setting deleted_at
    project.deleted_at = datetime.now()
    test_db.commit()

    # Verify deleted_at is set
    assert project.deleted_at is not None

    # Query with filter should exclude deleted projects
    active_projects = test_db.query(Project).filter(Project.deleted_at.is_(None)).all()
    assert len(active_projects) == 0


def test_create_conversation_with_project(test_db: Session):
    """
    Test creating a conversation associated with a project.

    Verifies that:
    - Conversation can be linked to a project
    - Foreign key relationship works correctly
    - Default values are set
    """
    # Create project first
    project = Project(name="Test Project")
    test_db.add(project)
    test_db.commit()
    test_db.refresh(project)

    # Create conversation linked to project
    conversation = Conversation(
        project_id=project.id,
        title="Test Conversation"
    )
    test_db.add(conversation)
    test_db.commit()
    test_db.refresh(conversation)

    # Assertions
    assert conversation.id is not None
    assert conversation.project_id == project.id
    assert conversation.title == "Test Conversation"
    assert conversation.message_count == 0
    assert conversation.last_message_at is None
    assert conversation.deleted_at is None


def test_conversation_without_project(test_db: Session):
    """
    Test creating a conversation without a project.

    Verifies that:
    - Conversation can exist without project_id (nullable)
    """
    # Create conversation without project
    conversation = Conversation(title="Standalone Chat")
    test_db.add(conversation)
    test_db.commit()
    test_db.refresh(conversation)

    # Assertions
    assert conversation.id is not None
    assert conversation.project_id is None
    assert conversation.title == "Standalone Chat"


def test_create_message_in_conversation(test_db: Session):
    """
    Test creating messages in a conversation.

    Verifies that:
    - User and assistant messages can be created
    - Foreign key relationship to conversation works
    - Default values are set correctly
    """
    # Create conversation
    conversation = Conversation(title="Test Chat")
    test_db.add(conversation)
    test_db.commit()
    test_db.refresh(conversation)

    # Create user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content="Hello, AI!"
    )
    test_db.add(user_message)
    test_db.commit()
    test_db.refresh(user_message)

    # Create assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content="Hello! How can I help you?",
        token_count=10,
        model_name="gpt-oss-20b",
        completion_time_ms=1500
    )
    test_db.add(assistant_message)
    test_db.commit()
    test_db.refresh(assistant_message)

    # Assertions for user message
    assert user_message.id is not None
    assert user_message.conversation_id == conversation.id
    assert user_message.role == "user"
    assert user_message.content == "Hello, AI!"
    assert user_message.token_count == 0  # Default for user messages
    assert user_message.reaction is None

    # Assertions for assistant message
    assert assistant_message.id is not None
    assert assistant_message.role == "assistant"
    assert assistant_message.token_count == 10
    assert assistant_message.model_name == "gpt-oss-20b"
    assert assistant_message.completion_time_ms == 1500


def test_message_reaction(test_db: Session):
    """
    Test adding reactions to messages.

    Verifies that:
    - Reactions can be added to messages
    - Reactions can be updated
    - Reactions can be removed (set to NULL)
    """
    # Create conversation and message
    conversation = Conversation(title="Test Chat")
    test_db.add(conversation)
    test_db.commit()

    message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content="Test response"
    )
    test_db.add(message)
    test_db.commit()
    test_db.refresh(message)

    # Add thumbs_up reaction
    message.reaction = "thumbs_up"
    test_db.commit()
    test_db.refresh(message)
    assert message.reaction == "thumbs_up"

    # Change to thumbs_down
    message.reaction = "thumbs_down"
    test_db.commit()
    test_db.refresh(message)
    assert message.reaction == "thumbs_down"

    # Remove reaction
    message.reaction = None
    test_db.commit()
    test_db.refresh(message)
    assert message.reaction is None


def test_message_regeneration_hierarchy(test_db: Session):
    """
    Test message regeneration using parent_message_id.

    Verifies that:
    - Messages can have parent_message_id set
    - Self-referential foreign key works correctly
    """
    # Create conversation
    conversation = Conversation(title="Test Chat")
    test_db.add(conversation)
    test_db.commit()

    # Create user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content="Explain something"
    )
    test_db.add(user_message)
    test_db.commit()
    test_db.refresh(user_message)

    # Create first assistant response
    response_1 = Message(
        conversation_id=conversation.id,
        role="assistant",
        content="Response 1",
        parent_message_id=user_message.id
    )
    test_db.add(response_1)
    test_db.commit()

    # Create regenerated response (also references same user message)
    response_2 = Message(
        conversation_id=conversation.id,
        role="assistant",
        content="Response 2 (regenerated)",
        parent_message_id=user_message.id
    )
    test_db.add(response_2)
    test_db.commit()
    test_db.refresh(response_2)

    # Assertions
    assert response_1.parent_message_id == user_message.id
    assert response_2.parent_message_id == user_message.id

    # Query all responses to the user message
    responses = test_db.query(Message).filter(
        Message.parent_message_id == user_message.id
    ).all()
    assert len(responses) == 2


def test_cascade_delete_conversations(test_db: Session):
    """
    Test cascade delete from project to conversations.

    Verifies that:
    - Deleting a project cascades to conversations (hard delete)
    """
    # Create project with conversation
    project = Project(name="Test Project")
    test_db.add(project)
    test_db.commit()

    conversation = Conversation(project_id=project.id, title="Test Chat")
    test_db.add(conversation)
    test_db.commit()

    # Hard delete project (actual delete, not soft delete)
    test_db.delete(project)
    test_db.commit()

    # Verify conversation is also deleted (cascade)
    conversations = test_db.query(Conversation).all()
    assert len(conversations) == 0


def test_cascade_delete_messages(test_db: Session):
    """
    Test cascade delete from conversation to messages.

    Verifies that:
    - Deleting a conversation cascades to messages
    """
    # Create conversation with messages
    conversation = Conversation(title="Test Chat")
    test_db.add(conversation)
    test_db.commit()

    message_1 = Message(conversation_id=conversation.id, role="user", content="Hi")
    message_2 = Message(conversation_id=conversation.id, role="assistant", content="Hello")
    test_db.add_all([message_1, message_2])
    test_db.commit()

    # Hard delete conversation
    test_db.delete(conversation)
    test_db.commit()

    # Verify messages are also deleted
    messages = test_db.query(Message).all()
    assert len(messages) == 0


def test_project_meta_json(test_db: Session):
    """
    Test JSON meta field in Project model.

    Verifies that:
    - Meta can store arbitrary JSON data
    - Meta defaults to empty dict
    """
    # Create project with meta
    project = Project(
        name="Test Project",
        meta={"tags": ["cybersecurity", "IEC 62443"], "priority": "high"}
    )
    test_db.add(project)
    test_db.commit()
    test_db.refresh(project)

    # Assertions
    assert project.meta["tags"] == ["cybersecurity", "IEC 62443"]
    assert project.meta["priority"] == "high"

    # Test default empty dict
    project_2 = Project(name="Project 2")
    test_db.add(project_2)
    test_db.commit()
    test_db.refresh(project_2)
    assert project_2.meta == {}
