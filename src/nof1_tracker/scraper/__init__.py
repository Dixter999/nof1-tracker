"""Scraper module for NOF1 Tracker.

This module provides web scraping functionality using Playwright for nof1.ai Alpha Arena.
It handles:
- Browser automation with Playwright
- Leaderboard data extraction
- Individual model page scraping (trades, positions, chat)
- Data persistence to PostgreSQL

Classes:
    BaseScraper: Base class with browser lifecycle management.
    LeaderboardScraper: Scraper for the leaderboard page.
    LeaderboardEntry: Dataclass for leaderboard row data.
    ModelPageScraper: Scraper for individual model pages.
    TradeData: Dataclass for trade records.
    ModelChatData: Dataclass for model chat/reasoning entries.
    PositionData: Dataclass for current positions.
    DataPersistence: Database persistence layer.
    ScraperRunner: Main orchestration and scheduling.

Example:
    >>> from nof1_tracker.scraper import LeaderboardScraper
    >>> async with LeaderboardScraper(headless=True) as scraper:
    ...     entries = await scraper.scrape()
    ...     for entry in entries:
    ...         print(f"{entry.rank}. {entry.model_name}")
"""

from nof1_tracker.scraper.base import BaseScraper
from nof1_tracker.scraper.leaderboard import LeaderboardEntry, LeaderboardScraper
from nof1_tracker.scraper.models import (
    LivePageScraper,
    ModelChatData,
    ModelPageScraper,
    PositionData,
    TradeData,
)
from nof1_tracker.scraper.persistence import DataPersistence
from nof1_tracker.scraper.runner import ScraperRunner

__all__ = [
    "BaseScraper",
    "LeaderboardScraper",
    "LeaderboardEntry",
    "ModelPageScraper",
    "LivePageScraper",
    "TradeData",
    "ModelChatData",
    "PositionData",
    "DataPersistence",
    "ScraperRunner",
]
