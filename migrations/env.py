"""Alembic environment configuration for NOF1 Tracker.

This module configures the Alembic migration environment for PostgreSQL:
- Reads database credentials from environment variables
- URL-encodes passwords to handle special characters
- Imports model metadata for autogenerate support
- Configures offline and online migration modes

Environment Variables:
    DB_HOST: Database host (default: 10.0.0.4)
    DB_PORT: Database port (default: 5432)
    DB_NAME: Database name (default: ai_model)
    DB_USER: Database user (default: ai_model)
    DB_PASSWORD: Database password (no default for security)
"""

import os
from logging.config import fileConfig
from urllib.parse import quote_plus

from alembic import context
from sqlalchemy import engine_from_config, pool

# Import Base metadata from models for autogenerate support
from nof1_tracker.database.models import Base

# Alembic Config object for access to alembic.ini values
config = context.config

# Set up Python logging from alembic.ini [loggers] section
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Model metadata for autogenerate support
# Alembic will compare database schema against these models
target_metadata = Base.metadata


def get_database_url() -> str:
    """Build PostgreSQL database URL from environment variables.

    Password is URL-encoded to safely handle special characters like #, @, etc.

    Returns:
        str: PostgreSQL connection URL in SQLAlchemy format.

    Example:
        postgresql://ai_model:q%23cCjmI5Tu3B@10.0.0.4:5432/ai_model
    """
    user = os.getenv("DB_USER", "ai_model")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "10.0.0.4")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "ai_model")

    # URL-encode password to handle special characters safely
    encoded_password = quote_plus(password)

    return f"postgresql://{user}:{encoded_password}@{host}:{port}/{name}"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    In offline mode, Alembic generates SQL scripts without connecting to the
    database. This is useful for:
    - Reviewing migration SQL before execution
    - Generating migration scripts for manual application
    - CI/CD pipelines where database access is restricted

    The generated SQL uses literal values instead of bound parameters.
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In online mode, Alembic connects directly to the database and executes
    migrations in a transaction. This is the standard mode for:
    - Development environments
    - Production deployments
    - Automated testing

    Uses NullPool to disable connection pooling for migration operations.
    """
    # Get alembic configuration section
    configuration = config.get_section(config.config_ini_section) or {}

    # Override sqlalchemy.url with environment-based URL
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# Execute appropriate migration mode based on context
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
