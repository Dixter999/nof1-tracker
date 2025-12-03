"""Pytest configuration and fixtures for NOF1 Tracker tests.

This module provides centralized test fixtures for all test modules:

Database Fixtures:
    - test_engine: Session-scoped PostgreSQL engine
    - db_session: Function-scoped session with transaction rollback

Sample Data Factory Fixtures:
    - sample_season: Pre-configured Season instance
    - sample_llm_model: Pre-configured LLMModel instance
    - sample_leaderboard_snapshot: Pre-configured LeaderboardSnapshot instance
    - sample_trade: Pre-configured Trade instance
    - sample_model_chat: Pre-configured ModelChat instance

All fixtures use transaction rollback to ensure test isolation.
"""

import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Generator
from urllib.parse import quote_plus

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
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

# =============================================================================
# PostgreSQL Test Database Configuration
# =============================================================================
# Uses environment variables - configure via .env file or environment
# Supports both NOF1_DB_ prefix (preferred) and legacy DB_ prefix
# Password must be URL-encoded to handle special characters like #

TEST_DB_HOST = os.getenv("NOF1_DB_HOST", os.getenv("DB_HOST", "localhost"))
TEST_DB_PORT = os.getenv("NOF1_DB_PORT", os.getenv("DB_PORT", "5432"))
TEST_DB_NAME = os.getenv("NOF1_DB_NAME", os.getenv("DB_NAME", "nof1_tracker"))
TEST_DB_USER = os.getenv("NOF1_DB_USER", os.getenv("DB_USER", "nof1_user"))
TEST_DB_PASSWORD = os.getenv("NOF1_DB_PASSWORD", os.getenv("DB_PASSWORD", ""))

TEST_DATABASE_URL = (
    f"postgresql://{TEST_DB_USER}:{quote_plus(TEST_DB_PASSWORD)}"
    f"@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
)


# =============================================================================
# Database Connection Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def test_engine() -> Generator[Engine, None, None]:
    """Create PostgreSQL engine for testing (session-scoped).

    This fixture creates the database engine once per test session and
    ensures all tables are created before tests run.

    Yields:
        SQLAlchemy Engine connected to the test database.
    """
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    yield engine
    # Optional: Drop tables after session (commented for data inspection)
    # Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(test_engine: Engine) -> Generator[Session, None, None]:
    """Create database session with transaction rollback (function-scoped).

    Each test runs in a nested transaction that is rolled back after the test,
    ensuring complete test isolation without leaving data in the database.

    Args:
        test_engine: The session-scoped database engine.

    Yields:
        SQLAlchemy Session within a transaction.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    yield session

    session.close()
    # Only rollback if transaction is still active (not already rolled back by IntegrityError)
    if transaction.is_active:
        transaction.rollback()
    connection.close()


# =============================================================================
# Sample Data Factory Fixtures
# =============================================================================


@pytest.fixture
def sample_season(db_session: Session) -> Season:
    """Create a sample season for testing.

    Creates a Season with:
        - season_number: 1
        - name: "Test Season 1"
        - status: active
        - start_date: current UTC time

    Args:
        db_session: Database session fixture.

    Returns:
        Season: A persisted Season instance with assigned ID.
    """
    season = Season(
        season_number=1,
        name="Test Season 1",
        start_date=datetime.now(timezone.utc),
        status=SeasonStatus.active,
    )
    db_session.add(season)
    db_session.flush()
    return season


@pytest.fixture
def sample_llm_model(db_session: Session) -> LLMModel:
    """Create a sample LLM model for testing.

    Creates an LLMModel with:
        - name: "Test GPT-4"
        - provider: "OpenAI"
        - model_id: "gpt-4-test"
        - is_active: True (default)

    Args:
        db_session: Database session fixture.

    Returns:
        LLMModel: A persisted LLMModel instance with assigned ID.
    """
    model = LLMModel(
        name="Test GPT-4",
        provider="OpenAI",
        model_id="gpt-4-test",
    )
    db_session.add(model)
    db_session.flush()
    return model


@pytest.fixture
def sample_leaderboard_snapshot(
    db_session: Session, sample_season: Season, sample_llm_model: LLMModel
) -> LeaderboardSnapshot:
    """Create a sample leaderboard snapshot for testing.

    Creates a LeaderboardSnapshot with:
        - Links to sample_season and sample_llm_model
        - rank: 1
        - total_assets: 10000.00
        - pnl: 500.00
        - pnl_percent: 5.0000

    Args:
        db_session: Database session fixture.
        sample_season: Season fixture for foreign key.
        sample_llm_model: LLMModel fixture for foreign key.

    Returns:
        LeaderboardSnapshot: A persisted snapshot instance with relationships.
    """
    snapshot = LeaderboardSnapshot(
        season_id=sample_season.id,
        model_id=sample_llm_model.id,
        timestamp=datetime.now(timezone.utc),
        rank=1,
        total_assets=Decimal("10000.00"),
        pnl=Decimal("500.00"),
        pnl_percent=Decimal("5.0000"),
    )
    db_session.add(snapshot)
    db_session.flush()
    return snapshot


@pytest.fixture
def sample_trade(db_session: Session, sample_llm_model: LLMModel) -> Trade:
    """Create a sample trade for testing.

    Creates a Trade with:
        - Links to sample_llm_model
        - symbol: "BTCUSDT"
        - side: buy
        - entry_price: 50000.00000000
        - size: 0.10000000
        - status: open

    Args:
        db_session: Database session fixture.
        sample_llm_model: LLMModel fixture for foreign key.

    Returns:
        Trade: A persisted Trade instance with model relationship.
    """
    trade = Trade(
        model_id=sample_llm_model.id,
        trade_id="test-trade-001",
        symbol="BTCUSDT",
        side=TradeSide.buy,
        entry_price=Decimal("50000.00000000"),
        size=Decimal("0.10000000"),
        status=TradeStatus.open,
        opened_at=datetime.now(timezone.utc),
    )
    db_session.add(trade)
    db_session.flush()
    return trade


@pytest.fixture
def sample_model_chat(db_session: Session, sample_llm_model: LLMModel) -> ModelChat:
    """Create a sample model chat for testing.

    Creates a ModelChat with:
        - Links to sample_llm_model
        - decision: buy
        - symbol: "BTCUSDT"
        - confidence: 75.00
        - content: Market analysis text

    Args:
        db_session: Database session fixture.
        sample_llm_model: LLMModel fixture for foreign key.

    Returns:
        ModelChat: A persisted ModelChat instance with model relationship.
    """
    chat = ModelChat(
        model_id=sample_llm_model.id,
        timestamp=datetime.now(timezone.utc),
        content="Test analysis: Market conditions look bullish.",
        decision=ChatDecision.buy,
        symbol="BTCUSDT",
        confidence=Decimal("75.00"),
    )
    db_session.add(chat)
    db_session.flush()
    return chat
