"""Tests for database connection manager.

This module tests the database connection utilities including:
- Database URL generation from environment variables
- Engine creation with connection pooling
- Singleton engine pattern
- Session management with context manager
- Database initialization
"""

from sqlalchemy import text
from sqlalchemy.orm import Session

from nof1_tracker.database.connection import (
    create_db_engine,
    get_database_url,
    get_engine,
    get_session,
    get_session_maker,
    init_db,
    reset_engine,
)
from nof1_tracker.database.models import LLMModel


class TestDatabaseUrl:
    """Tests for database URL generation."""

    def test_get_database_url_returns_postgresql_url(self):
        """Verify URL starts with postgresql://."""
        url = get_database_url()
        assert url.startswith("postgresql://")

    def test_get_database_url_contains_host(self):
        """Verify URL contains the database host."""
        url = get_database_url()
        # Should contain the host from environment or default
        assert "10.0.0.4" in url or "localhost" in url


class TestEngineCreation:
    """Tests for engine creation."""

    def test_create_db_engine_returns_engine(self):
        """Verify create_db_engine returns an Engine."""
        engine = create_db_engine()
        assert engine is not None
        engine.dispose()

    def test_create_db_engine_with_custom_pool_size(self):
        """Verify custom pool_size is applied."""
        engine = create_db_engine(pool_size=3)
        assert engine.pool.size() == 3
        engine.dispose()

    def test_create_db_engine_can_connect(self):
        """Verify engine can establish connection."""
        engine = create_db_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
        engine.dispose()


class TestEngineSingleton:
    """Tests for engine singleton pattern."""

    def setup_method(self):
        """Reset engine before each test."""
        reset_engine()

    def teardown_method(self):
        """Clean up after each test."""
        reset_engine()

    def test_get_engine_returns_same_instance(self):
        """Verify get_engine returns singleton."""
        engine1 = get_engine()
        engine2 = get_engine()
        assert engine1 is engine2

    def test_reset_engine_clears_singleton(self):
        """Verify reset_engine creates new instance."""
        engine1 = get_engine()
        reset_engine()
        engine2 = get_engine()
        assert engine1 is not engine2


class TestSessionMaker:
    """Tests for session maker."""

    def setup_method(self):
        """Reset engine before each test."""
        reset_engine()

    def teardown_method(self):
        """Clean up after each test."""
        reset_engine()

    def test_get_session_maker_returns_sessionmaker(self):
        """Verify get_session_maker returns a sessionmaker."""
        maker = get_session_maker()
        assert maker is not None

    def test_get_session_maker_returns_same_instance(self):
        """Verify session maker is singleton."""
        maker1 = get_session_maker()
        maker2 = get_session_maker()
        assert maker1 is maker2


class TestSessionContextManager:
    """Tests for session context manager."""

    def setup_method(self):
        """Reset engine and initialize database before each test."""
        reset_engine()
        init_db()

    def teardown_method(self):
        """Clean up after each test."""
        reset_engine()

    def test_get_session_provides_session(self):
        """Verify get_session yields a Session."""
        with get_session() as session:
            assert isinstance(session, Session)

    def test_get_session_can_execute_query(self):
        """Verify session can execute queries."""
        with get_session() as session:
            result = session.execute(text("SELECT 1"))
            assert result.scalar() == 1

    def test_get_session_auto_commits(self):
        """Verify session auto-commits on success."""
        # Create a model in one session
        with get_session() as session:
            model = LLMModel(
                name="AutoCommit Test",
                provider="Test",
                model_id="auto-commit-test",
            )
            session.add(model)

        # Verify it persists in another session
        with get_session() as session:
            found = session.query(LLMModel).filter_by(name="AutoCommit Test").first()
            assert found is not None
            # Cleanup
            session.delete(found)

    def test_get_session_rollback_on_exception(self):
        """Verify session rolls back on exception."""
        try:
            with get_session() as session:
                model = LLMModel(
                    name="Rollback Test",
                    provider="Test",
                    model_id="rollback-test",
                )
                session.add(model)
                session.flush()  # Force insert
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Verify it was rolled back
        with get_session() as session:
            found = session.query(LLMModel).filter_by(name="Rollback Test").first()
            assert found is None


class TestInitDb:
    """Tests for database initialization."""

    def setup_method(self):
        """Reset engine before each test."""
        reset_engine()

    def teardown_method(self):
        """Clean up after each test."""
        reset_engine()

    def test_init_db_creates_tables(self):
        """Verify init_db creates all tables."""
        init_db()

        engine = get_engine()
        from sqlalchemy import inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        assert "seasons" in tables
        assert "llm_models" in tables
        assert "leaderboard_snapshots" in tables
        assert "trades" in tables
        assert "model_chats" in tables

    def test_init_db_is_idempotent(self):
        """Verify init_db can be called multiple times."""
        init_db()
        init_db()  # Should not raise
