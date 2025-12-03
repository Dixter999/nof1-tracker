"""Tests for pytest fixtures to ensure they work correctly.

This module tests the centralized fixtures in conftest.py:
- Database connection fixtures (test_engine, db_session)
- Sample data factory fixtures (sample_season, sample_llm_model, etc.)
- Fixture relationships and isolation guarantees
"""

import pytest
from sqlalchemy import text

from nof1_tracker.database.models import (
    ChatDecision,
    LeaderboardSnapshot,
    LLMModel,
    ModelChat,
    Season,
    SeasonStatus,
    Trade,
    TradeSide,
    TradeStatus,
)


class TestDatabaseFixtures:
    """Tests for database connection fixtures."""

    def test_db_session_creates_connection(self, db_session):
        """Verify db_session fixture provides working session."""
        assert db_session is not None
        # Session should be able to execute queries
        result = db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1

    def test_db_session_can_query_tables(self, db_session):
        """Verify db_session can query database tables."""
        # Query should work even if tables are empty
        result = db_session.query(LLMModel).all()
        assert isinstance(result, list)

    def test_db_session_isolation(self, db_session):
        """Verify changes in one test don't persist to others."""
        # Create a model with unique name
        model = LLMModel(
            name="Isolation Test Model",
            provider="Test",
            model_id="isolation-test",
        )
        db_session.add(model)
        db_session.flush()

        # Query should find it within this session
        found = db_session.query(LLMModel).filter_by(name="Isolation Test Model").first()
        assert found is not None

    def test_db_session_isolation_verify(self, db_session):
        """Verify the model from previous test was rolled back."""
        # This should NOT find the model from previous test
        found = db_session.query(LLMModel).filter_by(name="Isolation Test Model").first()
        assert found is None, "Previous test data should have been rolled back"


class TestSampleDataFixtures:
    """Tests for sample data factory fixtures."""

    def test_sample_season_created(self, sample_season):
        """Verify sample_season fixture creates valid season."""
        assert sample_season.id is not None
        assert sample_season.season_number == 1
        assert sample_season.name == "Test Season 1"
        assert sample_season.status == SeasonStatus.active

    def test_sample_season_has_start_date(self, sample_season):
        """Verify sample_season has a valid start date."""
        assert sample_season.start_date is not None

    def test_sample_llm_model_created(self, sample_llm_model):
        """Verify sample_llm_model fixture creates valid model."""
        assert sample_llm_model.id is not None
        assert sample_llm_model.name == "Test GPT-4"
        assert sample_llm_model.provider == "OpenAI"
        assert sample_llm_model.model_id == "gpt-4-test"

    def test_sample_llm_model_is_active(self, sample_llm_model):
        """Verify sample_llm_model is active by default."""
        assert sample_llm_model.is_active is True

    def test_sample_leaderboard_snapshot_created(self, sample_leaderboard_snapshot):
        """Verify snapshot fixture creates valid snapshot with relationships."""
        assert sample_leaderboard_snapshot.id is not None
        assert sample_leaderboard_snapshot.season_id is not None
        assert sample_leaderboard_snapshot.model_id is not None
        assert sample_leaderboard_snapshot.rank == 1

    def test_sample_leaderboard_snapshot_has_pnl(self, sample_leaderboard_snapshot):
        """Verify snapshot has PnL data."""
        from decimal import Decimal

        assert sample_leaderboard_snapshot.pnl is not None
        assert sample_leaderboard_snapshot.pnl_percent is not None
        assert sample_leaderboard_snapshot.total_assets == Decimal("10000.00")

    def test_sample_trade_created(self, sample_trade):
        """Verify sample_trade fixture creates valid trade."""
        assert sample_trade.id is not None
        assert sample_trade.symbol == "BTCUSDT"
        assert sample_trade.side == TradeSide.buy
        assert sample_trade.status == TradeStatus.open

    def test_sample_trade_has_entry_price(self, sample_trade):
        """Verify sample_trade has valid entry price and size."""
        from decimal import Decimal

        assert sample_trade.entry_price == Decimal("50000.00000000")
        assert sample_trade.size == Decimal("0.10000000")

    def test_sample_model_chat_created(self, sample_model_chat):
        """Verify sample_model_chat fixture creates valid chat."""
        assert sample_model_chat.id is not None
        assert sample_model_chat.content is not None
        assert sample_model_chat.decision == ChatDecision.buy

    def test_sample_model_chat_has_confidence(self, sample_model_chat):
        """Verify sample_model_chat has confidence value."""
        from decimal import Decimal

        assert sample_model_chat.symbol == "BTCUSDT"
        assert sample_model_chat.confidence == Decimal("75.00")


class TestFixtureRelationships:
    """Tests for fixture relationships."""

    def test_snapshot_has_season_relationship(
        self, sample_leaderboard_snapshot, sample_season
    ):
        """Verify snapshot can navigate to season."""
        assert sample_leaderboard_snapshot.season == sample_season
        assert sample_leaderboard_snapshot.season.season_number == 1

    def test_snapshot_has_model_relationship(
        self, sample_leaderboard_snapshot, sample_llm_model
    ):
        """Verify snapshot can navigate to model."""
        assert sample_leaderboard_snapshot.model == sample_llm_model
        assert sample_leaderboard_snapshot.model.name == "Test GPT-4"

    def test_trade_has_model_relationship(self, sample_trade, sample_llm_model):
        """Verify trade can navigate to model."""
        assert sample_trade.model == sample_llm_model
        assert sample_trade.model.provider == "OpenAI"

    def test_chat_has_model_relationship(self, sample_model_chat, sample_llm_model):
        """Verify chat can navigate to model."""
        assert sample_model_chat.model == sample_llm_model
        assert sample_model_chat.model.model_id == "gpt-4-test"

    def test_model_has_trades_relationship(self, sample_trade, sample_llm_model, db_session):
        """Verify model can navigate to trades."""
        db_session.refresh(sample_llm_model)
        assert len(sample_llm_model.trades) >= 1
        assert sample_trade in sample_llm_model.trades

    def test_model_has_chats_relationship(self, sample_model_chat, sample_llm_model, db_session):
        """Verify model can navigate to chats."""
        db_session.refresh(sample_llm_model)
        assert len(sample_llm_model.chats) >= 1
        assert sample_model_chat in sample_llm_model.chats


class TestFixtureIsolation:
    """Tests for fixture isolation between tests."""

    def test_fixtures_independent_first(self, sample_llm_model, db_session):
        """First test - modify model name."""
        original_name = sample_llm_model.name
        sample_llm_model.name = "Modified Name"
        db_session.flush()
        assert sample_llm_model.name == "Modified Name"
        # Store for verification (but not persisted)
        assert original_name == "Test GPT-4"

    def test_fixtures_independent_second(self, sample_llm_model):
        """Second test - verify model has original name (isolation)."""
        # If fixture isolation works, this should be a fresh fixture
        assert sample_llm_model.name == "Test GPT-4"
