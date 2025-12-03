"""Tests for NOF1 Tracker scraper module.

This module contains unit tests for the scraper components:
- BaseScraper: Browser lifecycle management
- LeaderboardScraper: Leaderboard data extraction
- ModelPageScraper: Individual model page scraping
- DataPersistence: Database persistence layer
- ScraperRunner: Orchestration and scheduling

Note: Integration tests that require actual browser/network access
should be marked with @pytest.mark.integration.
"""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from nof1_tracker.database.models import (
    Base,
    ChatDecision,
    LLMModel,
    Season,
    SeasonStatus,
    TradeSide,
    TradeStatus,
)


class TestBaseScraper:
    """Tests for BaseScraper class."""

    def test_base_scraper_initialization_defaults(self) -> None:
        """Test BaseScraper initializes with default settings."""
        from nof1_tracker.scraper.base import BaseScraper

        scraper = BaseScraper()
        assert scraper.headless is True
        assert scraper.timeout == 30000
        assert scraper._playwright is None
        assert scraper._browser is None

    def test_base_scraper_initialization_custom(self) -> None:
        """Test BaseScraper initializes with custom settings."""
        from nof1_tracker.scraper.base import BaseScraper

        scraper = BaseScraper(headless=False, timeout=60000)
        assert scraper.headless is False
        assert scraper.timeout == 60000

    def test_base_scraper_base_url(self) -> None:
        """Test BaseScraper has correct BASE_URL."""
        from nof1_tracker.scraper.base import BaseScraper

        assert BaseScraper.BASE_URL == "https://nof1.ai"

    def test_base_scraper_now_utc_returns_utc(self) -> None:
        """Test now_utc returns UTC datetime."""
        from nof1_tracker.scraper.base import BaseScraper

        before = datetime.now(timezone.utc)
        result = BaseScraper.now_utc()
        after = datetime.now(timezone.utc)

        assert result.tzinfo is not None
        assert before <= result <= after

    @pytest.mark.asyncio
    async def test_base_scraper_context_manager(self) -> None:
        """Test BaseScraper works as async context manager."""
        from nof1_tracker.scraper.base import BaseScraper

        scraper = BaseScraper()

        with patch.object(scraper, "start", new_callable=AsyncMock) as mock_start:
            with patch.object(scraper, "stop", new_callable=AsyncMock) as mock_stop:
                async with scraper:
                    mock_start.assert_called_once()
                mock_stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_base_scraper_new_page_requires_browser(self) -> None:
        """Test new_page raises if browser not started."""
        from nof1_tracker.scraper.base import BaseScraper

        scraper = BaseScraper()
        with pytest.raises(RuntimeError, match="Browser not started"):
            async with scraper.new_page():
                pass


class TestLeaderboardScraper:
    """Tests for LeaderboardScraper class."""

    def test_leaderboard_scraper_inherits_base(self) -> None:
        """Test LeaderboardScraper inherits from BaseScraper."""
        from nof1_tracker.scraper.base import BaseScraper
        from nof1_tracker.scraper.leaderboard import LeaderboardScraper

        assert issubclass(LeaderboardScraper, BaseScraper)

    def test_leaderboard_scraper_has_correct_url(self) -> None:
        """Test LeaderboardScraper has correct LEADERBOARD_URL."""
        from nof1_tracker.scraper.leaderboard import LeaderboardScraper

        assert LeaderboardScraper.LEADERBOARD_URL == "https://nof1.ai/leaderboard"

    def test_leaderboard_scraper_model_providers_mapping(self) -> None:
        """Test LeaderboardScraper has model provider mapping."""
        from nof1_tracker.scraper.leaderboard import LeaderboardScraper

        providers = LeaderboardScraper.MODEL_PROVIDERS
        assert "DeepSeek V3.1" in providers
        assert "Claude Sonnet 4.5" in providers
        assert providers["Claude Sonnet 4.5"] == "Anthropic"
        assert providers["GPT-5"] == "OpenAI"
        assert providers["Grok 4"] == "xAI"


