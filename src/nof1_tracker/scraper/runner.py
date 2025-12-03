"""Main scraper runner with scheduling.

This module provides the orchestration layer for running all scrapers
and persisting data to the database. It supports both one-time scraping
and continuous scheduled scraping.

Classes:
    ScraperRunner: Main entry point for scraper orchestration.

Functions:
    main: Async entry point for running scrapers.

Example:
    >>> runner = ScraperRunner(headless=True)
    >>> results = await runner.run_once()
    >>> print(f"Scraped {len(results['leaderboard'])} models")

    >>> # Or run continuously every 15 minutes
    >>> await runner.run_continuous(interval_minutes=15)
"""

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from nof1_tracker.database.connection import get_session
from nof1_tracker.scraper.leaderboard import LeaderboardScraper
from nof1_tracker.scraper.models import ModelPageScraper
from nof1_tracker.scraper.persistence import DataPersistence

logger = logging.getLogger(__name__)


class ScraperRunner:
    """Run all scrapers and persist data.

    Orchestrates scraping of the leaderboard and individual model pages,
    then saves all data to the database.

    Attributes:
        MODELS: List of model names to scrape.
        headless: Whether to run browser in headless mode.

    Example:
        >>> runner = ScraperRunner(headless=True)
        >>> results = await runner.run_once()
        >>> if results["errors"]:
        ...     print(f"Errors: {results['errors']}")
    """

    MODELS: list[str] = [
        "DeepSeek V3.1",
        "Qwen3 Max",
        "Claude Sonnet 4.5",
        "Grok 4",
        "GPT-5",
        "Gemini 2.5 Pro",
    ]

    def __init__(self, headless: bool = True) -> None:
        """Initialize the scraper runner.

        Args:
            headless: Run browsers in headless mode. Default True.
        """
        self.headless = headless

    async def run_once(self) -> dict[str, Any]:
        """Run all scrapers once and save to database.

        Scrapes the leaderboard and all model pages, saving results
        to the database.

        Returns:
            Dictionary containing:
                - timestamp: ISO format UTC timestamp
                - leaderboard: List of scraped model names
                - models: Dict of model names to scrape counts
                - errors: List of error messages

        Example:
            >>> results = await runner.run_once()
            >>> len(results["leaderboard"])
            6
        """
        results: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "leaderboard": [],
            "models": {},
            "errors": [],
        }

        # Scrape leaderboard
        try:
            async with LeaderboardScraper(headless=self.headless) as scraper:
                entries = await scraper.scrape()
                results["leaderboard"] = [e.model_name for e in entries]

                # Save to database
                with get_session() as session:
                    persistence = DataPersistence(session)
                    season = persistence.get_or_create_season(1)

                    for entry in entries:
                        persistence.save_leaderboard_entry(entry, season)

                    logger.info(f"Saved {len(entries)} leaderboard entries")

        except Exception as e:
            logger.error(f"Leaderboard scrape error: {e}")
            results["errors"].append(f"Leaderboard: {str(e)}")

        # Scrape each model's detailed data
        try:
            async with ModelPageScraper(headless=self.headless) as scraper:
                for model_name in self.MODELS:
                    try:
                        data = await scraper.scrape_model(model_name)
                        results["models"][model_name] = {
                            "trades": len(data.get("trades", [])),
                            "chats": len(data.get("chats", [])),
                            "positions": len(data.get("positions", [])),
                        }

                        # Save to database
                        with get_session() as session:
                            persistence = DataPersistence(session)
                            model = persistence.get_or_create_model(
                                model_name,
                                LeaderboardScraper.MODEL_PROVIDERS.get(
                                    model_name, "Unknown"
                                ),
                            )

                            for trade in data.get("trades", []):
                                persistence.save_trade(trade, model)

                            for chat in data.get("chats", []):
                                persistence.save_model_chat(chat, model)

                        logger.info(f"Scraped {model_name}")

                    except Exception as e:
                        logger.error(f"Error scraping {model_name}: {e}")
                        results["errors"].append(f"{model_name}: {str(e)}")

        except Exception as e:
            logger.error(f"Model scraper error: {e}")
            results["errors"].append(f"Models: {str(e)}")

        return results

    async def run_continuous(self, interval_minutes: int = 15) -> None:
        """Run scrapers continuously at specified interval.

        Runs all scrapers in an infinite loop with the specified
        interval between runs.

        Args:
            interval_minutes: Minutes to wait between scrape cycles.
                Default is 15 minutes.

        Note:
            This method runs indefinitely until interrupted.
            Use Ctrl+C or send SIGINT to stop.

        Example:
            >>> await runner.run_continuous(interval_minutes=15)
        """
        logger.info(f"Starting continuous scraping every {interval_minutes} minutes")

        while True:
            try:
                results = await self.run_once()
                logger.info(f"Scrape complete: {len(results['leaderboard'])} models")
                if results["errors"]:
                    logger.warning(f"Errors: {results['errors']}")
            except Exception as e:
                logger.error(f"Scrape cycle error: {e}")

            await asyncio.sleep(interval_minutes * 60)


async def main() -> None:
    """Main entry point for scraper.

    Sets up logging and runs a single scrape cycle.

    Example:
        >>> asyncio.run(main())
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    runner = ScraperRunner(headless=True)
    results = await runner.run_once()
    logger.info(f"Scrape results: {results}")


if __name__ == "__main__":
    asyncio.run(main())
