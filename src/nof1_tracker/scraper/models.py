"""Scraper for individual model pages (trades, positions, chat).

This module provides functionality to scrape detailed data from individual
model pages on nof1.ai, including trade history, current positions, and
model chat/reasoning logs.

Classes:
    TradeData: Dataclass representing a single trade.
    ModelChatData: Dataclass representing a model chat/decision entry.
    PositionData: Dataclass representing a current open position.
    ModelPageScraper: Scraper for model detail pages.

Example:
    >>> async with ModelPageScraper(headless=True) as scraper:
    ...     data = await scraper.scrape_model("Claude Sonnet 4.5")
    ...     print(f"Trades: {len(data['trades'])}")
    ...     print(f"Chats: {len(data['chats'])}")
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

from playwright.async_api import ElementHandle, Page

from nof1_tracker.scraper.base import BaseScraper


@dataclass
class TradeData:
    """Trade data from model page.

    Represents a single trade executed by an AI model.

    Attributes:
        trade_id: Unique identifier for the trade (if available).
        symbol: Trading symbol (e.g., "BTC-PERP").
        side: Trade direction ("long"/"short" or "buy"/"sell").
        entry_price: Price at trade entry.
        exit_price: Price at trade exit (None if still open).
        size: Position size in base currency.
        leverage: Leverage multiplier used (optional).
        pnl: Realized profit/loss in USD (optional).
        pnl_percent: Realized profit/loss as percentage (optional).
        status: Trade status ("open", "closed", "liquidated").
        opened_at: Timestamp when trade was opened.
        closed_at: Timestamp when trade was closed (None if open).
        raw_data: Original scraped data for debugging.
    """

    trade_id: str | None
    symbol: str
    side: str  # "long" or "short" / "buy" or "sell"
    entry_price: Decimal
    exit_price: Decimal | None
    size: Decimal
    leverage: int | None
    pnl: Decimal | None
    pnl_percent: Decimal | None
    status: str  # "open", "closed", "liquidated"
    opened_at: datetime
    closed_at: datetime | None
    raw_data: dict[str, Any]


@dataclass
class ModelChatData:
    """Model chat/reasoning data.

    Represents a single chat or decision entry from a model's reasoning log.

    Attributes:
        timestamp: When the chat entry was created.
        content: The full text content of the chat/reasoning.
        decision: Trading decision if any ("buy", "sell", "hold", "close", "none").
        symbol: Trading symbol related to the decision (optional).
        confidence: Model's confidence in the decision (0-100, optional).
        raw_data: Original scraped data for debugging.
    """

    timestamp: datetime
    content: str
    decision: str | None  # "buy", "sell", "hold", "close", "none"
    symbol: str | None
    confidence: Decimal | None
    raw_data: dict[str, Any]


@dataclass
class PositionData:
    """Current open position.

    Represents a currently open position held by a model.

    Attributes:
        symbol: Trading symbol (e.g., "BTC-PERP").
        side: Position direction ("long" or "short").
        size: Position size in base currency.
        entry_price: Average entry price.
        current_price: Current market price.
        unrealized_pnl: Unrealized profit/loss in USD.
        leverage: Leverage multiplier used (optional).
    """

    symbol: str
    side: str
    size: Decimal
    entry_price: Decimal
    current_price: Decimal
    unrealized_pnl: Decimal
    leverage: int | None


class ModelPageScraper(BaseScraper):
    """Scraper for individual model pages.

    Extracts detailed data from model-specific pages including trades,
    positions, and chat/reasoning history.

    Attributes:
        MODEL_SLUGS: Mapping of model names to URL slugs.

    Example:
        >>> async with ModelPageScraper() as scraper:
        ...     # Scrape all data for a model
        ...     data = await scraper.scrape_model("Claude Sonnet 4.5")
        ...
        ...     # Or scrape specific data types
        ...     trades = await scraper.scrape_trades("GPT-5")
    """

    MODEL_SLUGS: dict[str, str] = {
        "DeepSeek V3.1": "deepseek-chat-v3.1",
        "Qwen3 Max": "qwen3-max",
        "Claude Sonnet 4.5": "claude-sonnet-4-5",
        "Grok 4": "grok-4",
        "GPT-5": "gpt-5",
        "Gemini 2.5 Pro": "gemini-2-5-pro",
    }

    def get_model_url(self, model_name: str) -> str:
        """Get URL for a model's page.

        Args:
            model_name: Display name of the model.

        Returns:
            Full URL to the model's detail page.

        Example:
            >>> scraper = ModelPageScraper()
            >>> scraper.get_model_url("Claude Sonnet 4.5")
            'https://nof1.ai/models/claude-sonnet-4-5'
        """
        slug = self.MODEL_SLUGS.get(model_name, model_name.lower().replace(" ", "-"))
        return f"{self.BASE_URL}/models/{slug}"

    async def scrape_model(self, model_name: str) -> dict[str, Any]:
        """Scrape all data for a specific model.

        Navigates to the model's page and extracts trades, positions,
        and chat/reasoning history.

        Args:
            model_name: Display name of the model to scrape.

        Returns:
            Dictionary containing:
                - model_name: The model name
                - trades: List of TradeData
                - positions: List of PositionData
                - chats: List of ModelChatData
                - scraped_at: Timestamp of scrape

        Raises:
            TimeoutError: If page fails to load within timeout.
        """
        async with self.new_page() as page:
            url = self.get_model_url(model_name)
            await page.goto(url)
            await page.wait_for_load_state("networkidle")

            trades = await self._scrape_trades(page)
            positions = await self._scrape_positions(page)
            chats = await self._scrape_model_chat(page)

            return {
                "model_name": model_name,
                "trades": trades,
                "positions": positions,
                "chats": chats,
                "scraped_at": self.now_utc(),
            }

    async def scrape_model_by_url(self, model_url: str) -> dict[str, Any]:
        """Scrape all data for a model using its direct URL.

        Navigates directly to the model's URL (e.g., /models/23) and
        extracts trades, positions, and chat/reasoning history.

        Args:
            model_url: URL path to the model page (e.g., "/models/23").

        Returns:
            Dictionary containing:
                - trades: List of TradeData
                - positions: List of PositionData
                - chats: List of ModelChatData
                - scraped_at: Timestamp of scrape

        Raises:
            TimeoutError: If page fails to load within timeout.
        """
        import asyncio

        async with self.new_page() as page:
            # Build full URL from path
            full_url = (
                f"{self.BASE_URL}{model_url}"
                if model_url.startswith("/")
                else model_url
            )
            await page.goto(full_url)
            await page.wait_for_load_state("networkidle")

            # Wait a bit for dynamic content to load
            await asyncio.sleep(2)

            trades = await self._scrape_trades(page)
            positions = await self._scrape_positions(page)
            chats = await self._scrape_model_chat(page)

            return {
                "trades": trades,
                "positions": positions,
                "chats": chats,
                "scraped_at": self.now_utc(),
            }

    async def scrape_trades(self, model_name: str) -> list[TradeData]:
        """Scrape trade history for a model.

        Args:
            model_name: Display name of the model.

        Returns:
            List of trade records for the model.
        """
        async with self.new_page() as page:
            url = self.get_model_url(model_name)
            await page.goto(url)
            await page.wait_for_load_state("networkidle")
            return await self._scrape_trades(page)

    async def _scrape_trades(self, page: Page) -> list[TradeData]:
        """Parse trades from page.

        Actual nof1.ai trade structure uses CSS Grid (div.grid.grid-cols-10):
        - Column 0: SIDE (LONG/SHORT)
        - Column 1: COIN (symbol like AMZN)
        - Column 2: ENTRY PRICE ($235.02)
        - Column 3: EXIT PRICE ($235.13)
        - Column 4: QUANTITY (2.34)
        - Column 5: HOLDING TIME (35M)
        - Column 6: NOTIONAL ENTRY ($549.95)
        - Column 7: NOTIONAL EXIT ($550.20)
        - Column 8: TOTAL FEES ($0.09)
        - Column 9: NET P&L ($0.26)

        Args:
            page: The browser page to scrape from.

        Returns:
            List of TradeData objects.
        """
        import re

        trades = []

        try:
            # Find trade rows inside the space-y-3 container (data rows)
            # The header is grid-cols-10 with text-[10px], data rows are text-[12px]
            trade_rows = await page.query_selector_all(
                "div.space-y-3 > div.grid.grid-cols-10"
            )

            for row in trade_rows:
                cells = await row.query_selector_all(":scope > div")
                if len(cells) >= 10:
                    try:
                        # Extract data from cells
                        side_text = await cells[0].inner_text()
                        side = side_text.strip().lower()

                        symbol_text = await cells[1].inner_text()
                        symbol = symbol_text.strip()

                        entry_text = await cells[2].inner_text()
                        entry_price = Decimal(re.sub(r"[$,]", "", entry_text).strip())

                        exit_text = await cells[3].inner_text()
                        exit_cleaned = re.sub(r"[$,]", "", exit_text).strip()
                        exit_price = (
                            Decimal(exit_cleaned)
                            if exit_cleaned and exit_cleaned != "-"
                            else None
                        )

                        qty_text = await cells[4].inner_text()
                        size = Decimal(re.sub(r"[,]", "", qty_text).strip())

                        # Column 9: NET P&L
                        pnl_text = await cells[9].inner_text()
                        pnl_cleaned = re.sub(r"[$,]", "", pnl_text).strip()
                        pnl = (
                            Decimal(pnl_cleaned)
                            if pnl_cleaned and pnl_cleaned != "-"
                            else None
                        )

                        trade = TradeData(
                            trade_id=None,
                            symbol=symbol,
                            side=side,
                            entry_price=entry_price,
                            exit_price=exit_price,
                            size=size,
                            leverage=None,
                            pnl=pnl,
                            pnl_percent=None,
                            status="closed" if exit_price else "open",
                            opened_at=self.now_utc(),
                            closed_at=self.now_utc() if exit_price else None,
                            raw_data={"symbol": symbol, "side": side},
                        )
                        trades.append(trade)

                    except Exception as e:
                        print(f"Error parsing trade row: {e}")
                        continue

        except Exception as e:
            print(f"Error scraping trades: {e}")

        return trades

    async def _parse_trade_row(self, row: ElementHandle) -> TradeData | None:
        """Parse a single trade row.

        Args:
            row: Element handle for the trade row.

        Returns:
            TradeData if parsing succeeds, None otherwise.
        """
        try:
            # Extract trade ID if available
            trade_id_el = await row.query_selector('[data-testid="trade-id"]')
            trade_id = await trade_id_el.inner_text() if trade_id_el else None

            # Extract symbol
            symbol_el = await row.query_selector('[data-testid="symbol"]')
            symbol = (await symbol_el.inner_text() if symbol_el else "UNKNOWN").strip()

            # Extract side
            side_el = await row.query_selector('[data-testid="side"]')
            side = (await side_el.inner_text() if side_el else "long").strip().lower()

            # Extract prices
            entry_el = await row.query_selector('[data-testid="entry-price"]')
            entry_text = await entry_el.inner_text() if entry_el else "0"
            entry_price = Decimal(entry_text.replace("$", "").replace(",", "").strip())

            exit_el = await row.query_selector('[data-testid="exit-price"]')
            exit_price = None
            if exit_el:
                exit_text = await exit_el.inner_text()
                if exit_text and exit_text.strip() not in ("-", "", "N/A"):
                    exit_price = Decimal(
                        exit_text.replace("$", "").replace(",", "").strip()
                    )

            # Extract size
            size_el = await row.query_selector('[data-testid="size"]')
            size_text = await size_el.inner_text() if size_el else "0"
            size = Decimal(size_text.replace(",", "").strip())

            # Extract leverage
            leverage_el = await row.query_selector('[data-testid="leverage"]')
            leverage = None
            if leverage_el:
                lev_text = await leverage_el.inner_text()
                lev_cleaned = lev_text.replace("x", "").strip()
                if lev_cleaned.isdigit():
                    leverage = int(lev_cleaned)

            # Extract PnL
            pnl_el = await row.query_selector('[data-testid="pnl"]')
            pnl = None
            if pnl_el:
                pnl_text = await pnl_el.inner_text()
                pnl_cleaned = pnl_text.replace("$", "").replace(",", "").strip()
                if pnl_cleaned and pnl_cleaned not in ("-", "", "N/A"):
                    pnl = Decimal(pnl_cleaned)

            pnl_pct_el = await row.query_selector('[data-testid="pnl-percent"]')
            pnl_percent = None
            if pnl_pct_el:
                pct_text = await pnl_pct_el.inner_text()
                pct_cleaned = pct_text.replace("%", "").strip()
                if pct_cleaned and pct_cleaned not in ("-", "", "N/A"):
                    pnl_percent = Decimal(pct_cleaned)

            # Extract status
            status_el = await row.query_selector('[data-testid="status"]')
            status = (
                (await status_el.inner_text() if status_el else "open").strip().lower()
            )

            return TradeData(
                trade_id=trade_id,
                symbol=symbol,
                side=side,
                entry_price=entry_price,
                exit_price=exit_price,
                size=size,
                leverage=leverage,
                pnl=pnl,
                pnl_percent=pnl_percent,
                status=status,
                opened_at=self.now_utc(),
                closed_at=self.now_utc() if exit_price else None,
                raw_data={},
            )
        except Exception as e:
            print(f"Error parsing trade row: {e}")
            return None

    async def _scrape_positions(self, page: Page) -> list[PositionData]:
        """Parse current positions from page.

        Actual nof1.ai position structure (ACTIVE POSITIONS section):
        Positions are displayed as cards with format:
        - LONG/SHORT + SYMBOL
        - EXIT PLAN button
        - ENTRY TIME: HH:MM:SS
        - ENTRY PRICE: $XXX.XX
        - QUANTITY: X.XXX
        - LEVERAGE: XXX
        - LIQUIDATION: $XXX.XX
        - MARGIN: $XXX.XX
        - UNREALIZED P&L: $XX.XX

        Args:
            page: The browser page to scrape from.

        Returns:
            List of PositionData objects.
        """
        import re

        positions = []

        # Get all text from page and look for position patterns
        try:
            # Find text content that looks like positions
            body_text = await page.inner_text("body")

            # Split by common position indicators
            if "ACTIVE POSITIONS" in body_text:
                # Find all position blocks
                # Pattern: LONG/SHORT followed by symbol
                position_pattern = r"(LONG|SHORT)\s+([A-Z]+)\s+EXIT PLAN.*?ENTRY PRICE\s*\$?([\d,]+\.?\d*)\s*.*?QUANTITY\s*([\d,]+\.?\d*)\s*.*?LEVERAGE\s*(\d+)X.*?UNREALIZED P&L[:\s]*\$?([-\d,]+\.?\d*)"

                matches = re.findall(position_pattern, body_text, re.DOTALL)

                for match in matches:
                    try:
                        side = match[0].lower()
                        symbol = match[1]
                        entry_price = Decimal(match[2].replace(",", ""))
                        size = Decimal(match[3].replace(",", ""))
                        leverage = int(match[4])
                        unrealized_pnl = Decimal(match[5].replace(",", ""))

                        position = PositionData(
                            symbol=symbol,
                            side=side,
                            size=size,
                            entry_price=entry_price,
                            current_price=entry_price,  # Approximate
                            unrealized_pnl=unrealized_pnl,
                            leverage=leverage,
                        )
                        positions.append(position)
                    except Exception as e:
                        print(f"Error parsing position match: {e}")
                        continue

        except Exception as e:
            print(f"Error scraping positions: {e}")

        return positions

    async def _parse_position_row(self, row: ElementHandle) -> PositionData | None:
        """Parse a single position row.

        Args:
            row: Element handle for the position row.

        Returns:
            PositionData if parsing succeeds, None otherwise.
        """
        try:
            symbol_el = await row.query_selector('[data-testid="symbol"]')
            symbol = (await symbol_el.inner_text() if symbol_el else "UNKNOWN").strip()

            side_el = await row.query_selector('[data-testid="side"]')
            side = (await side_el.inner_text() if side_el else "long").strip().lower()

            size_el = await row.query_selector('[data-testid="size"]')
            size_text = await size_el.inner_text() if size_el else "0"
            size = Decimal(size_text.replace(",", "").strip())

            entry_el = await row.query_selector('[data-testid="entry-price"]')
            entry_text = await entry_el.inner_text() if entry_el else "0"
            entry_price = Decimal(entry_text.replace("$", "").replace(",", "").strip())

            current_el = await row.query_selector('[data-testid="current-price"]')
            current_text = await current_el.inner_text() if current_el else "0"
            current_price = Decimal(
                current_text.replace("$", "").replace(",", "").strip()
            )

            upnl_el = await row.query_selector('[data-testid="unrealized-pnl"]')
            upnl_text = await upnl_el.inner_text() if upnl_el else "0"
            unrealized_pnl = Decimal(
                upnl_text.replace("$", "").replace(",", "").strip()
            )

            leverage_el = await row.query_selector('[data-testid="leverage"]')
            leverage = None
            if leverage_el:
                lev_text = await leverage_el.inner_text()
                lev_cleaned = lev_text.replace("x", "").strip()
                if lev_cleaned.isdigit():
                    leverage = int(lev_cleaned)

            return PositionData(
                symbol=symbol,
                side=side,
                size=size,
                entry_price=entry_price,
                current_price=current_price,
                unrealized_pnl=unrealized_pnl,
                leverage=leverage,
            )
        except Exception as e:
            print(f"Error parsing position row: {e}")
            return None

    async def _scrape_model_chat(self, page: Page) -> list[ModelChatData]:
        """Parse model chat/reasoning from page.

        Args:
            page: The browser page to scrape from.

        Returns:
            List of ModelChatData objects.
        """
        chats = []

        # Click on chat/reasoning tab if exists
        try:
            chat_tab = await page.query_selector('[data-testid="chat-tab"]')
            if not chat_tab:
                chat_tab = await page.query_selector(
                    'button:has-text("Chat"), button:has-text("Reasoning")'
                )
            if chat_tab:
                await chat_tab.click()
                await page.wait_for_timeout(1000)
        except Exception:
            pass

        # Parse chat entries
        try:
            entries = await page.query_selector_all('[data-testid="chat-entry"]')
            if not entries:
                entries = await page.query_selector_all(".chat-entry, .reasoning-entry")

            for entry in entries:
                chat = await self._parse_chat_entry(entry)
                if chat:
                    chats.append(chat)
        except Exception as e:
            print(f"Error scraping chat: {e}")

        return chats

    async def _parse_chat_entry(self, entry: ElementHandle) -> ModelChatData | None:
        """Parse a single chat entry.

        Args:
            entry: Element handle for the chat entry.

        Returns:
            ModelChatData if parsing succeeds, None otherwise.
        """
        try:
            # Extract content
            content_el = await entry.query_selector('[data-testid="content"]')
            if not content_el:
                content_el = await entry.query_selector(".content, p")
            content = await content_el.inner_text() if content_el else ""

            # Extract decision
            decision_el = await entry.query_selector('[data-testid="decision"]')
            decision = None
            if decision_el:
                decision = (await decision_el.inner_text()).strip().lower()
                if decision not in ("buy", "sell", "hold", "close", "none"):
                    decision = "none"

            # Extract symbol
            symbol_el = await entry.query_selector('[data-testid="symbol"]')
            symbol = (await symbol_el.inner_text()).strip() if symbol_el else None

            # Extract confidence
            conf_el = await entry.query_selector('[data-testid="confidence"]')
            confidence = None
            if conf_el:
                conf_text = await conf_el.inner_text()
                conf_cleaned = conf_text.replace("%", "").strip()
                if conf_cleaned:
                    try:
                        confidence = Decimal(conf_cleaned)
                    except Exception:
                        pass

            return ModelChatData(
                timestamp=self.now_utc(),
                content=content,
                decision=decision,
                symbol=symbol,
                confidence=confidence,
                raw_data={},
            )
        except Exception as e:
            print(f"Error parsing chat entry: {e}")
            return None