class TestLeaderboardEntry:
    """Tests for LeaderboardEntry dataclass."""

    def test_leaderboard_entry_creation(self) -> None:
        """Test LeaderboardEntry can be created with required fields."""
        from nof1_tracker.scraper.leaderboard import LeaderboardEntry

        entry = LeaderboardEntry(
            model_name="Claude Sonnet 4.5",
            provider="Anthropic",
            rank=1,
            total_assets=Decimal("12345.67"),
            pnl=Decimal("2345.67"),
            pnl_percent=Decimal("23.45"),
            sharpe_ratio=Decimal("1.5"),
            win_rate=Decimal("65.0"),
            total_trades=100,
            fees=Decimal("45.67"),
            leverage=Decimal("2.0"),
            confidence=Decimal("85.0"),
            raw_data={"test": "data"},
            scraped_at=datetime.now(timezone.utc),
        )

        assert entry.model_name == "Claude Sonnet 4.5"
        assert entry.provider == "Anthropic"
        assert entry.rank == 1
        assert entry.total_assets == Decimal("12345.67")

    def test_leaderboard_entry_optional_fields_none(self) -> None:
        """Test LeaderboardEntry works with None optional fields."""
        from nof1_tracker.scraper.leaderboard import LeaderboardEntry

        entry = LeaderboardEntry(
            model_name="Test Model",
            provider="Test Provider",
            rank=1,
            total_assets=Decimal("10000"),
            pnl=Decimal("0"),
            pnl_percent=Decimal("0"),
            sharpe_ratio=None,
            win_rate=None,
            total_trades=None,
            fees=None,
            leverage=None,
            confidence=None,
            raw_data={},
            scraped_at=datetime.now(timezone.utc),
        )

        assert entry.sharpe_ratio is None
        assert entry.win_rate is None


class TestModelPageScraper:
    """Tests for ModelPageScraper class."""

    def test_model_page_scraper_inherits_base(self) -> None:
        """Test ModelPageScraper inherits from BaseScraper."""
        from nof1_tracker.scraper.base import BaseScraper
        from nof1_tracker.scraper.models import ModelPageScraper

        assert issubclass(ModelPageScraper, BaseScraper)

    def test_model_page_scraper_model_slugs(self) -> None:
        """Test ModelPageScraper has correct model slugs."""
        from nof1_tracker.scraper.models import ModelPageScraper

        slugs = ModelPageScraper.MODEL_SLUGS
        assert slugs["DeepSeek V3.1"] == "deepseek-chat-v3.1"
        assert slugs["Claude Sonnet 4.5"] == "claude-sonnet-4-5"
        assert slugs["GPT-5"] == "gpt-5"

    def test_model_page_scraper_url_generation(self) -> None:
        """Test get_model_url generates correct URLs."""
        from nof1_tracker.scraper.models import ModelPageScraper

        scraper = ModelPageScraper()

        url = scraper.get_model_url("DeepSeek V3.1")
        assert url == "https://nof1.ai/models/deepseek-chat-v3.1"

        url = scraper.get_model_url("Claude Sonnet 4.5")
        assert url == "https://nof1.ai/models/claude-sonnet-4-5"

    def test_model_page_scraper_url_generation_unknown_model(self) -> None:
        """Test get_model_url handles unknown models."""
        from nof1_tracker.scraper.models import ModelPageScraper

        scraper = ModelPageScraper()
        url = scraper.get_model_url("Unknown Model")
        assert url == "https://nof1.ai/models/unknown-model"


class TestTradeData:
    """Tests for TradeData dataclass."""

    def test_trade_data_creation(self) -> None:
        """Test TradeData can be created with all fields."""
        from nof1_tracker.scraper.models import TradeData

        trade = TradeData(
            trade_id="trade-123",
            symbol="BTC-PERP",
            side="long",
            entry_price=Decimal("50000.00"),
            exit_price=Decimal("51000.00"),
            size=Decimal("0.1"),
            leverage=10,
            pnl=Decimal("100.00"),
            pnl_percent=Decimal("2.0"),
            status="closed",
            opened_at=datetime.now(timezone.utc),
            closed_at=datetime.now(timezone.utc),
            raw_data={"test": "data"},
        )

        assert trade.trade_id == "trade-123"
        assert trade.symbol == "BTC-PERP"
        assert trade.side == "long"
        assert trade.leverage == 10


class TestModelChatData:
    """Tests for ModelChatData dataclass."""

    def test_model_chat_data_creation(self) -> None:
        """Test ModelChatData can be created with all fields."""
        from nof1_tracker.scraper.models import ModelChatData

        chat = ModelChatData(
            timestamp=datetime.now(timezone.utc),
            content="I recommend buying BTC",
            decision="buy",
            symbol="BTC-PERP",
            confidence=Decimal("85.0"),
            raw_data={"test": "data"},
        )

        assert chat.content == "I recommend buying BTC"
        assert chat.decision == "buy"
        assert chat.symbol == "BTC-PERP"


