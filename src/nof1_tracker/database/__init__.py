"""Database module for NOF1 Tracker.

This module provides database operations using SQLAlchemy ORM
with async support and PostgreSQL backend. It handles:
- Database connection management
- Model definitions for experiments and data
- CRUD operations with proper transaction handling

Connection Management:
    get_database_url: Build PostgreSQL connection URL from environment.
    create_db_engine: Create SQLAlchemy engine with connection pooling.
    get_engine: Get or create singleton database engine.
    get_session_maker: Get or create singleton session factory.
    get_session: Context manager for database sessions.
    init_db: Initialize database by creating all tables.
    reset_engine: Reset singleton engine and session maker.

Models:
    Season: Trading season periods
    LLMModel: AI model information
    LeaderboardSnapshot: Point-in-time performance data
    Trade: Individual trade records
    ModelChat: AI model chat/decision logs

Enums:
    SeasonStatus: Status of a trading season (active, completed, cancelled)
    TradeSide: Side of a trade (buy, sell)
    TradeStatus: Status of a trade (open, closed, cancelled)
    ChatDecision: Decision type from model chat (buy, sell, hold, none)
"""

from nof1_tracker.database.config import db_settings
from nof1_tracker.database.connection import (
    create_db_engine,
    get_database_url,
    get_engine,
    get_session,
    get_session_maker,
    init_db,
    reset_engine,
)
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

__all__ = [
    # Configuration
    "db_settings",
    # Connection Management
    "get_database_url",
    "create_db_engine",
    "get_engine",
    "get_session_maker",
    "get_session",
    "init_db",
    "reset_engine",
    # Base class
    "Base",
    # Models
    "Season",
    "LLMModel",
    "LeaderboardSnapshot",
    "Trade",
    "ModelChat",
    # Enums
    "SeasonStatus",
    "TradeSide",
    "TradeStatus",
    "ChatDecision",
]
