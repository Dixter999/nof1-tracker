"""SQLAlchemy ORM models for NOF1 Tracker.

This module defines the database models for tracking Alpha Arena trading data:
- Season: Trading season periods
- LLMModel: AI model information
- LeaderboardSnapshot: Point-in-time performance data
- Trade: Individual trade records
- ModelChat: AI model chat/decision logs

All models use SQLAlchemy 2.0 style with Mapped type annotations.
"""

import enum
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Use JSONB for PostgreSQL, fall back to JSON for other databases (e.g., SQLite)
JSONType = JSON().with_variant(JSONB(), "postgresql")


class SeasonStatus(str, enum.Enum):
    """Status of a trading season."""

    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class TradeSide(str, enum.Enum):
    """Side of a trade (buy or sell)."""

    buy = "buy"
    sell = "sell"


class TradeStatus(str, enum.Enum):
    """Status of a trade."""

    open = "open"
    closed = "closed"
    cancelled = "cancelled"


class ChatDecision(str, enum.Enum):
    """Decision type from model chat."""

    buy = "buy"
    sell = "sell"
    hold = "hold"
    none = "none"


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class Season(Base):
    """Trading season model."""

    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    initial_capital: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("10000.00")
    )
    status: Mapped[SeasonStatus] = mapped_column(
        Enum(SeasonStatus, create_constraint=False, native_enum=False),
        default=SeasonStatus.active,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    snapshots: Mapped[list["LeaderboardSnapshot"]] = relationship(
        "LeaderboardSnapshot", back_populates="season"
    )

    def __repr__(self) -> str:
        """Return string representation of Season."""
        return f"<Season(id={self.id}, season_number={self.season_number}, name='{self.name}')>"


class LLMModel(Base):
    """AI/LLM model information."""

    __tablename__ = "llm_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model_id: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    snapshots: Mapped[list["LeaderboardSnapshot"]] = relationship(
        "LeaderboardSnapshot", back_populates="model"
    )
    trades: Mapped[list["Trade"]] = relationship("Trade", back_populates="model")
    chats: Mapped[list["ModelChat"]] = relationship("ModelChat", back_populates="model")

    def __repr__(self) -> str:
        """Return string representation of LLMModel."""
        return f"<LLMModel(id={self.id}, name='{self.name}', provider='{self.provider}')>"


class LeaderboardSnapshot(Base):
    """Point-in-time leaderboard snapshot."""

    __tablename__ = "leaderboard_snapshots"
    __table_args__ = (
        UniqueConstraint("model_id", "timestamp", name="uix_model_timestamp"),
        Index("ix_leaderboard_model_id", "model_id"),
        Index("ix_leaderboard_timestamp", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("seasons.id"), nullable=False
    )
    model_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("llm_models.id"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    total_assets: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    pnl: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    pnl_percent: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    roi: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    win_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    total_trades: Mapped[int] = mapped_column(Integer, default=0)
    raw_data: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    season: Mapped["Season"] = relationship("Season", back_populates="snapshots")
    model: Mapped["LLMModel"] = relationship("LLMModel", back_populates="snapshots")

    def __repr__(self) -> str:
        """Return string representation of LeaderboardSnapshot."""
        return f"<LeaderboardSnapshot(id={self.id}, model_id={self.model_id}, rank={self.rank})>"


class Trade(Base):
    """Individual trade record."""

    __tablename__ = "trades"
    __table_args__ = (
        Index("ix_trades_model_id", "model_id"),
        Index("ix_trades_symbol", "symbol"),
        Index("ix_trades_opened_at", "opened_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("llm_models.id"), nullable=False
    )
    trade_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    side: Mapped[TradeSide] = mapped_column(
        Enum(TradeSide, create_constraint=False, native_enum=False), nullable=False
    )
    entry_price: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    exit_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8), nullable=True)
    size: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    leverage: Mapped[int] = mapped_column(Integer, default=1)
    pnl: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    pnl_percent: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 4), nullable=True
    )
    status: Mapped[TradeStatus] = mapped_column(
        Enum(TradeStatus, create_constraint=False, native_enum=False), nullable=False
    )
    opened_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    raw_data: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    model: Mapped["LLMModel"] = relationship("LLMModel", back_populates="trades")

    def __repr__(self) -> str:
        """Return string representation of Trade."""
        return f"<Trade(id={self.id}, symbol='{self.symbol}', side={self.side.value})>"


class ModelChat(Base):
    """AI model chat/decision log."""

    __tablename__ = "model_chats"
    __table_args__ = (
        Index("ix_model_chats_model_id", "model_id"),
        Index("ix_model_chats_timestamp", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("llm_models.id"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    decision: Mapped[Optional[ChatDecision]] = mapped_column(
        Enum(ChatDecision, create_constraint=False, native_enum=False), nullable=True
    )
    symbol: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    raw_data: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    model: Mapped["LLMModel"] = relationship("LLMModel", back_populates="chats")

    def __repr__(self) -> str:
        """Return string representation of ModelChat."""
        return f"<ModelChat(id={self.id}, model_id={self.model_id})>"
