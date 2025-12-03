"""Data persistence for scraped data.

This module provides functionality to persist scraped data from nof1.ai
to the PostgreSQL database using SQLAlchemy ORM.

Classes:
    DataPersistence: Handles database operations for scraped data.

Example:
    >>> from nof1_tracker.database.connection import get_session
    >>> with get_session() as session:
    ...     persistence = DataPersistence(session)
    ...     model = persistence.get_or_create_model("Claude Sonnet 4.5", "Anthropic")
    ...     season = persistence.get_or_create_season(1)
"""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

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
from nof1_tracker.scraper.leaderboard import LeaderboardEntry
from nof1_tracker.scraper.models import ModelChatData, TradeData


class DataPersistence:
    """Persist scraped data to PostgreSQL.

    Provides methods to save leaderboard entries, trades, and model chat
    data to the database with proper model and season management.

    Attributes:
        session: SQLAlchemy session for database operations.

    Example:
        >>> with get_session() as session:
        ...     persistence = DataPersistence(session)
        ...     model = persistence.get_or_create_model("GPT-5", "OpenAI")
        ...     season = persistence.get_or_create_season(1)
        ...     persistence.save_leaderboard_entry(entry, season)
    """

    def __init__(self, session: Session) -> None:
        """Initialize DataPersistence with a database session.

        Args:
            session: SQLAlchemy session for database operations.
        """
        self.session = session

    def get_or_create_model(self, name: str, provider: str) -> LLMModel:
        """Get existing model or create new one.

        Looks up a model by name and creates it if it doesn't exist.

        Args:
            name: Display name of the model.
            provider: Company/organization providing the model.

        Returns:
            LLMModel: The existing or newly created model.

        Example:
            >>> model = persistence.get_or_create_model("Claude Sonnet 4.5", "Anthropic")
            >>> model.provider
            'Anthropic'
        """
        model = self.session.query(LLMModel).filter_by(name=name).first()
        if not model:
            model = LLMModel(
                name=name,
                provider=provider,
                model_id=name.lower().replace(" ", "-"),
                is_active=True,
            )
            self.session.add(model)
            self.session.flush()
        return model

    def get_or_create_season(self, season_number: int = 1) -> Season:
        """Get existing season or create new one.

        Looks up a season by number and creates it if it doesn't exist.

        Args:
            season_number: The season number to look up or create.

        Returns:
            Season: The existing or newly created season.

        Example:
            >>> season = persistence.get_or_create_season(1)
            >>> season.name
            'Season 1'
        """
        season = (
            self.session.query(Season).filter_by(season_number=season_number).first()
        )
        if not season:
            season = Season(
                season_number=season_number,
                name=f"Season {season_number}",
                start_date=datetime.now(UTC),
                status=SeasonStatus.active,
            )
            self.session.add(season)
            self.session.flush()
        return season

    def save_leaderboard_entry(
        self,
        entry: LeaderboardEntry,
        season: Season,
    ) -> LeaderboardSnapshot:
        """Save a leaderboard entry as a snapshot.

        Creates a new LeaderboardSnapshot record in the database,
        automatically creating or finding the associated model.

        Args:
            entry: The leaderboard entry to save.
            season: The season this snapshot belongs to.

        Returns:
            LeaderboardSnapshot: The newly created snapshot record.

        Example:
            >>> snapshot = persistence.save_leaderboard_entry(entry, season)
            >>> snapshot.rank
            1
        """
        model = self.get_or_create_model(entry.model_name, entry.provider)

        snapshot = LeaderboardSnapshot(
            season_id=season.id,
            model_id=model.id,
            timestamp=entry.scraped_at,
            rank=entry.rank,
            total_assets=entry.total_assets,
            pnl=entry.pnl,
            pnl_percent=entry.pnl_percent,
            roi=entry.pnl_percent,  # Using pnl_percent as ROI
            win_rate=entry.win_rate,
            total_trades=entry.total_trades,
            raw_data={
                "sharpe_ratio": str(entry.sharpe_ratio) if entry.sharpe_ratio else None,
                "fees": str(entry.fees) if entry.fees else None,
                "leverage": str(entry.leverage) if entry.leverage else None,
                "confidence": str(entry.confidence) if entry.confidence else None,
            },
        )
        self.session.add(snapshot)
        return snapshot

    def save_trade(self, trade: TradeData, model: LLMModel) -> Trade:
        """Save a trade record.

        Creates a new Trade record in the database.

        Args:
            trade: The trade data to save.
            model: The LLM model that made this trade.

        Returns:
            Trade: The newly created trade record.

        Note:
            - "long" and "buy" are mapped to TradeSide.buy
            - "short" and "sell" are mapped to TradeSide.sell
            - "liquidated" status is mapped to TradeStatus.cancelled

        Example:
            >>> db_trade = persistence.save_trade(trade_data, model)
            >>> db_trade.symbol
            'BTC-PERP'
        """
        # Map side - "long" and "buy" both map to buy
        side = (
            TradeSide.buy if trade.side.lower() in ("long", "buy") else TradeSide.sell
        )

        # Map status
        status_map = {
            "open": TradeStatus.open,
            "closed": TradeStatus.closed,
            "liquidated": TradeStatus.cancelled,
        }
        status = status_map.get(trade.status.lower(), TradeStatus.open)

        # Generate trade_id if not provided
        trade_id = trade.trade_id
        if not trade_id:
            trade_id = f"{model.id}-{trade.symbol}-{trade.opened_at.isoformat()}"

        db_trade = Trade(
            model_id=model.id,
            trade_id=trade_id,
            symbol=trade.symbol,
            side=side,
            entry_price=trade.entry_price,
            exit_price=trade.exit_price,
            size=trade.size,
            leverage=trade.leverage or 1,
            pnl=trade.pnl,
            pnl_percent=trade.pnl_percent,
            status=status,
            opened_at=trade.opened_at,
            closed_at=trade.closed_at,
            raw_data=trade.raw_data,
        )
        self.session.add(db_trade)
        return db_trade

    def save_model_chat(self, chat: ModelChatData, model: LLMModel) -> ModelChat:
        """Save a model chat entry.

        Creates a new ModelChat record in the database.

        Args:
            chat: The chat data to save.
            model: The LLM model that created this chat.

        Returns:
            ModelChat: The newly created chat record.

        Note:
            Decision values are mapped to ChatDecision enum.
            "close" is mapped to ChatDecision.none.

        Example:
            >>> db_chat = persistence.save_model_chat(chat_data, model)
            >>> db_chat.decision
            ChatDecision.buy
        """
        # Map decision
        decision_map = {
            "buy": ChatDecision.buy,
            "sell": ChatDecision.sell,
            "hold": ChatDecision.hold,
            "close": ChatDecision.none,  # Map close to none
            "none": ChatDecision.none,
        }
        decision = decision_map.get(
            chat.decision.lower() if chat.decision else "none", ChatDecision.none
        )

        db_chat = ModelChat(
            model_id=model.id,
            timestamp=chat.timestamp,
            content=chat.content,
            decision=decision,
            symbol=chat.symbol,
            confidence=chat.confidence,
            raw_data=chat.raw_data,
        )
        self.session.add(db_chat)
        return db_chat
