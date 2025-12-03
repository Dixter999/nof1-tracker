"""Click-based CLI for the NOF1 Tracker Scraper.

This module provides command-line interface commands for running
the web scraper in one-time or continuous mode.

Commands:
    scrape: Run scraper once
    scrape-continuous: Run scraper continuously at specified interval

Example:
    $ nof1 scrape --headless --verbose
    $ nof1 scrape-continuous --interval 30 --headless
"""

import asyncio
import logging
import sys
from typing import Any

import click

from nof1_tracker.scraper.runner import ScraperRunner


def setup_logging(verbose: bool) -> None:
    """Configure logging based on verbosity level.

    Args:
        verbose: If True, set DEBUG level; otherwise INFO level.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )


def format_results(results: dict[str, Any], verbose: bool) -> str:
    """Format scrape results for display.

    Args:
        results: Dictionary of scrape results from ScraperRunner.
        verbose: If True, include detailed model information.

    Returns:
        Formatted string for display.
    """
    lines = []
    lines.append(f"Timestamp: {results['timestamp']}")
    lines.append(f"Scraped {len(results['leaderboard'])} leaderboard entries")

    if verbose and results["leaderboard"]:
        lines.append("\nLeaderboard models:")
        for model in results["leaderboard"]:
            lines.append(f"  - {model}")

    if verbose and results["models"]:
        lines.append("\nModel details:")
        for model_name, data in results["models"].items():
            lines.append(f"  {model_name}: {data}")

    if results["errors"]:
        lines.append("\nErrors:")
        for error in results["errors"]:
            lines.append(f"  - {error}")

    return "\n".join(lines)


@click.group()
@click.version_option()
def main() -> None:
    """NOF1 Tracker Scraper CLI.

    CLI for running the NOF1.ai web scraper to collect leaderboard
    and model trading data.
    """
    pass


@main.command()
@click.option(
    "--headless/--no-headless",
    default=True,
    help="Run browser in headless mode (default: headless)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Enable verbose output with detailed results",
)
def scrape(headless: bool, verbose: bool) -> None:
    """Run scraper once.

    Scrapes the leaderboard and model pages once and saves
    results to the database.
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    try:
        runner = ScraperRunner(headless=headless)
        results = asyncio.run(runner.run_once())

        output = format_results(results, verbose)
        click.echo(output)

        if results["errors"]:
            logger.warning(f"Completed with {len(results['errors'])} errors")

    except Exception as e:
        logger.error(f"Scrape failed: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command("scrape-continuous")
@click.option(
    "--headless/--no-headless",
    default=True,
    help="Run browser in headless mode (default: headless)",
)
@click.option(
    "--interval",
    "-i",
    default=15,
    type=int,
    help="Interval between scrape cycles in minutes (default: 15)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Enable verbose output",
)
def scrape_continuous(headless: bool, interval: int, verbose: bool) -> None:
    """Run scraper continuously at specified interval.

    Starts continuous scraping loop that runs at the specified
    interval until interrupted with Ctrl+C.
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    click.echo(f"Starting continuous scraping every {interval} minutes")
    click.echo("Press Ctrl+C to stop")

    try:
        runner = ScraperRunner(headless=headless)
        asyncio.run(runner.run_continuous(interval_minutes=interval))
    except KeyboardInterrupt:
        click.echo("\nStopping continuous scraping...")
        logger.info("Continuous scraping stopped by user")
    except Exception as e:
        logger.error(f"Continuous scraping failed: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
