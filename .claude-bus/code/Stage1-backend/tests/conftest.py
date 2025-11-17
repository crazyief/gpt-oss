"""
Shared pytest fixtures for all test modules.

Provides common test database and client setup.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.models.database import Base
from app.db.session import get_db


# Create shared test database engine
# WHY module-level: Ensures tables persist across all tests in the session
# WHY StaticPool: Shares single connection across threads for in-memory database
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

# Create all tables once at module import
Base.metadata.create_all(engine)

# Session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def test_db():
    """
    Create database session for testing.

    Yields a SQLAlchemy session that commits on success or rolls back on failure.
    """
    db = TestingSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@pytest.fixture
def client(test_db):
    """
    Create FastAPI test client with database override.

    Injects the test database session into the FastAPI dependency system.
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
