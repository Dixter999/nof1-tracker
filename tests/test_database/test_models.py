"""Tests for SQLAlchemy ORM models.

This module tests all database models for NOF1 Tracker:
- Season: Trading season tracking
- LLMModel: AI model information
- LeaderboardSnapshot: Point-in-time performance data
- Trade: Individual trade records
- ModelChat: AI model chat/decision logs
"""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from nof1_tracker.database.models import (
    Base,
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


@pytest.fixture
def engine():
    """Create in-memory SQLite engine for testing."""
    return create_engine("sqlite:///:memory:")


@pytest.fixture
def session(engine) -> Session:
    """Create database session with all tables.

    Yields:
        SQLAlchemy session with all tables created.
    """
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestSeasonModel:
    """Tests for Season model."""

    def test_season_creation(self, session: Session) -> None:
        """Create season with all required fields, verify defaults."""
        start_date = datetime.utcnow()
        season = Season(
            season_number=1,
            name="Season 1",
            start_date=start_date,
        )
        session.add(season)
        session.commit()
        session.refresh(season)

        assert season.id is not None
        assert season.season_number == 1
        assert season.name == "Season 1"
        assert season.start_date == start_date
        assert season.end_date is None
        assert season.initial_capital == Decimal("10000.00")
        assert season.status == SeasonStatus.active
        assert season.created_at is not None
        # Note: updated_at may be None until first update

    def test_season_status_enum(self, session: Session) -> None:
        """Test all SeasonStatus enum values can be stored and retrieved."""
        for i, status in enumerate(SeasonStatus):
            season = Season(
                season_number=100 + i,
                name=f"Season {100 + i}",
                start_date=datetime.utcnow(),
                status=status,
            )
            session.add(season)
            session.commit()
            session.refresh(season)

            assert season.status == status
            assert season.status.value == status.value


class TestLLMModelModel:
    """Tests for LLMModel model."""

    def test_llm_model_creation(self, session: Session) -> None:
        """Create model with provider and model_id."""
        model = LLMModel(
            name="GPT-4 Turbo",
            provider="OpenAI",
            model_id="gpt-4-turbo",
        )
        session.add(model)
        session.commit()
        session.refresh(model)

        assert model.id is not None
        assert model.name == "GPT-4 Turbo"
        assert model.provider == "OpenAI"
        assert model.model_id == "gpt-4-turbo"
        assert model.is_active is True
        assert model.created_at is not None

    def test_llm_model_unique_name(self, session: Session) -> None:
        """Verify name uniqueness constraint."""
        model1 = LLMModel(
            name="GPT-4",
            provider="OpenAI",
            model_id="gpt-4",
        )
        session.add(model1)
        session.commit()

        model2 = LLMModel(
            name="GPT-4",  # Duplicate name
            provider="OpenAI",
            model_id="gpt-4-different",
        )
        session.add(model2)

        with pytest.raises(IntegrityError):
            session.commit()


class TestLeaderboardSnapshotModel:
    """Tests for LeaderboardSnapshot model."""

    def test_leaderboard_snapshot_creation(self, session: Session) -> None:
        """Create snapshot with season and model FKs."""
        # Create prerequisite records
        season = Season(
            season_number=1,
            name="Season 1",
            start_date=datetime.utcnow(),
        )
        model = LLMModel(
            name="Claude 3",
            provider="Anthropic",
            model_id="claude-3-opus",
        )
        session.add_all([season, model])
        session.commit()

        timestamp = datetime.utcnow()
        snapshot = LeaderboardSnapshot(
            season_id=season.id,
            model_id=model.id,
            timestamp=timestamp,
            rank=1,
            total_assets=Decimal("12500.50"),
            pnl=Decimal("2500.50"),
            pnl_percent=Decimal("25.0050"),
            roi=Decimal("25.0050"),
            win_rate=Decimal("65.50"),
            total_trades=42,
        )
        session.add(snapshot)
        session.commit()
        session.refresh(snapshot)

        assert snapshot.id is not None
        assert snapshot.season_id == season.id
        assert snapshot.model_id == model.id
        assert snapshot.timestamp == timestamp
        assert snapshot.rank == 1
        assert snapshot.total_assets == Decimal("12500.50")
        assert snapshot.pnl == Decimal("2500.50")
        assert snapshot.pnl_percent == Decimal("25.0050")
        assert snapshot.roi == Decimal("25.0050")
        assert snapshot.win_rate == Decimal("65.50")
        assert snapshot.total_trades == 42
        assert snapshot.created_at is not None

    def test_leaderboard_snapshot_unique_constraint(self, session: Session) -> None:
        """Same model+timestamp should fail uniqueness constraint."""
        season = Season(
            season_number=1,
            name="Season 1",
            start_date=datetime.utcnow(),
        )
        model = LLMModel(
            name="Claude 3",
            provider="Anthropic",
            model_id="claude-3-opus",
        )
        session.add_all([season, model])
        session.commit()

        timestamp = datetime.utcnow()

        snapshot1 = LeaderboardSnapshot(
            season_id=season.id,
            model_id=model.id,
            timestamp=timestamp,
            rank=1,
            total_assets=Decimal("10000.00"),
            pnl=Decimal("0.00"),
            pnl_percent=Decimal("0.0000"),
        )
        session.add(snapshot1)
        session.commit()

        snapshot2 = LeaderboardSnapshot(
            season_id=season.id,
            model_id=model.id,
            timestamp=timestamp,  # Same timestamp for same model
            rank=2,
            total_assets=Decimal("11000.00"),
            pnl=Decimal("1000.00"),
            pnl_percent=Decimal("10.0000"),
        )
        session.add(snapshot2)

        with pytest.raises(IntegrityError):
            session.commit()


class TestTradeModel:
    """Tests for Trade model."""

    def test_trade_creation(self, session: Session) -> None:
        """Create trade with all enums and fields."""
        model = LLMModel(
            name="GPT-4",
            provider="OpenAI",
            model_id="gpt-4",
        )
        session.add(model)
        session.commit()

        opened_at = datetime.utcnow()
        closed_at = opened_at + timedelta(hours=2)

        trade = Trade(
            model_id=model.id,
            trade_id="ext-trade-12345",
            symbol="BTCUSDT",
            side=TradeSide.buy,
            entry_price=Decimal("45000.12345678"),
            exit_price=Decimal("46000.87654321"),
            size=Decimal("0.5"),
            leverage=10,
            pnl=Decimal("500.38"),
            pnl_percent=Decimal("2.2239"),
            status=TradeStatus.closed,
            opened_at=opened_at,
            closed_at=closed_at,
        )
        session.add(trade)
        session.commit()
        session.refresh(trade)

        assert trade.id is not None
        assert trade.model_id == model.id
        assert trade.trade_id == "ext-trade-12345"
        assert trade.symbol == "BTCUSDT"
        assert trade.side == TradeSide.buy
        assert trade.entry_price == Decimal("45000.12345678")
        assert trade.exit_price == Decimal("46000.87654321")
        assert trade.size == Decimal("0.5")
        assert trade.leverage == 10
        assert trade.pnl == Decimal("500.38")
        assert trade.pnl_percent == Decimal("2.2239")
        assert trade.status == TradeStatus.closed
        assert trade.opened_at == opened_at
        assert trade.closed_at == closed_at
        assert trade.created_at is not None

    def test_trade_side_enum(self, session: Session) -> None:
        """Test TradeSide enum values can be stored and retrieved."""
        model = LLMModel(
            name="Claude 3",
            provider="Anthropic",
            model_id="claude-3",
        )
        session.add(model)
        session.commit()

        for i, side in enumerate(TradeSide):
            trade = Trade(
                model_id=model.id,
                trade_id=f"side-test-{i}",
                symbol="ETHUSDT",
                side=side,
                entry_price=Decimal("3000.00"),
                size=Decimal("1.0"),
                status=TradeStatus.open,
                opened_at=datetime.utcnow(),
            )
            session.add(trade)
            session.commit()
            session.refresh(trade)

            assert trade.side == side

    def test_trade_status_enum(self, session: Session) -> None:
        """Test TradeStatus enum values can be stored and retrieved."""
        model = LLMModel(
            name="Gemini Pro",
            provider="Google",
            model_id="gemini-pro",
        )
        session.add(model)
        session.commit()

        for i, status in enumerate(TradeStatus):
            trade = Trade(
                model_id=model.id,
                trade_id=f"status-test-{i}",
                symbol="SOLUSDT",
                side=TradeSide.buy,
                entry_price=Decimal("100.00"),
                size=Decimal("5.0"),
                status=status,
                opened_at=datetime.utcnow(),
            )
            session.add(trade)
            session.commit()
            session.refresh(trade)

            assert trade.status == status


class TestModelChatModel:
    """Tests for ModelChat model."""

    def test_model_chat_creation(self, session: Session) -> None:
        """Create chat with decision enum."""
        model = LLMModel(
            name="Claude 3 Sonnet",
            provider="Anthropic",
            model_id="claude-3-sonnet",
        )
        session.add(model)
        session.commit()

        timestamp = datetime.utcnow()
        chat = ModelChat(
            model_id=model.id,
            timestamp=timestamp,
            content="Based on technical analysis, I recommend buying BTC.",
            decision=ChatDecision.buy,
            symbol="BTCUSDT",
            confidence=Decimal("85.50"),
        )
        session.add(chat)
        session.commit()
        session.refresh(chat)

        assert chat.id is not None
        assert chat.model_id == model.id
        assert chat.timestamp == timestamp
        assert chat.content == "Based on technical analysis, I recommend buying BTC."
        assert chat.decision == ChatDecision.buy
        assert chat.symbol == "BTCUSDT"
        assert chat.confidence == Decimal("85.50")
        assert chat.created_at is not None


class TestModelRelationships:
    """Tests for model relationships."""

    def test_model_relationships(self, session: Session) -> None:
        """Verify navigation from LLMModel to related records."""
        # Create model
        model = LLMModel(
            name="GPT-4",
            provider="OpenAI",
            model_id="gpt-4",
        )
        session.add(model)
        session.commit()

        # Create season
        season = Season(
            season_number=1,
            name="Season 1",
            start_date=datetime.utcnow(),
        )
        session.add(season)
        session.commit()

        # Create related records
        snapshot = LeaderboardSnapshot(
            season_id=season.id,
            model_id=model.id,
            timestamp=datetime.utcnow(),
            rank=1,
            total_assets=Decimal("10000.00"),
            pnl=Decimal("0.00"),
            pnl_percent=Decimal("0.0000"),
        )
        trade = Trade(
            model_id=model.id,
            trade_id="rel-test-1",
            symbol="BTCUSDT",
            side=TradeSide.buy,
            entry_price=Decimal("50000.00"),
            size=Decimal("0.1"),
            status=TradeStatus.open,
            opened_at=datetime.utcnow(),
        )
        chat = ModelChat(
            model_id=model.id,
            timestamp=datetime.utcnow(),
            content="Test chat message",
            decision=ChatDecision.hold,
        )
        session.add_all([snapshot, trade, chat])
        session.commit()

        # Refresh model to get relationships
        session.refresh(model)

        # Verify relationships
        assert len(model.snapshots) == 1
        assert model.snapshots[0].rank == 1

        assert len(model.trades) == 1
        assert model.trades[0].symbol == "BTCUSDT"

        assert len(model.chats) == 1
        assert model.chats[0].decision == ChatDecision.hold

        # Verify back-references
        assert snapshot.model.name == "GPT-4"
        assert trade.model.provider == "OpenAI"
        assert chat.model.model_id == "gpt-4"


class TestJSONBField:
    """Tests for JSONB field storage."""

    def test_jsonb_field_storage(self, session: Session) -> None:
        """Store and retrieve dict in raw_data field."""
        model = LLMModel(
            name="Claude 3",
            provider="Anthropic",
            model_id="claude-3",
        )
        season = Season(
            season_number=1,
            name="Season 1",
            start_date=datetime.utcnow(),
        )
        session.add_all([model, season])
        session.commit()

        # Test JSONB in LeaderboardSnapshot
        raw_data = {
            "source": "alpha_arena",
            "scraped_at": "2024-01-15T10:30:00Z",
            "additional_metrics": {
                "sharpe_ratio": 1.5,
                "max_drawdown": 0.15,
            },
        }
        snapshot = LeaderboardSnapshot(
            season_id=season.id,
            model_id=model.id,
            timestamp=datetime.utcnow(),
            rank=1,
            total_assets=Decimal("10000.00"),
            pnl=Decimal("0.00"),
            pnl_percent=Decimal("0.0000"),
            raw_data=raw_data,
        )
        session.add(snapshot)
        session.commit()
        session.refresh(snapshot)

        assert snapshot.raw_data == raw_data
        assert snapshot.raw_data["source"] == "alpha_arena"
        assert snapshot.raw_data["additional_metrics"]["sharpe_ratio"] == 1.5

        # Test JSONB in Trade
        trade_raw_data = {"order_id": "12345", "exchange": "binance"}
        trade = Trade(
            model_id=model.id,
            trade_id="json-test-1",
            symbol="BTCUSDT",
            side=TradeSide.buy,
            entry_price=Decimal("50000.00"),
            size=Decimal("0.1"),
            status=TradeStatus.open,
            opened_at=datetime.utcnow(),
            raw_data=trade_raw_data,
        )
        session.add(trade)
        session.commit()
        session.refresh(trade)

        assert trade.raw_data == trade_raw_data

        # Test JSONB in ModelChat
        chat_raw_data = {"message_id": "msg-123", "tokens": 150}
        chat = ModelChat(
            model_id=model.id,
            timestamp=datetime.utcnow(),
            content="Test message",
            raw_data=chat_raw_data,
        )
        session.add(chat)
        session.commit()
        session.refresh(chat)

        assert chat.raw_data == chat_raw_data


class TestTimestamps:
    """Tests for automatic timestamp population."""

    def test_timestamps_auto_populate(self, session: Session) -> None:
        """Verify created_at auto-populates on insert."""
        before_insert = datetime.utcnow()

        model = LLMModel(
            name="Claude 3",
            provider="Anthropic",
            model_id="claude-3",
        )
        session.add(model)
        session.commit()
        session.refresh(model)

        after_insert = datetime.utcnow()

        assert model.created_at is not None
        assert before_insert <= model.created_at <= after_insert

        # Test Season timestamps
        season = Season(
            season_number=1,
            name="Season 1",
            start_date=datetime.utcnow(),
        )
        session.add(season)
        session.commit()
        session.refresh(season)

        assert season.created_at is not None


class TestReprMethods:
    """Tests for __repr__ methods."""

    def test_repr_methods(self, session: Session) -> None:
        """Verify __repr__ returns useful strings."""
        # Test Season repr
        season = Season(
            season_number=1,
            name="Season Alpha",
            start_date=datetime.utcnow(),
        )
        session.add(season)
        session.commit()
        session.refresh(season)

        season_repr = repr(season)
        assert "Season" in season_repr
        assert "1" in season_repr or "Alpha" in season_repr

        # Test LLMModel repr
        model = LLMModel(
            name="GPT-4 Turbo",
            provider="OpenAI",
            model_id="gpt-4-turbo",
        )
        session.add(model)
        session.commit()
        session.refresh(model)

        model_repr = repr(model)
        assert "LLMModel" in model_repr
        assert "GPT-4 Turbo" in model_repr

        # Test Trade repr
        trade = Trade(
            model_id=model.id,
            trade_id="repr-test",
            symbol="BTCUSDT",
            side=TradeSide.buy,
            entry_price=Decimal("50000.00"),
            size=Decimal("0.1"),
            status=TradeStatus.open,
            opened_at=datetime.utcnow(),
        )
        session.add(trade)
        session.commit()
        session.refresh(trade)

        trade_repr = repr(trade)
        assert "Trade" in trade_repr
        assert "BTCUSDT" in trade_repr

        # Test LeaderboardSnapshot repr
        snapshot = LeaderboardSnapshot(
            season_id=season.id,
            model_id=model.id,
            timestamp=datetime.utcnow(),
            rank=5,
            total_assets=Decimal("10000.00"),
            pnl=Decimal("0.00"),
            pnl_percent=Decimal("0.0000"),
        )
        session.add(snapshot)
        session.commit()
        session.refresh(snapshot)

        snapshot_repr = repr(snapshot)
        assert "LeaderboardSnapshot" in snapshot_repr
        assert "5" in snapshot_repr  # rank

        # Test ModelChat repr
        chat = ModelChat(
            model_id=model.id,
            timestamp=datetime.utcnow(),
            content="Test message for repr",
        )
        session.add(chat)
        session.commit()
        session.refresh(chat)

        chat_repr = repr(chat)
        assert "ModelChat" in chat_repr