class TestPositionData:
    """Tests for PositionData dataclass."""

    def test_position_data_creation(self) -> None:
        """Test PositionData can be created with all fields."""
        from nof1_tracker.scraper.models import PositionData

        position = PositionData(
            symbol="BTC-PERP",
            side="long",
            size=Decimal("0.5"),
            entry_price=Decimal("50000.00"),
            current_price=Decimal("51000.00"),
            unrealized_pnl=Decimal("500.00"),
            leverage=10,
        )

        assert position.symbol == "BTC-PERP"
        assert position.unrealized_pnl == Decimal("500.00")


class TestDataPersistence:
    """Tests for DataPersistence class."""

    @pytest.fixture
    def mock_session(self) -> MagicMock:
        """Create a mock database session."""
        session = MagicMock()
        session.query.return_value.filter_by.return_value.first.return_value = None
        return session

    def test_data_persistence_initialization(self, mock_session: MagicMock) -> None:
        """Test DataPersistence initializes with session."""
        from nof1_tracker.scraper.persistence import DataPersistence

        persistence = DataPersistence(mock_session)
        assert persistence.session is mock_session

    def test_get_or_create_model_creates_new(self, mock_session: MagicMock) -> None:
        """Test get_or_create_model creates new model if not exists."""
        from nof1_tracker.scraper.persistence import DataPersistence

        persistence = DataPersistence(mock_session)
        model = persistence.get_or_create_model("Test Model", "Test Provider")

        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        assert model.name == "Test Model"
        assert model.provider == "Test Provider"

    def test_get_or_create_model_returns_existing(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_or_create_model returns existing model."""
        from nof1_tracker.scraper.persistence import DataPersistence

        existing_model = LLMModel(
            id=1,
            name="Existing Model",
            provider="Existing Provider",
            model_id="existing-model",
        )
        mock_session.query.return_value.filter_by.return_value.first.return_value = (
            existing_model
        )

        persistence = DataPersistence(mock_session)
        model = persistence.get_or_create_model("Existing Model", "Existing Provider")

        mock_session.add.assert_not_called()
        assert model is existing_model

    def test_get_or_create_season_creates_new(self, mock_session: MagicMock) -> None:
        """Test get_or_create_season creates new season if not exists."""
        from nof1_tracker.scraper.persistence import DataPersistence

        persistence = DataPersistence(mock_session)
        season = persistence.get_or_create_season(1)

        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        assert season.season_number == 1
        assert season.name == "Season 1"
        assert season.status == SeasonStatus.active

    def test_save_leaderboard_entry(self, mock_session: MagicMock) -> None:
        """Test save_leaderboard_entry creates snapshot."""
        from nof1_tracker.scraper.leaderboard import LeaderboardEntry
        from nof1_tracker.scraper.persistence import DataPersistence

        # Setup mock to return model and season
        model = LLMModel(id=1, name="Test", provider="Test", model_id="test")
        season = Season(id=1, season_number=1, name="Season 1")
        mock_session.query.return_value.filter_by.return_value.first.return_value = (
            model
        )

        persistence = DataPersistence(mock_session)
        entry = LeaderboardEntry(
            model_name="Test",
            provider="Test",
            rank=1,
            total_assets=Decimal("10000"),
            pnl=Decimal("1000"),
            pnl_percent=Decimal("10.0"),
            sharpe_ratio=Decimal("1.5"),
            win_rate=Decimal("65.0"),
            total_trades=100,
            fees=None,
            leverage=None,
            confidence=None,
            raw_data={},
            scraped_at=datetime.now(timezone.utc),
        )

        snapshot = persistence.save_leaderboard_entry(entry, season)

        mock_session.add.assert_called()
        assert snapshot.rank == 1
        assert snapshot.total_assets == Decimal("10000")

    def test_save_trade_maps_side_correctly(self, mock_session: MagicMock) -> None:
        """Test save_trade maps trade side to enum."""
        from nof1_tracker.scraper.models import TradeData
        from nof1_tracker.scraper.persistence import DataPersistence

        model = LLMModel(id=1, name="Test", provider="Test", model_id="test")

        persistence = DataPersistence(mock_session)
        trade_data = TradeData(
            trade_id="test-123",
            symbol="BTC-PERP",
            side="long",
            entry_price=Decimal("50000"),
            exit_price=None,
            size=Decimal("0.1"),
            leverage=10,
            pnl=None,
            pnl_percent=None,
            status="open",
            opened_at=datetime.now(timezone.utc),
            closed_at=None,
            raw_data={},
        )

        trade = persistence.save_trade(trade_data, model)

        mock_session.add.assert_called_once()
        assert trade.side == TradeSide.buy

    def test_save_trade_maps_sell_side(self, mock_session: MagicMock) -> None:
        """Test save_trade maps short/sell to sell enum."""
        from nof1_tracker.scraper.models import TradeData
        from nof1_tracker.scraper.persistence import DataPersistence

        model = LLMModel(id=1, name="Test", provider="Test", model_id="test")

        persistence = DataPersistence(mock_session)
        trade_data = TradeData(
            trade_id="test-456",
            symbol="ETH-PERP",
            side="short",
            entry_price=Decimal("3000"),
            exit_price=None,
            size=Decimal("1.0"),
            leverage=5,
            pnl=None,
            pnl_percent=None,
            status="open",
            opened_at=datetime.now(timezone.utc),
            closed_at=None,
            raw_data={},
        )

        trade = persistence.save_trade(trade_data, model)
        assert trade.side == TradeSide.sell

    def test_save_model_chat(self, mock_session: MagicMock) -> None:
        """Test save_model_chat creates chat record."""
        from nof1_tracker.scraper.models import ModelChatData
        from nof1_tracker.scraper.persistence import DataPersistence

        model = LLMModel(id=1, name="Test", provider="Test", model_id="test")

        persistence = DataPersistence(mock_session)
        chat_data = ModelChatData(
            timestamp=datetime.now(timezone.utc),
            content="Buy recommendation",
            decision="buy",
            symbol="BTC-PERP",
            confidence=Decimal("90.0"),
            raw_data={},
        )

        chat = persistence.save_model_chat(chat_data, model)

        mock_session.add.assert_called_once()
        assert chat.decision == ChatDecision.buy
        assert chat.content == "Buy recommendation"


class TestScraperRunner:
    """Tests for ScraperRunner class."""

    def test_scraper_runner_initialization_default(self) -> None:
        """Test ScraperRunner initializes with default headless=True."""
        from nof1_tracker.scraper.runner import ScraperRunner

        runner = ScraperRunner()
        assert runner.headless is True

    def test_scraper_runner_initialization_custom(self) -> None:
        """Test ScraperRunner initializes with custom headless setting."""
        from nof1_tracker.scraper.runner import ScraperRunner

        runner = ScraperRunner(headless=False)
        assert runner.headless is False

    def test_scraper_runner_has_models_list(self) -> None:
        """Test ScraperRunner has list of models to scrape."""
        from nof1_tracker.scraper.runner import ScraperRunner

        assert len(ScraperRunner.MODELS) == 6
        assert "DeepSeek V3.1" in ScraperRunner.MODELS
        assert "Claude Sonnet 4.5" in ScraperRunner.MODELS
        assert "GPT-5" in ScraperRunner.MODELS


class TestScraperModuleExports:
    """Tests for scraper module exports."""

    def test_all_classes_exported(self) -> None:
        """Test all scraper classes are exported from module."""
        from nof1_tracker.scraper import (
            BaseScraper,
            DataPersistence,
            LeaderboardEntry,
            LeaderboardScraper,
            ModelChatData,
            ModelPageScraper,
            PositionData,
            ScraperRunner,
            TradeData,
        )

        # Just verify imports work
        assert BaseScraper is not None
        assert LeaderboardScraper is not None
        assert LeaderboardEntry is not None
        assert ModelPageScraper is not None
        assert TradeData is not None
        assert ModelChatData is not None
        assert PositionData is not None
        assert DataPersistence is not None
        assert ScraperRunner is not None


# Integration tests marked for separate execution
@pytest.mark.integration
class TestScraperIntegration:
    """Integration tests requiring browser and network.

    These tests are skipped by default. Run with:
    pytest -m integration tests/test_scraper/
    """

    @pytest.mark.asyncio
    async def test_leaderboard_scraper_real_browser(self) -> None:
        """Test LeaderboardScraper with real browser."""
        from nof1_tracker.scraper.leaderboard import LeaderboardScraper

        async with LeaderboardScraper(headless=True) as scraper:
            entries = await scraper.scrape()
            assert isinstance(entries, list)

    @pytest.mark.asyncio
    async def test_model_page_scraper_real_browser(self) -> None:
        """Test ModelPageScraper with real browser."""
        from nof1_tracker.scraper.models import ModelPageScraper

        async with ModelPageScraper(headless=True) as scraper:
            data = await scraper.scrape_model("Claude Sonnet 4.5")
            assert "trades" in data
            assert "positions" in data
            assert "chats" in data
