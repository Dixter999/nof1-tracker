"""Add season_id to trades and model_chats tables.

Revision ID: 002
Revises: 001
Create Date: 2025-12-04

This migration:
    - Changes seasons.season_number from Integer to Numeric(5,1) to support decimal seasons (1.5)
    - Adds season_id foreign key to trades table
    - Adds season_id foreign key to model_chats table
    - Creates indexes for efficient season-based queries
    - Backfills existing data with Season 1.5
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# Revision identifiers used by Alembic
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply migration: add season support to trades and model_chats."""
    # =========================================================================
    # Step 1: Alter season_number column type from Integer to Numeric(5,1)
    # =========================================================================
    op.alter_column(
        "seasons",
        "season_number",
        existing_type=sa.Integer(),
        type_=sa.Numeric(precision=5, scale=1),
        existing_nullable=False,
    )

    # =========================================================================
    # Step 2: Ensure Season 1.5 exists for backfilling
    # =========================================================================
    # Insert Season 1.5 if it doesn't exist
    op.execute(
        """
        INSERT INTO seasons (season_number, name, start_date, status, created_at)
        SELECT 1.5, 'Season 1.5', NOW(), 'active', NOW()
        WHERE NOT EXISTS (SELECT 1 FROM seasons WHERE season_number = 1.5)
        """
    )

    # =========================================================================
    # Step 3: Add season_id column to trades (nullable first for backfill)
    # =========================================================================
    op.add_column(
        "trades",
        sa.Column("season_id", sa.Integer(), nullable=True),
    )

    # Backfill existing trades with Season 1.5
    op.execute(
        """
        UPDATE trades
        SET season_id = (SELECT id FROM seasons WHERE season_number = 1.5)
        WHERE season_id IS NULL
        """
    )

    # Make season_id NOT NULL after backfill
    op.alter_column(
        "trades",
        "season_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    # Add foreign key constraint
    op.create_foreign_key(
        "fk_trades_season_id",
        "trades",
        "seasons",
        ["season_id"],
        ["id"],
    )

    # Create index for season_id
    op.create_index("ix_trades_season_id", "trades", ["season_id"], unique=False)

    # =========================================================================
    # Step 4: Add season_id column to model_chats (nullable first for backfill)
    # =========================================================================
    op.add_column(
        "model_chats",
        sa.Column("season_id", sa.Integer(), nullable=True),
    )

    # Backfill existing chats with Season 1.5
    op.execute(
        """
        UPDATE model_chats
        SET season_id = (SELECT id FROM seasons WHERE season_number = 1.5)
        WHERE season_id IS NULL
        """
    )

    # Make season_id NOT NULL after backfill
    op.alter_column(
        "model_chats",
        "season_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    # Add foreign key constraint
    op.create_foreign_key(
        "fk_model_chats_season_id",
        "model_chats",
        "seasons",
        ["season_id"],
        ["id"],
    )

    # Create index for season_id
    op.create_index(
        "ix_model_chats_season_id", "model_chats", ["season_id"], unique=False
    )


def downgrade() -> None:
    """Rollback migration: remove season_id from trades and model_chats."""
    # Drop index and FK from model_chats
    op.drop_index("ix_model_chats_season_id", table_name="model_chats")
    op.drop_constraint("fk_model_chats_season_id", "model_chats", type_="foreignkey")
    op.drop_column("model_chats", "season_id")

    # Drop index and FK from trades
    op.drop_index("ix_trades_season_id", table_name="trades")
    op.drop_constraint("fk_trades_season_id", "trades", type_="foreignkey")
    op.drop_column("trades", "season_id")

    # Revert season_number back to Integer
    op.alter_column(
        "seasons",
        "season_number",
        existing_type=sa.Numeric(precision=5, scale=1),
        type_=sa.Integer(),
        existing_nullable=False,
    )
