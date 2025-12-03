"""CLI entry point for the scraper module.

Allows running the scraper via: python -m nof1_tracker.scraper

Usage:
    python -m nof1_tracker.scraper              # Run once
    python -m nof1_tracker.scraper --continuous # Run every 15 minutes
    python -m nof1_tracker.scraper --interval 5 # Run every 5 minutes
"""

import argparse
import asyncio
import logging
import sys

from nof1_tracker.scraper.runner import ScraperRunner


def main() -> int:
    """Main entry point for scraper CLI.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(
        description="NOF1 Tracker web scraper for nof1.ai Alpha Arena"
    )
    parser.add_argument(
        "--continuous",
        "-c",
        action="store_true",
        help="Run continuously at specified interval",
    )
    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=15,
        help="Interval between scrapes in minutes (default: 15)",
    )
    parser.add_argument(
        "--max-models",
        "-m",
        type=int,
        default=32,
        help="Maximum number of model pages to scrape (default: 32)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default: True)",
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Show browser window (useful for debugging)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    # Determine headless mode
    headless = not args.no_headless

    try:
        runner = ScraperRunner(
            headless=headless,
            max_models_to_scrape=args.max_models,
        )

        if args.continuous:
            logger.info(
                f"Starting continuous scraping every {args.interval} minutes "
                f"(max {args.max_models} models per run)"
            )
            asyncio.run(runner.run_continuous(interval_minutes=args.interval))
        else:
            logger.info(f"Running single scrape (max {args.max_models} models)")
            results = asyncio.run(runner.run_once())

            # Print summary
            print(f"\nScrape Results:")
            print(f"  Leaderboard: {len(results.get('leaderboard', []))} models")
            print(f"  Chats: {results.get('chats', 0)} entries")
            print(f"  Models scraped: {len(results.get('models', {}))}")

            if results.get("errors"):
                print(f"  Errors: {len(results['errors'])}")
                for error in results["errors"]:
                    print(f"    - {error}")
                return 1

        return 0

    except KeyboardInterrupt:
        logger.info("Scraper stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Scraper failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
