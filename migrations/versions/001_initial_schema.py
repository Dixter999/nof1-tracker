"""Initial schema for NOF1 Tracker.

Revision ID: 001
Revises: None
Create Date: 2025-12-03

This migration creates the complete initial database schema for NOF1 Tracker:

Tables:
    - seasons: Trading season periods with status tracking
    - llm_models: AI/LLM model information and metadata
    - leaderboard_snapshots: Point-in-time performance data
    - trades: Individual trade records with P&L tracking
    - model_chats: AI model chat/decision logs

Note: Enum values are stored as VARCHAR (native_enum=False in models) for
compatibility and easier migration. PostgreSQL native enums are not used.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# Revision identifiers used by Alembic
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply migration: create all tables for NOF1 Tracker."""
    # =========================================================================
    # Create seasons table
    # =========================================================================
    op.create_table(
        "seasons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("season_number", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=True),
        sa.Column(
            "initial_capital",
            sa.Numeric(precision=15, scale=2),
            nullable=True,
            server_default="10000.00",
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=True,
            server_default="active",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("season_number", name="uq_seasons_season_number"),
    )

    # =========================================================================
    # Create llm_models table
    # =========================================================================
    op.create_table(
        "llm_models",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("model_id", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("name", name="uq_llm_models_name"),
    )

    # =========================================================================
    # Create leaderboard_snapshots table
    # =========================================================================
    op.create_table(
        "leaderboard_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("season_id", sa.Integer(), nullable=False),
        sa.Column("model_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("total_assets", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("pnl", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("pnl_percent", sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column("roi", sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column("win_rate", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("total_trades", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["season_id"],
            ["seasons.id"],
            name="fk_leaderboard_snapshots_season_id",
        ),
        sa.ForeignKeyConstraint(
            ["model_id"],
            ["llm_models.id"],
            name="fk_leaderboard_snapshots_model_id",
        ),
        sa.UniqueConstraint("model_id", "timestamp", name="uix_model_timestamp"),
    )

    # Create indexes for leaderboard_snapshots
    op.create_index(
        "ix_leaderboard_model_id",
        "leaderboard_snapshots",
        ["model_id"],
        unique=False,
    )
    op.create_index(
        "ix_leaderboard_timestamp",
        "leaderboard_snapshots",
        ["timestamp"],
        unique=False,
    )

    # =========================================================================
    # Create trades table
    # =========================================================================
    op.create_table(
        "trades",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("model_id", sa.Integer(), nullable=False),
        sa.Column("trade_id", sa.String(length=100), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("side", sa.String(length=10), nullable=False),
        sa.Column("entry_price", sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column("exit_price", sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column("size", sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column("leverage", sa.Integer(), nullable=True, server_default="1"),
        sa.Column("pnl", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("pnl_percent", sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("opened_at", sa.DateTime(), nullable=False),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["model_id"],
            ["llm_models.id"],
            name="fk_trades_model_id",
        ),
        sa.UniqueConstraint("trade_id", name="uq_trades_trade_id"),
    )

    # Create indexes for trades
    op.create_index("ix_trades_model_id", "trades", ["model_id"], unique=False)
    op.create_index("ix_trades_symbol", "trades", ["symbol"], unique=False)
    op.create_index("ix_trades_opened_at", "trades", ["opened_at"], unique=False)

    # =========================================================================
    # Create model_chats table
    # =========================================================================
    op.create_table(
        "model_chats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("model_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("decision", sa.String(length=10), nullable=True),
        sa.Column("symbol", sa.String(length=20), nullable=True),
        sa.Column("confidence", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["model_id"],
            ["llm_models.id"],
            name="fk_model_chats_model_id",
        ),
    )

    # Create indexes for model_chats
    op.create_index(
        "ix_model_chats_model_id", "model_chats", ["model_id"], unique=False
    )
    op.create_index(
        "ix_model_chats_timestamp", "model_chats", ["timestamp"], unique=False
    )


def downgrade() -> None:
    """Rollback migration: drop all tables in reverse order."""
    # Drop tables in reverse order to respect foreign key dependencies
    op.drop_index("ix_model_chats_timestamp", table_name="model_chats")
    op.drop_index("ix_model_chats_model_id", table_name="model_chats")
    op.drop_table("model_chats")

    op.drop_index("ix_trades_opened_at", table_name="trades")
    op.drop_index("ix_trades_symbol", table_name="trades")
    op.drop_index("ix_trades_model_id", table_name="trades")
    op.drop_table("trades")

    op.drop_index("ix_leaderboard_timestamp", table_name="leaderboard_snapshots")
    op.drop_index("ix_leaderboard_model_id", table_name="leaderboard_snapshots")
    op.drop_table("leaderboard_snapshots")

    op.drop_table("llm_models")
    op.drop_table("seasons")
