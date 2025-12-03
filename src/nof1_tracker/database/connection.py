"""Database connection manager for NOF1 Tracker.

Provides engine creation with connection pooling, session management
via context manager, and database initialization utilities.

This module uses environment variables for database configuration:
    DB_HOST: Database hostname (default: "10.0.0.4")
    DB_PORT: Database port (default: "5432")
    DB_NAME: Database name (default: "ai_model")
    DB_USER: Database user (default: "ai_model")
    DB_PASSWORD: Database password (default: "")

Functions:
    get_database_url: Build PostgreSQL connection URL from environment.
    create_db_engine: Create SQLAlchemy engine with connection pooling.
    get_engine: Get or create singleton database engine.
    get_session_maker: Get or create singleton session factory.
    get_session: Context manager for database sessions.
    init_db: Initialize database by creating all tables.
    reset_engine: Reset singleton engine and session maker.

Example:
    >>> from nof1_tracker.database.connection import get_session, init_db
    >>> init_db()
    >>> with get_session() as session:
    ...     result = session.execute(text("SELECT 1"))
    ...     print(result.scalar())
    1
"""

import os
from collections.abc import Generator
from contextlib import contextmanager
from urllib.parse import quote_plus

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from nof1_tracker.database.models import Base

# Module-level engine (singleton pattern)
_engine: Engine | None = None
_session_maker: sessionmaker[Session] | None = None


def get_database_url() -> str:
    """Build PostgreSQL connection URL from environment variables.

    Reads database connection parameters from environment variables and
    constructs a properly formatted PostgreSQL connection URL. The password
    is URL-encoded to handle special characters.

    Environment Variables:
        DB_HOST: Database hostname (default: "10.0.0.4")
        DB_PORT: Database port (default: "5432")
        DB_NAME: Database name (default: "ai_model")
        DB_USER: Database user (default: "ai_model")
        DB_PASSWORD: Database password (default: "")

    Returns:
        PostgreSQL connection URL in format:
        postgresql://user:password@host:port/dbname

    Example:
        >>> url = get_database_url()
        >>> url.startswith("postgresql://")
        True
    """
    host = os.getenv("DB_HOST", "10.0.0.4")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "ai_model")
    user = os.getenv("DB_USER", "ai_model")
    password = os.getenv("DB_PASSWORD", "")

    return f"postgresql://{user}:{quote_plus(password)}@{host}:{port}/{name}"


def create_db_engine(
    pool_size: int = 5,
    max_overflow: int = 10,
    pool_pre_ping: bool = True,
    pool_recycle: int = 3600,
) -> Engine:
    """Create SQLAlchemy engine with connection pooling.

    Creates a new SQLAlchemy Engine instance configured with connection pooling
    parameters. The engine uses the database URL from environment variables.

    Args:
        pool_size: Number of connections to maintain in the pool.
            Default: 5.
        max_overflow: Maximum additional connections beyond pool_size
            that can be created when the pool is exhausted. Default: 10.
        pool_pre_ping: If True, test connections before using them to detect
            stale connections. Default: True.
        pool_recycle: Number of seconds after which a connection is recycled.
            Helps prevent connection timeout issues. Default: 3600 (1 hour).

    Returns:
        Configured SQLAlchemy Engine instance.

    Example:
        >>> engine = create_db_engine(pool_size=3)
        >>> engine.pool.size()
        3
        >>> engine.dispose()
    """
    return create_engine(
        get_database_url(),
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=pool_pre_ping,
        pool_recycle=pool_recycle,
    )


def get_engine() -> Engine:
    """Get or create the singleton database engine.

    Returns the shared Engine instance, creating it if necessary. This
    ensures all parts of the application use the same connection pool.

    Returns:
        The shared Engine instance.

    Note:
        Use reset_engine() to clear the singleton if you need to
        reconfigure the connection parameters.

    Example:
        >>> engine1 = get_engine()
        >>> engine2 = get_engine()
        >>> engine1 is engine2
        True
    """
    global _engine
    if _engine is None:
        _engine = create_db_engine()
    return _engine


def get_session_maker() -> sessionmaker[Session]:
    """Get or create the session factory.

    Returns the shared sessionmaker instance, creating it if necessary.
    The sessionmaker is bound to the singleton engine.

    Returns:
        Configured sessionmaker bound to the engine.

    Example:
        >>> maker = get_session_maker()
        >>> session = maker()
        >>> session.close()
    """
    global _session_maker
    if _session_maker is None:
        _session_maker = sessionmaker(bind=get_engine())
    return _session_maker


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Context manager for database sessions.

    Provides automatic commit on success, rollback on exception,
    and session cleanup on exit. This is the recommended way to
    interact with the database.

    Yields:
        SQLAlchemy Session instance.

    Raises:
        Any exception raised within the context will trigger a rollback
        before being re-raised.

    Example:
        >>> with get_session() as session:
        ...     session.add(model)
        ...     # Auto-commits on exit, rolls back on exception
    """
    session = get_session_maker()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Initialize database by creating all tables.

    Uses the metadata from Base to create tables. Safe to call multiple
    times as it uses CREATE IF NOT EXISTS semantics.

    Example:
        >>> init_db()  # Creates all tables
        >>> init_db()  # Safe to call again
    """
    Base.metadata.create_all(get_engine())


def reset_engine() -> None:
    """Reset the singleton engine and session maker.

    Useful for testing or when connection parameters change.
    Disposes of existing connections before reset.

    Example:
        >>> engine1 = get_engine()
        >>> reset_engine()
        >>> engine2 = get_engine()
        >>> engine1 is not engine2
        True
    """
    global _engine, _session_maker
    if _engine is not None:
        _engine.dispose()
        _engine = None
    _session_maker = None
