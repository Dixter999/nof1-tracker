"""Base scraper class with Playwright browser management.

This module provides the foundation for all nof1.ai scrapers using Playwright
for browser automation. It handles browser lifecycle, page management, and
common utilities.

Classes:
    BaseScraper: Base class for all scrapers with browser management.

Example:
    >>> async with BaseScraper(headless=True) as scraper:
    ...     async with scraper.new_page() as page:
    ...         await page.goto("https://nof1.ai")
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncIterator

from playwright.async_api import Browser, Page, Playwright, async_playwright

from nof1_tracker.database.config import scraper_settings


class BaseScraper:
    """Base class for all nof1.ai scrapers.

    Manages Playwright browser lifecycle and provides common utilities
    for web scraping operations.

    Attributes:
        BASE_URL: The base URL for nof1.ai site.
        headless: Whether to run browser in headless mode.
        timeout: Default page timeout in milliseconds.

    Example:
        >>> scraper = BaseScraper(headless=True)
        >>> await scraper.start()
        >>> async with scraper.new_page() as page:
        ...     await page.goto(scraper.BASE_URL)
        >>> await scraper.stop()

        Or using context manager:
        >>> async with BaseScraper() as scraper:
        ...     async with scraper.new_page() as page:
        ...         await page.goto(scraper.BASE_URL)
    """

    BASE_URL = "https://nof1.ai"

    def __init__(
        self,
        headless: bool | None = None,
        timeout: int | None = None,
    ) -> None:
        """Initialize the base scraper.

        Args:
            headless: Run browser in headless mode. Defaults to scraper_settings.
            timeout: Page load timeout in milliseconds. Defaults to scraper_settings.
        """
        self.headless = headless if headless is not None else scraper_settings.headless
        self.timeout = timeout if timeout is not None else scraper_settings.timeout
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None

    async def start(self) -> None:
        """Start the browser.

        Initializes Playwright and launches a Chromium browser instance.
        Must be called before using new_page().

        Raises:
            PlaywrightError: If browser fails to launch.
        """
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)

    async def stop(self) -> None:
        """Stop the browser and cleanup.

        Closes the browser and stops the Playwright instance.
        Safe to call multiple times.
        """
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    @asynccontextmanager
    async def new_page(self) -> AsyncIterator[Page]:
        """Create a new browser page as context manager.

        Yields:
            Page: A new Playwright page with default timeout configured.

        Raises:
            RuntimeError: If browser not started via start() or context manager.

        Example:
            >>> async with scraper.new_page() as page:
            ...     await page.goto("https://nof1.ai")
            ...     content = await page.content()
        """
        if not self._browser:
            raise RuntimeError("Browser not started. Call start() first.")
        page = await self._browser.new_page()
        page.set_default_timeout(self.timeout)
        try:
            yield page
        finally:
            await page.close()

    async def __aenter__(self) -> "BaseScraper":
        """Enter async context manager.

        Starts the browser automatically.

        Returns:
            BaseScraper: Self for use in async with statements.
        """
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Exit async context manager.

        Stops the browser automatically, even on exceptions.
        """
        await self.stop()

    @staticmethod
    def now_utc() -> datetime:
        """Get current UTC timestamp.

        Returns:
            datetime: Current time with UTC timezone.

        Example:
            >>> timestamp = BaseScraper.now_utc()
            >>> timestamp.tzinfo is not None
            True
        """
        return datetime.now(timezone.utc)
