"""Database module for NOF1 Tracker.

This module provides database operations using SQLAlchemy ORM
with async support and PostgreSQL backend. It handles:
- Database connection management
- Model definitions for experiments and data
- CRUD operations with proper transaction handling

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
