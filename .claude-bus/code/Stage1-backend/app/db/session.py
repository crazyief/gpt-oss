"""
Database session management and initialization.

This module handles SQLAlchemy engine creation, session lifecycle,
and database initialization including WAL mode configuration.
"""

import logging
from typing import Generator
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.models.database import Base

# Configure logging for database operations
logger = logging.getLogger(__name__)


# SQLAlchemy engine instance
# check_same_thread=False is required for SQLite with FastAPI async
# This is safe because SQLAlchemy handles thread safety internally
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_pre_ping=True,  # Verify connections before using them
)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Configure SQLite-specific settings on connection.

    Enables WAL (Write-Ahead Logging) mode for concurrent access.
    WAL mode allows multiple readers while a write is in progress.

    Args:
        dbapi_conn: Raw database connection
        connection_record: SQLAlchemy connection record

    Notes:
        - WAL mode creates -wal and -shm files alongside the .db file
        - Requires local filesystem (not network file systems)
        - Provides better concurrency than default DELETE mode

    WHY WAL mode: SQLite's default DELETE mode only allows 1 writer OR N readers,
    blocking all reads during writes. WAL mode allows 1 writer AND N readers
    simultaneously by writing changes to a separate -wal file, then checkpointing
    to the main .db file later. This is CRITICAL for FastAPI's concurrent request
    handling - without WAL, every write (like creating a message) would block all
    read requests (like loading conversations), causing 500ms+ latency spikes.

    WHY foreign keys need explicit enable: SQLite disables FK constraints by default
    for backward compatibility (pre-3.6.19 behavior). Without explicit PRAGMA, our
    CASCADE deletes and SET NULL behaviors won't work - deleting a project wouldn't
    cascade to conversations, violating referential integrity and creating orphaned
    records. This is a critical data integrity issue that must be enforced at DB level.
    """
    # Only apply pragma to SQLite connections
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_conn.cursor()

        # Enable WAL mode for concurrent reads during writes
        # This allows multiple readers + 1 writer simultaneously
        # Critical for Stage 2+ when we have multiple API requests
        cursor.execute("PRAGMA journal_mode=WAL")

        # Increase cache size to 10MB for better performance
        # Default is 2MB which causes excessive disk I/O
        cursor.execute("PRAGMA cache_size=-10000")

        # Enable foreign key constraints (not enabled by default in SQLite)
        # Required for CASCADE deletes and SET NULL to work properly
        cursor.execute("PRAGMA foreign_keys=ON")

        cursor.close()

        logger.info("SQLite WAL mode enabled with foreign key constraints")


# Session factory
# Creates new Session instances for each request
# autocommit=False: Manual transaction control
# autoflush=False: Manual flush control for better performance
# WHY autocommit=False: We want explicit transaction boundaries via db.commit().
# This gives us control over when changes are persisted and allows rollback on errors.
# Autocommit mode would commit after every statement, preventing multi-statement
# transactions and making error recovery impossible.
# WHY autoflush=False: By default, SQLAlchemy flushes changes before every query
# to ensure query results reflect pending changes. However, this causes unnecessary
# database round-trips. We explicitly flush when needed, improving performance by
# batching multiple changes into a single flush operation.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def init_db() -> None:
    """
    Initialize database schema.

    Creates all tables defined in Base.metadata.
    This is safe to call multiple times - existing tables are not modified.

    Should be called at application startup before serving requests.
    """
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        # Verify indexes were created
        with engine.connect() as conn:
            if "sqlite" in settings.DATABASE_URL:
                result = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
                )
                indexes = [row[0] for row in result]
                logger.info(f"Created {len(indexes)} indexes: {', '.join(indexes)}")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI routes to get database session.

    Yields a SQLAlchemy Session instance that is automatically closed
    after the request completes. Handles commit/rollback automatically.

    Yields:
        Session: SQLAlchemy database session

    Example:
        @app.get("/projects")
        def get_projects(db: Session = Depends(get_db)):
            return db.query(Project).all()

    Notes:
        - Session is automatically committed if no exceptions occur
        - Session is rolled back if an exception is raised
        - Session is always closed in the finally block

    WHY this pattern (Session-per-Request): Each HTTP request gets its own
    database session that lives only for the duration of that request.
    This prevents issues with:
    1. Stale data: Sessions cache objects, so reusing sessions shows old data
    2. Thread safety: Sessions are not thread-safe, so sharing causes race conditions
    3. Transaction isolation: Each request should be an independent transaction
    The finally block ensures sessions are ALWAYS closed even on exceptions,
    preventing connection pool exhaustion (max connections = pool size).
    Without proper cleanup, we'd leak connections and eventually deadlock.
    """
    db = SessionLocal()
    try:
        # Yield session to the route handler
        yield db
    finally:
        # Always close the session, even if an exception occurred
        # This returns the connection to the pool for reuse
        db.close()


def get_db_with_rollback() -> Generator[Session, None, None]:
    """
    Dependency function with explicit rollback on error.

    Similar to get_db() but explicitly rolls back on exception.
    Use this for write operations that need guaranteed rollback.

    Yields:
        Session: SQLAlchemy database session

    Example:
        @app.post("/projects")
        def create_project(project: ProjectCreate, db: Session = Depends(get_db_with_rollback)):
            new_project = Project(**project.dict())
            db.add(new_project)
            db.commit()
            return new_project
    """
    db = SessionLocal()
    try:
        yield db
        # Commit if no exception occurred
        db.commit()
    except Exception:
        # Rollback on any exception
        db.rollback()
        raise
    finally:
        # Always close the session
        db.close()
