"""Scraper for nof1.ai leaderboard page.

This module provides functionality to scrape the Alpha Arena leaderboard,
extracting model rankings, performance metrics, and trading statistics.

Classes:
    LeaderboardEntry: Dataclass representing a single leaderboard row.
    LeaderboardScraper: Scraper for the leaderboard page.

Example:
    >>> async with LeaderboardScraper(headless=True) as scraper:
    ...     entries = await scraper.scrape()
    ...     for entry in entries:
    ...         print(f"{entry.rank}. {entry.model_name}: {entry.pnl_percent}%")
"""

import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

from playwright.async_api import ElementHandle, Page

from nof1_tracker.scraper.base import BaseScraper


@dataclass
class LeaderboardEntry:
    """Single entry from the leaderboard.

    Represents one model's performance data from a leaderboard snapshot.

    Attributes:
        model_name: Display name of the AI model.
        provider: Company/organization providing the model.
        rank: Current position on the leaderboard.
        total_assets: Total account value in USD.
        pnl: Profit and loss in USD.
        pnl_percent: Profit and loss as percentage.
        sharpe_ratio: Risk-adjusted return metric (optional).
        win_rate: Percentage of winning trades (optional).
        total_trades: Number of completed trades (optional).
        fees: Trading fees paid in USD (optional).
        leverage: Average leverage used (optional).
        confidence: Model's confidence level (optional).
        raw_data: Original scraped data for debugging.
        scraped_at: Timestamp when data was scraped.
    """

    model_name: str
    provider: str
    rank: int
    total_assets: Decimal
    pnl: Decimal
    pnl_percent: Decimal
    sharpe_ratio: Decimal | None
    win_rate: Decimal | None
    total_trades: int | None
    fees: Decimal | None
    leverage: Decimal | None
    confidence: Decimal | None
    raw_data: dict[str, Any]
    scraped_at: datetime


class LeaderboardScraper(BaseScraper):
    """Scraper for the nof1.ai leaderboard.

    Extracts model rankings and performance metrics from the Alpha Arena
    leaderboard page.

    Attributes:
        LEADERBOARD_URL: URL of the leaderboard page.
        MODEL_PROVIDERS: Mapping of model names to their providers.

    Example:
        >>> async with LeaderboardScraper() as scraper:
        ...     entries = await scraper.scrape()
        ...     print(f"Found {len(entries)} models")
    """

    LEADERBOARD_URL = f"{BaseScraper.BASE_URL}/leaderboard"

    # Model name to provider mapping
    # Includes common variations of model names
    MODEL_PROVIDERS: dict[str, str] = {
        "DeepSeek V3.1": "DeepSeek",
        "DeepSeek Chat V3.1": "DeepSeek",
        "Qwen3 Max": "Alibaba",
        "Qwen 3 Max": "Alibaba",
        "Claude Sonnet 4.5": "Anthropic",
        "Claude 4.5 Sonnet": "Anthropic",
        "Grok 4": "xAI",
        "GPT-5": "OpenAI",
        "Gemini 2.5 Pro": "Google",
    }

    async def scrape(self) -> list[LeaderboardEntry]:
        """Scrape the current leaderboard standings.

        Navigates to the leaderboard page and extracts all model
        performance data.

        Returns:
            list[LeaderboardEntry]: List of leaderboard entries, ordered by rank.

        Raises:
            TimeoutError: If page or elements fail to load within timeout.
        """
        async with self.new_page() as page:
            await page.goto(self.LEADERBOARD_URL)
            await page.wait_for_load_state("networkidle")

            # Wait for leaderboard to load
            try:
                await page.wait_for_selector(
                    '[data-testid="leaderboard"]', timeout=10000
                )
            except Exception:
                # Try alternative selectors if data-testid not found
                await page.wait_for_selector("table", timeout=10000)

            entries = []
            # Parse leaderboard rows
            rows = await page.query_selector_all('[data-testid="leaderboard-row"]')

            # Fallback to table rows if data-testid not found
            if not rows:
                rows = await page.query_selector_all("table tbody tr")

            for rank, row in enumerate(rows, 1):
                entry = await self._parse_row(page, row, rank)
                if entry:
                    entries.append(entry)

            return entries

    async def _parse_row(
        self, page: Page, row: ElementHandle, rank: int
    ) -> LeaderboardEntry | None:
        """Parse a single leaderboard row.

        Args:
            page: The browser page (for context).
            row: Element handle for the row to parse.
            rank: Position number of this row.

        Returns:
            LeaderboardEntry if parsing succeeds, None otherwise.
        """
        try:
            # Extract text content - adjust selectors based on actual DOM
            model_name = await row.query_selector('[data-testid="model-name"]')

            # Fallback selectors
            if not model_name:
                model_name = await row.query_selector("td:first-child")

            model_name_text = await model_name.inner_text() if model_name else "Unknown"
            model_name_text = model_name_text.strip()

            # Get numeric values
            total_assets = await self._extract_decimal(
                row, '[data-testid="total-assets"]'
            )
            pnl = await self._extract_decimal(row, '[data-testid="pnl"]')
            pnl_percent = await self._extract_decimal(
                row, '[data-testid="pnl-percent"]'
            )

            # Use defaults if not found
            if total_assets is None:
                total_assets = Decimal("0")
            if pnl is None:
                pnl = Decimal("0")
            if pnl_percent is None:
                pnl_percent = Decimal("0")

            # Optional fields
            sharpe = await self._extract_decimal(row, '[data-testid="sharpe"]')
            win_rate = await self._extract_decimal(row, '[data-testid="win-rate"]')
            total_trades = await self._extract_int(row, '[data-testid="total-trades"]')
            fees = await self._extract_decimal(row, '[data-testid="fees"]')
            leverage = await self._extract_decimal(row, '[data-testid="leverage"]')
            confidence = await self._extract_decimal(row, '[data-testid="confidence"]')

            provider = self.MODEL_PROVIDERS.get(model_name_text, "Unknown")

            return LeaderboardEntry(
                model_name=model_name_text,
                provider=provider,
                rank=rank,
                total_assets=total_assets,
                pnl=pnl,
                pnl_percent=pnl_percent,
                sharpe_ratio=sharpe,
                win_rate=win_rate,
                total_trades=total_trades,
                fees=fees,
                leverage=leverage,
                confidence=confidence,
                raw_data={"rank": rank, "model": model_name_text},
                scraped_at=self.now_utc(),
            )
        except Exception as e:
            # Log error but continue processing other rows
            print(f"Error parsing row: {e}")
            return None

    async def _extract_decimal(
        self, element: ElementHandle, selector: str
    ) -> Decimal | None:
        """Extract decimal value from element.

        Args:
            element: Parent element to search within.
            selector: CSS selector for the target element.

        Returns:
            Decimal value if found and parseable, None otherwise.
        """
        try:
            el = await element.query_selector(selector)
            if el:
                text = await el.inner_text()
                # Remove $, %, commas and parse
                cleaned = re.sub(r"[$%,]", "", text).strip()
                return Decimal(cleaned) if cleaned and cleaned != "-" else None
        except Exception:
            pass
        return None

    async def _extract_int(self, element: ElementHandle, selector: str) -> int | None:
        """Extract integer value from element.

        Args:
            element: Parent element to search within.
            selector: CSS selector for the target element.

        Returns:
            Integer value if found and parseable, None otherwise.
        """
        try:
            el = await element.query_selector(selector)
            if el:
                text = await el.inner_text()
                cleaned = re.sub(r"[,]", "", text).strip()
                return int(cleaned) if cleaned and cleaned != "-" else None
        except Exception:
            pass
        return None
