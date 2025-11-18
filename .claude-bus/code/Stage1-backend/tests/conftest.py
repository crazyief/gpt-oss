"""
Shared pytest fixtures for all test modules.

Provides common test database and client setup.
"""

import sys
from pathlib import Path

# Add project root to Python path
# WHY: pytest runs from tests/ directory, but app module is in parent directory.
# Without this, 'from app.main import app' fails with ModuleNotFoundError.
# This is a standard pattern for pytest projects where tests/ is a subdirectory.
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Patch init_db BEFORE importing app.main to prevent production DB access
# WHY patch before import: The app.main module's lifespan manager references init_db
# at import time. If we patch after import, the lifespan still has the old reference.
# By patching before import, we ensure the lifespan sees our mocked version.
import app.db.session
app.db.session.init_db = lambda: None

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import FastAPI app instance and database dependencies
from app.main import app as fastapi_app
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
    Create database session for testing with automatic rollback.

    Yields a SQLAlchemy session within a transaction that ALWAYS rolls back
    after the test, ensuring test isolation. Each test starts with clean state.

    WHY nested transaction pattern: Service layer calls db.commit(), but we need
    to rollback ALL changes after each test. Solution: wrap the test in a
    savepoint (nested transaction). The service's commit() only commits to the
    savepoint, not the database. At test end, we rollback the savepoint, undoing
    all changes including committed ones.

    WHY always rollback: Tests should not affect each other. By rolling back
    all changes (even on success), we ensure each test starts with the same
    empty database. This prevents test pollution where one test's data affects
    another test's assertions, leading to flaky tests that pass/fail based on
    execution order.
    """
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)

    # Start a savepoint (nested transaction)
    # WHY nested transaction: Allows service layer to "commit" without actually
    # persisting to database. The commit() only commits to this savepoint.
    # At test end, we rollback the outer transaction, undoing all changes.
    nested = connection.begin_nested()

    # Event handler to restart savepoint after each commit
    # WHY this event: When service layer calls db.commit(), SQLAlchemy ends
    # the savepoint. We need to immediately create a new savepoint so the
    # next commit also stays isolated. Without this, the second commit would
    # persist to the database.
    @event.listens_for(db.sync_session if hasattr(db, 'sync_session') else db, "after_transaction_end")
    def restart_savepoint(session, trans):
        if trans.nested and not trans._parent.nested:
            session.begin_nested()

    try:
        yield db
    finally:
        # Rollback outer transaction to undo ALL changes
        db.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(test_db):
    """
    Create FastAPI test client with database override.

    Injects the test database session into the FastAPI dependency system.
    Uses raise_server_exceptions=False to prevent FastAPI startup errors
    from failing the test setup.

    WHY raise_server_exceptions=False: FastAPI's lifespan manager tries to
    call init_db() which requires the ./data/ directory to exist. In tests,
    we don't want to create production files. By setting raise_server_exceptions
    to False, startup errors are logged but don't crash the test client.
    We then override get_db to use our in-memory test database, bypassing
    the production database entirely.
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    fastapi_app.dependency_overrides[get_db] = override_get_db

    # Use raise_server_exceptions=False to ignore init_db() errors during startup
    # The test database is already created, so we don't need the app's init_db()
    with TestClient(fastapi_app, raise_server_exceptions=False) as c:
        yield c

    fastapi_app.dependency_overrides.clear()
