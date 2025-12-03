"""Tests for the scraper CLI.

This module tests the Click-based CLI commands for running the scraper.
Tests verify command invocation, options parsing, and help text.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from click.testing import CliRunner

from nof1_tracker.cli import main, scrape, scrape_continuous


class TestCliHelp:
    """Test CLI help messages."""

    def test_main_help_displays(self) -> None:
        """Test that main command shows help text."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "NOF1 Tracker Scraper CLI" in result.output

    def test_scrape_help_displays(self) -> None:
        """Test that scrape command shows help text."""
        runner = CliRunner()
        result = runner.invoke(main, ["scrape", "--help"])
        assert result.exit_code == 0
        assert "Run scraper once" in result.output

    def test_scrape_continuous_help_displays(self) -> None:
        """Test that scrape-continuous command shows help text."""
        runner = CliRunner()
        result = runner.invoke(main, ["scrape-continuous", "--help"])
        assert result.exit_code == 0
        assert "Run scraper continuously" in result.output


class TestScrapeCommand:
    """Test the scrape command."""

    def test_scrape_default_headless(self) -> None:
        """Test that scrape uses headless by default."""
        runner = CliRunner()
        with patch("nof1_tracker.cli.ScraperRunner") as mock_runner_cls:
            mock_runner = MagicMock()
            mock_runner.run_once = AsyncMock(
                return_value={
                    "timestamp": "2024-01-01T00:00:00Z",
                    "leaderboard": ["Model1"],
                    "models": {},
                    "errors": [],
                }
            )
            mock_runner_cls.return_value = mock_runner

            result = runner.invoke(main, ["scrape"])
            assert result.exit_code == 0
            mock_runner_cls.assert_called_once_with(headless=True)

    def test_scrape_no_headless_option(self) -> None:
        """Test that --no-headless disables headless mode."""
        runner = CliRunner()
        with patch("nof1_tracker.cli.ScraperRunner") as mock_runner_cls:
            mock_runner = MagicMock()
            mock_runner.run_once = AsyncMock(
                return_value={
                    "timestamp": "2024-01-01T00:00:00Z",
                    "leaderboard": ["Model1"],
                    "models": {},
                    "errors": [],
                }
            )
            mock_runner_cls.return_value = mock_runner

            result = runner.invoke(main, ["scrape", "--no-headless"])
            assert result.exit_code == 0
            mock_runner_cls.assert_called_once_with(headless=False)

    def test_scrape_verbose_option(self) -> None:
        """Test that --verbose enables verbose output."""
        runner = CliRunner()
        with patch("nof1_tracker.cli.ScraperRunner") as mock_runner_cls:
            mock_runner = MagicMock()
            mock_runner.run_once = AsyncMock(
                return_value={
                    "timestamp": "2024-01-01T00:00:00Z",
                    "leaderboard": ["Model1", "Model2"],
                    "models": {"Model1": {"trades": 5}},
                    "errors": [],
                }
            )
            mock_runner_cls.return_value = mock_runner

            result = runner.invoke(main, ["scrape", "--verbose"])
            assert result.exit_code == 0
            # Verbose should show detailed output
            assert "Model1" in result.output or "model" in result.output.lower()

    def test_scrape_displays_summary(self) -> None:
        """Test that scrape displays a summary of results."""
        runner = CliRunner()
        with patch("nof1_tracker.cli.ScraperRunner") as mock_runner_cls:
            mock_runner = MagicMock()
            mock_runner.run_once = AsyncMock(
                return_value={
                    "timestamp": "2024-01-01T00:00:00Z",
                    "leaderboard": ["Model1", "Model2", "Model3"],
                    "models": {},
                    "errors": [],
                }
            )
            mock_runner_cls.return_value = mock_runner

            result = runner.invoke(main, ["scrape"])
            assert result.exit_code == 0
            assert "3" in result.output  # Should show count of scraped models


class TestScrapeContinuousCommand:
    """Test the scrape-continuous command."""

    def test_scrape_continuous_default_interval(self) -> None:
        """Test that scrape-continuous uses 15 minute default interval."""
        runner = CliRunner()
        with patch("nof1_tracker.cli.ScraperRunner") as mock_runner_cls:
            mock_runner = MagicMock()
            # Make run_continuous raise KeyboardInterrupt to exit the loop
            mock_runner.run_continuous = AsyncMock(side_effect=KeyboardInterrupt())
            mock_runner_cls.return_value = mock_runner

            result = runner.invoke(main, ["scrape-continuous"])
            # Should handle KeyboardInterrupt gracefully
            mock_runner.run_continuous.assert_called_once_with(interval_minutes=15)

    def test_scrape_continuous_custom_interval(self) -> None:
        """Test that --interval sets custom interval."""
        runner = CliRunner()
        with patch("nof1_tracker.cli.ScraperRunner") as mock_runner_cls:
            mock_runner = MagicMock()
            mock_runner.run_continuous = AsyncMock(side_effect=KeyboardInterrupt())
            mock_runner_cls.return_value = mock_runner

            result = runner.invoke(main, ["scrape-continuous", "--interval", "30"])
            mock_runner.run_continuous.assert_called_once_with(interval_minutes=30)

    def test_scrape_continuous_headless_option(self) -> None:
        """Test that headless option works for continuous scraping."""
        runner = CliRunner()
        with patch("nof1_tracker.cli.ScraperRunner") as mock_runner_cls:
            mock_runner = MagicMock()
            mock_runner.run_continuous = AsyncMock(side_effect=KeyboardInterrupt())
            mock_runner_cls.return_value = mock_runner

            result = runner.invoke(main, ["scrape-continuous", "--no-headless"])
            mock_runner_cls.assert_called_once_with(headless=False)


class TestCliErrorHandling:
    """Test CLI error handling."""

    def test_scrape_handles_errors(self) -> None:
        """Test that scrape handles errors gracefully."""
        runner = CliRunner()
        with patch("nof1_tracker.cli.ScraperRunner") as mock_runner_cls:
            mock_runner = MagicMock()
            mock_runner.run_once = AsyncMock(
                return_value={
                    "timestamp": "2024-01-01T00:00:00Z",
                    "leaderboard": [],
                    "models": {},
                    "errors": ["Connection failed", "Timeout error"],
                }
            )
            mock_runner_cls.return_value = mock_runner

            result = runner.invoke(main, ["scrape"])
            # Should still exit 0 but show errors
            assert "error" in result.output.lower() or "Error" in result.output

    def test_scrape_handles_exception(self) -> None:
        """Test that scrape handles unexpected exceptions."""
        runner = CliRunner()
        with patch("nof1_tracker.cli.ScraperRunner") as mock_runner_cls:
            mock_runner = MagicMock()
            mock_runner.run_once = AsyncMock(
                side_effect=Exception("Unexpected error")
            )
            mock_runner_cls.return_value = mock_runner

            result = runner.invoke(main, ["scrape"])
            assert result.exit_code != 0 or "error" in result.output.lower()
