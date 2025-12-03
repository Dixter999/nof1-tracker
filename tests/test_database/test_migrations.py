"""Tests for Alembic database migrations.

This module tests the Alembic migration configuration and execution:
- Configuration validation (alembic.ini settings)
- Migration execution (upgrade/downgrade)
- Schema verification (tables, enums, indexes, constraints)

All tests use the PostgreSQL test database with proper cleanup.
"""

import os

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from urllib.parse import quote_plus

# =============================================================================
# PostgreSQL Test Database Configuration
# =============================================================================

TEST_DB_HOST = os.getenv("DB_HOST", "10.0.0.4")
TEST_DB_PORT = os.getenv("DB_PORT", "5432")
TEST_DB_NAME = os.getenv("DB_NAME", "ai_model")
TEST_DB_USER = os.getenv("DB_USER", "ai_model")
TEST_DB_PASSWORD = os.getenv("DB_PASSWORD", "q#cCjmI5Tu3B")

TEST_DATABASE_URL = (
    f"postgresql://{TEST_DB_USER}:{quote_plus(TEST_DB_PASSWORD)}"
    f"@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(scope="module")
def alembic_config() -> Config:
    """Create Alembic config for testing.

    The URL is set via environment variables in env.py, not via set_main_option,
    to avoid configparser interpolation issues with special characters in passwords.

    Returns:
        Config: Alembic configuration object.
    """
    config = Config("alembic.ini")
    # Don't set sqlalchemy.url here - env.py reads from environment variables
    # This avoids configparser interpolation issues with % in URL-encoded passwords
    return config


@pytest.fixture(scope="module")
def migration_engine() -> Engine:
    """Create test database engine for migration tests.

    This fixture is separate from the conftest test_engine to avoid
    conflicts between ORM-managed tables and migration-managed tables.

    Returns:
        Engine: SQLAlchemy Engine connected to the test database.
    """
    return create_engine(TEST_DATABASE_URL)


@pytest.fixture(scope="module", autouse=True)
def clean_database(migration_engine: Engine) -> None:
    """Clean database before migration tests.

    Drops all existing tables to ensure clean slate for migration testing.
    This runs once per module before any tests.

    Args:
        migration_engine: Database engine for cleanup operations.
    """
    with migration_engine.connect() as conn:
        # Drop all tables if they exist
        conn.execute(text("DROP TABLE IF EXISTS model_chats CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS trades CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS leaderboard_snapshots CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS llm_models CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS seasons CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
        # Drop enum types if they exist
        conn.execute(text("DROP TYPE IF EXISTS seasonstatus CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS tradeside CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS tradestatus CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS chatdecision CASCADE"))
        conn.commit()


# =============================================================================
# Test Classes
# =============================================================================


class TestAlembicConfiguration:
    """Tests for Alembic configuration validation."""

    def test_alembic_ini_exists(self) -> None:
        """Verify alembic.ini configuration file exists."""
        assert os.path.exists("alembic.ini"), "alembic.ini not found at project root"

    def test_alembic_config_script_location(self, alembic_config: Config) -> None:
        """Verify script_location points to migrations directory."""
        script_location = alembic_config.get_main_option("script_location")
        assert script_location == "migrations"

    def test_alembic_env_py_exists(self) -> None:
        """Verify migrations/env.py exists."""
        assert os.path.exists("migrations/env.py"), "migrations/env.py not found"

    def test_alembic_script_template_exists(self) -> None:
        """Verify migrations/script.py.mako template exists."""
        assert os.path.exists(
            "migrations/script.py.mako"
        ), "migrations/script.py.mako not found"

    def test_alembic_versions_directory_exists(self) -> None:
        """Verify migrations/versions directory exists."""
        assert os.path.isdir(
            "migrations/versions"
        ), "migrations/versions directory not found"


class TestMigrationExecution:
    """Tests for migration upgrade execution."""

    def test_alembic_upgrade_head(self, alembic_config: Config) -> None:
        """Verify migration can be applied to head revision."""
        # This should complete without error
        command.upgrade(alembic_config, "head")

    def test_tables_created_after_upgrade(self, migration_engine: Engine) -> None:
        """Verify all expected tables exist after migration."""
        inspector = inspect(migration_engine)
        tables = inspector.get_table_names()

        expected_tables = [
            "seasons",
            "llm_models",
            "leaderboard_snapshots",
            "trades",
            "model_chats",
            "alembic_version",
        ]

        for table in expected_tables:
            assert table in tables, f"Table '{table}' not found after migration"

    def test_seasons_table_columns(self, migration_engine: Engine) -> None:
        """Verify seasons table has correct columns."""
        inspector = inspect(migration_engine)
        columns = {col["name"] for col in inspector.get_columns("seasons")}

        expected_columns = {
            "id",
            "season_number",
            "name",
            "start_date",
            "end_date",
            "initial_capital",
            "status",
            "created_at",
            "updated_at",
        }

        assert expected_columns.issubset(
            columns
        ), f"Missing columns in seasons: {expected_columns - columns}"

    def test_llm_models_table_columns(self, migration_engine: Engine) -> None:
        """Verify llm_models table has correct columns."""
        inspector = inspect(migration_engine)
        columns = {col["name"] for col in inspector.get_columns("llm_models")}

        expected_columns = {
            "id",
            "name",
            "provider",
            "model_id",
            "is_active",
            "created_at",
            "updated_at",
        }

        assert expected_columns.issubset(
            columns
        ), f"Missing columns in llm_models: {expected_columns - columns}"

    def test_leaderboard_snapshots_table_columns(
        self, migration_engine: Engine
    ) -> None:
        """Verify leaderboard_snapshots table has correct columns."""
        inspector = inspect(migration_engine)
        columns = {col["name"] for col in inspector.get_columns("leaderboard_snapshots")}

        expected_columns = {
            "id",
            "season_id",
            "model_id",
            "timestamp",
            "rank",
            "total_assets",
            "pnl",
            "pnl_percent",
            "roi",
            "win_rate",
            "total_trades",
            "raw_data",
            "created_at",
        }

        assert expected_columns.issubset(
            columns
        ), f"Missing columns in leaderboard_snapshots: {expected_columns - columns}"

    def test_trades_table_columns(self, migration_engine: Engine) -> None:
        """Verify trades table has correct columns."""
        inspector = inspect(migration_engine)
        columns = {col["name"] for col in inspector.get_columns("trades")}

        expected_columns = {
            "id",
            "model_id",
            "trade_id",
            "symbol",
            "side",
            "entry_price",
            "exit_price",
            "size",
            "leverage",
            "pnl",
            "pnl_percent",
            "status",
            "opened_at",
            "closed_at",
            "raw_data",
            "created_at",
        }

        assert expected_columns.issubset(
            columns
        ), f"Missing columns in trades: {expected_columns - columns}"

    def test_model_chats_table_columns(self, migration_engine: Engine) -> None:
        """Verify model_chats table has correct columns."""
        inspector = inspect(migration_engine)
        columns = {col["name"] for col in inspector.get_columns("model_chats")}

        expected_columns = {
            "id",
            "model_id",
            "timestamp",
            "content",
            "decision",
            "symbol",
            "confidence",
            "raw_data",
            "created_at",
        }

        assert expected_columns.issubset(
            columns
        ), f"Missing columns in model_chats: {expected_columns - columns}"


class TestForeignKeyConstraints:
    """Tests for foreign key relationships."""

    def test_leaderboard_snapshots_foreign_keys(
        self, migration_engine: Engine
    ) -> None:
        """Verify leaderboard_snapshots has correct foreign keys."""
        inspector = inspect(migration_engine)
        foreign_keys = inspector.get_foreign_keys("leaderboard_snapshots")

        fk_columns = {fk["constrained_columns"][0] for fk in foreign_keys}

        assert "season_id" in fk_columns, "Missing FK on season_id"
        assert "model_id" in fk_columns, "Missing FK on model_id"

    def test_trades_foreign_keys(self, migration_engine: Engine) -> None:
        """Verify trades table has correct foreign keys."""
        inspector = inspect(migration_engine)
        foreign_keys = inspector.get_foreign_keys("trades")

        fk_columns = {fk["constrained_columns"][0] for fk in foreign_keys}

        assert "model_id" in fk_columns, "Missing FK on model_id"

    def test_model_chats_foreign_keys(self, migration_engine: Engine) -> None:
        """Verify model_chats table has correct foreign keys."""
        inspector = inspect(migration_engine)
        foreign_keys = inspector.get_foreign_keys("model_chats")

        fk_columns = {fk["constrained_columns"][0] for fk in foreign_keys}

        assert "model_id" in fk_columns, "Missing FK on model_id"


class TestIndexes:
    """Tests for database indexes."""

    def test_leaderboard_snapshots_indexes(self, migration_engine: Engine) -> None:
        """Verify leaderboard_snapshots has expected indexes."""
        inspector = inspect(migration_engine)
        indexes = inspector.get_indexes("leaderboard_snapshots")
        index_names = [idx["name"] for idx in indexes]

        # Should have indexes on model_id and timestamp
        assert any(
            "model_id" in name.lower() for name in index_names
        ), "Missing index on model_id"
        assert any(
            "timestamp" in name.lower() for name in index_names
        ), "Missing index on timestamp"

    def test_trades_indexes(self, migration_engine: Engine) -> None:
        """Verify trades table has expected indexes."""
        inspector = inspect(migration_engine)
        indexes = inspector.get_indexes("trades")
        index_names = [idx["name"] for idx in indexes]

        assert any(
            "model_id" in name.lower() for name in index_names
        ), "Missing index on model_id"
        assert any(
            "symbol" in name.lower() for name in index_names
        ), "Missing index on symbol"
        assert any(
            "opened_at" in name.lower() for name in index_names
        ), "Missing index on opened_at"

    def test_model_chats_indexes(self, migration_engine: Engine) -> None:
        """Verify model_chats table has expected indexes."""
        inspector = inspect(migration_engine)
        indexes = inspector.get_indexes("model_chats")
        index_names = [idx["name"] for idx in indexes]

        assert any(
            "model_id" in name.lower() for name in index_names
        ), "Missing index on model_id"
        assert any(
            "timestamp" in name.lower() for name in index_names
        ), "Missing index on timestamp"


class TestUniqueConstraints:
    """Tests for unique constraints."""

    def test_seasons_unique_season_number(self, migration_engine: Engine) -> None:
        """Verify seasons table has unique constraint on season_number."""
        inspector = inspect(migration_engine)
        unique_constraints = inspector.get_unique_constraints("seasons")

        unique_columns = []
        for constraint in unique_constraints:
            unique_columns.extend(constraint["column_names"])

        assert (
            "season_number" in unique_columns
        ), "Missing unique constraint on season_number"

    def test_llm_models_unique_name(self, migration_engine: Engine) -> None:
        """Verify llm_models table has unique constraint on name."""
        inspector = inspect(migration_engine)
        unique_constraints = inspector.get_unique_constraints("llm_models")

        unique_columns = []
        for constraint in unique_constraints:
            unique_columns.extend(constraint["column_names"])

        assert "name" in unique_columns, "Missing unique constraint on name"

    def test_trades_unique_trade_id(self, migration_engine: Engine) -> None:
        """Verify trades table has unique constraint on trade_id."""
        inspector = inspect(migration_engine)
        unique_constraints = inspector.get_unique_constraints("trades")

        unique_columns = []
        for constraint in unique_constraints:
            unique_columns.extend(constraint["column_names"])

        assert "trade_id" in unique_columns, "Missing unique constraint on trade_id"

    def test_leaderboard_snapshots_unique_model_timestamp(
        self, migration_engine: Engine
    ) -> None:
        """Verify leaderboard_snapshots has unique constraint on model_id + timestamp."""
        inspector = inspect(migration_engine)
        unique_constraints = inspector.get_unique_constraints("leaderboard_snapshots")

        # Look for composite unique constraint
        for constraint in unique_constraints:
            cols = set(constraint["column_names"])
            if "model_id" in cols and "timestamp" in cols:
                return  # Found the composite constraint

        pytest.fail(
            "Missing unique constraint on (model_id, timestamp) in leaderboard_snapshots"
        )


class TestMigrationRollback:
    """Tests for migration rollback functionality."""

    def test_alembic_downgrade_base(
        self, alembic_config: Config, migration_engine: Engine
    ) -> None:
        """Verify migration can be rolled back to base."""
        # First ensure we're at head
        command.upgrade(alembic_config, "head")

        # Then downgrade to base
        command.downgrade(alembic_config, "base")

        # Verify tables are gone (except alembic_version which may persist)
        inspector = inspect(migration_engine)
        tables = inspector.get_table_names()

        assert "seasons" not in tables, "seasons table should be dropped"
        assert "llm_models" not in tables, "llm_models table should be dropped"
        assert "trades" not in tables, "trades table should be dropped"
        assert "model_chats" not in tables, "model_chats table should be dropped"
        assert (
            "leaderboard_snapshots" not in tables
        ), "leaderboard_snapshots table should be dropped"

    def test_alembic_upgrade_after_downgrade(
        self, alembic_config: Config, migration_engine: Engine
    ) -> None:
        """Verify migration can be re-applied after rollback."""
        # Start from base
        command.downgrade(alembic_config, "base")

        # Re-apply migration
        command.upgrade(alembic_config, "head")

        # Verify tables exist again
        inspector = inspect(migration_engine)
        tables = inspector.get_table_names()

        assert "seasons" in tables, "seasons table should exist after re-upgrade"
        assert "llm_models" in tables, "llm_models table should exist after re-upgrade"
