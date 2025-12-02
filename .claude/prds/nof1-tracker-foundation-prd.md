---
name: nof1-tracker-foundation
description: Foundation setup for tracking and analyzing LLM trading performance from nof1.ai Alpha Arena
priority: P1
status: draft
created: 2025-12-02
author: user
---

# PRD: nof1-tracker Foundation

## Project Overview

**Project Name:** nof1-tracker
**Purpose:** Track and analyze LLM trading performance from nof1.ai Alpha Arena
**Data Source:** https://nof1.ai/leaderboard

### What is Alpha Arena?

Alpha Arena is a real-money benchmark where top LLMs ($10k each) trade perpetual futures on Hyperliquid DEX. This project scrapes, stores, and analyzes:

- **Leaderboard rankings** (P&L, ROI, total assets)
- **Trade history** (positions, entries/exits, leverage)
- **ModelChat** (AI's internal decision reasoning)
- **Season performance** (multi-season tracking)

### Models Tracked

| Model | Provider |
|-------|----------|
| DeepSeek V3.1 | DeepSeek |
| Qwen3 Max | Alibaba |
| Claude Sonnet 4.5 | Anthropic |
| Grok 4 | xAI |
| GPT-5 | OpenAI |
| Gemini 2.5 Pro | Google |

---

## Task 001: Project Setup and PostgreSQL Foundation

### Description

Create the foundational project structure with PostgreSQL database connectivity, Docker containerization, and SQLAlchemy ORM models for storing Alpha Arena trading data.

### TDD Requirements

**This project uses Test-Driven Development. You MUST:**
1. **RED**: Write failing test first
2. **GREEN**: Write minimal code to make test pass
3. **REFACTOR**: Clean up code while keeping tests green

### Acceptance Criteria

- [ ] Project structure matches specification below
- [ ] `pyproject.toml` with all dependencies
- [ ] `.env.example` with database configuration
- [ ] Docker Compose with PostgreSQL 16 service
- [ ] SQLAlchemy models for all entities
- [ ] Database connection manager with pooling
- [ ] Alembic migrations initialized
- [ ] All tests pass (`pytest`)
- [ ] Linters pass (`black`, `ruff`)

---

## Technical Specification

### Directory Structure

```
nof1-tracker/
├── .claude/
│   └── commands/          # Custom slash commands
├── .github/
│   └── workflows/         # CI/CD pipelines
├── src/
│   └── nof1_tracker/
│       ├── __init__.py
│       ├── main.py                    # CLI orchestrator
│       ├── scraper/
│       │   ├── __init__.py
│       │   ├── leaderboard.py         # Leaderboard scraper
│       │   ├── trades.py              # Trade history scraper
│       │   └── model_chat.py          # ModelChat scraper
│       ├── database/
│       │   ├── __init__.py
│       │   ├── config.py              # Pydantic config
│       │   ├── connection.py          # Connection manager
│       │   ├── models.py              # SQLAlchemy models
│       │   └── repositories.py        # Data access layer
│       └── analyzer/
│           ├── __init__.py
│           └── performance.py         # Performance analytics
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Pytest fixtures
│   ├── test_database/
│   │   ├── __init__.py
│   │   ├── test_connection.py
│   │   └── test_models.py
│   └── test_scraper/
│       └── __init__.py
├── migrations/
│   └── versions/                      # Alembic migrations
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

---

### pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "nof1-tracker"
version = "0.1.0"
description = "Track and analyze LLM trading performance from nof1.ai Alpha Arena"
readme = "README.md"
requires-python = ">=3.11"
license = "MIT"
authors = [
    { name = "Your Name", email = "your@email.com" }
]
keywords = ["llm", "trading", "alpha-arena", "nof1", "crypto"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "playwright>=1.40.0",
    "sqlalchemy>=2.0.0",
    "psycopg2-binary>=2.9.9",
    "alembic>=1.13.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "httpx>=0.27.0",
    "rich>=13.0.0",
    "typer>=0.12.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.23.0",
    "black>=24.0.0",
    "ruff>=0.3.0",
    "mypy>=1.8.0",
    "types-psycopg2>=2.9.0",
    "pre-commit>=3.6.0",
]

[project.scripts]
nof1-tracker = "nof1_tracker.main:app"

[tool.hatch.build.targets.wheel]
packages = ["src/nof1_tracker"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-v --cov=nof1_tracker --cov-report=term-missing"

[tool.black]
line-length = 88
target-version = ['py311', 'py312']

[tool.ruff]
line-length = 88
target-version = "py311"
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_ignores = true
```

---

### .env.example

```env
# ===========================================
# NOF1 TRACKER DATABASE CONFIGURATION
# ===========================================

# PostgreSQL Connection
NOF1_DB_HOST=localhost
NOF1_DB_PORT=5432
NOF1_DB_NAME=nof1_tracker
NOF1_DB_USER=nof1_user
NOF1_DB_PASSWORD=your_secure_password_here

# Connection Pool Settings
NOF1_DB_POOL_SIZE=5
NOF1_DB_MAX_OVERFLOW=10

# ===========================================
# SCRAPER CONFIGURATION
# ===========================================

# Playwright settings
SCRAPER_HEADLESS=true
SCRAPER_TIMEOUT=30000

# Rate limiting (requests per minute)
SCRAPER_RATE_LIMIT=30

# ===========================================
# APPLICATION SETTINGS
# ===========================================

# Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Data refresh interval (minutes)
REFRESH_INTERVAL=15
```

---

### docker-compose.yml

```yaml
version: "3.8"

services:
  # ===========================================
  # PostgreSQL Database
  # ===========================================
  postgres:
    image: postgres:16-alpine
    container_name: nof1-tracker-db
    environment:
      POSTGRES_USER: ${NOF1_DB_USER:-nof1_user}
      POSTGRES_PASSWORD: ${NOF1_DB_PASSWORD:-nof1_password}
      POSTGRES_DB: ${NOF1_DB_NAME:-nof1_tracker}
    ports:
      - "${NOF1_DB_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./migrations/init:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${NOF1_DB_USER:-nof1_user} -d ${NOF1_DB_NAME:-nof1_tracker}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # ===========================================
  # Application Service
  # ===========================================
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: nof1-tracker-app
    env_file:
      - .env
    environment:
      # Override host for Docker networking
      NOF1_DB_HOST: postgres
    volumes:
      - ./src:/app/src:ro
    depends_on:
      postgres:
        condition: service_healthy
    command: ["python", "-m", "nof1_tracker.main", "--help"]

  # ===========================================
  # Scraper Service (run on-demand)
  # ===========================================
  scraper:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: nof1-tracker-scraper
    env_file:
      - .env
    environment:
      NOF1_DB_HOST: postgres
    profiles:
      - scraper
    depends_on:
      postgres:
        condition: service_healthy
    command: >
      python -m nof1_tracker.main scrape
      --leaderboard
      --trades
      --model-chat

  # ===========================================
  # Continuous Monitor (daemon)
  # ===========================================
  monitor:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: nof1-tracker-monitor
    env_file:
      - .env
    environment:
      NOF1_DB_HOST: postgres
    profiles:
      - monitor
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped
    command: >
      python -m nof1_tracker.main monitor
      --interval ${REFRESH_INTERVAL:-15}
    healthcheck:
      test: ["CMD", "python", "-c", "from nof1_tracker.database import get_session; get_session()"]
      interval: 60s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
    driver: local
```

---

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

# Install Playwright browsers
RUN playwright install chromium --with-deps

# Copy source code
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY tests/ ./tests/

# Set Python path
ENV PYTHONPATH=/app/src

# Default command
CMD ["python", "-m", "nof1_tracker.main", "--help"]
```

---

### Database Models (src/nof1_tracker/database/models.py)

```python
"""
SQLAlchemy ORM models for nof1-tracker database.

Stores Alpha Arena leaderboard data, trade history, and model chat logs.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Season(Base):
    """Alpha Arena competition season.

    Attributes:
        id: Primary key
        season_number: Season identifier (1, 2, 3...)
        name: Season name (e.g., "Season 1")
        start_date: Season start timestamp
        end_date: Season end timestamp (null if ongoing)
        initial_capital: Starting capital per model ($10,000)
        status: active, completed, cancelled
    """

    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    season_number = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    initial_capital = Column(Numeric(15, 2), default=Decimal("10000.00"))
    status = Column(
        Enum("active", "completed", "cancelled", name="season_status"),
        default="active",
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    snapshots = relationship("LeaderboardSnapshot", back_populates="season")

    def __repr__(self) -> str:
        return f"<Season(id={self.id}, number={self.season_number}, status={self.status})>"


class LLMModel(Base):
    """LLM model participating in Alpha Arena.

    Attributes:
        id: Primary key
        name: Model name (e.g., "DeepSeek V3.1")
        provider: Model provider (e.g., "DeepSeek", "Anthropic")
        model_id: Internal identifier used by nof1.ai
        is_active: Whether model is currently competing
    """

    __tablename__ = "llm_models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    provider = Column(String(100), nullable=False)
    model_id = Column(String(100), unique=True, nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    snapshots = relationship("LeaderboardSnapshot", back_populates="model")
    trades = relationship("Trade", back_populates="model")
    model_chats = relationship("ModelChat", back_populates="model")

    def __repr__(self) -> str:
        return f"<LLMModel(id={self.id}, name={self.name}, provider={self.provider})>"


class LeaderboardSnapshot(Base):
    """Point-in-time snapshot of leaderboard standings.

    Captured periodically to track performance over time.

    Attributes:
        id: Primary key
        season_id: FK to seasons table
        model_id: FK to llm_models table
        timestamp: When snapshot was taken
        rank: Current leaderboard position (1 = first)
        total_assets: Total portfolio value in USD
        pnl: Profit/Loss in USD
        pnl_percent: Profit/Loss percentage
        roi: Return on Investment percentage
        win_rate: Percentage of winning trades
        total_trades: Total number of trades
    """

    __tablename__ = "leaderboard_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False, index=True)
    model_id = Column(Integer, ForeignKey("llm_models.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    rank = Column(Integer, nullable=False)
    total_assets = Column(Numeric(15, 2), nullable=False)
    pnl = Column(Numeric(15, 2), nullable=True)
    pnl_percent = Column(Numeric(8, 4), nullable=True)
    roi = Column(Numeric(8, 4), nullable=True)
    win_rate = Column(Numeric(5, 2), nullable=True)
    total_trades = Column(Integer, nullable=True)
    raw_data = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    season = relationship("Season", back_populates="snapshots")
    model = relationship("LLMModel", back_populates="snapshots")

    # Unique constraint: one snapshot per model per timestamp
    __table_args__ = (
        UniqueConstraint("model_id", "timestamp", name="uq_model_timestamp"),
    )

    def __repr__(self) -> str:
        return f"<LeaderboardSnapshot(id={self.id}, model_id={self.model_id}, rank={self.rank})>"


class Trade(Base):
    """Individual trade executed by an LLM model.

    Attributes:
        id: Primary key
        model_id: FK to llm_models table
        trade_id: External trade identifier from nof1.ai
        symbol: Trading pair (e.g., "BTC-PERP", "ETH-PERP")
        side: "long" or "short"
        entry_price: Price at position open
        exit_price: Price at position close (null if open)
        size: Position size in units
        leverage: Leverage multiplier used
        pnl: Realized P&L (null if open)
        pnl_percent: Realized P&L percentage (null if open)
        status: open, closed, liquidated
        opened_at: When position was opened
        closed_at: When position was closed (null if open)
    """

    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey("llm_models.id"), nullable=False, index=True)
    trade_id = Column(String(100), unique=True, nullable=True, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    side = Column(Enum("long", "short", name="trade_side"), nullable=False)
    entry_price = Column(Numeric(20, 8), nullable=False)
    exit_price = Column(Numeric(20, 8), nullable=True)
    size = Column(Numeric(20, 8), nullable=False)
    leverage = Column(Numeric(5, 2), nullable=True)
    pnl = Column(Numeric(15, 2), nullable=True)
    pnl_percent = Column(Numeric(8, 4), nullable=True)
    status = Column(
        Enum("open", "closed", "liquidated", name="trade_status"),
        default="open",
    )
    opened_at = Column(DateTime, nullable=False, index=True)
    closed_at = Column(DateTime, nullable=True)
    raw_data = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    model = relationship("LLMModel", back_populates="trades")

    def __repr__(self) -> str:
        return f"<Trade(id={self.id}, symbol={self.symbol}, side={self.side}, status={self.status})>"


class ModelChat(Base):
    """AI model's internal decision reasoning (ModelChat).

    Stores the AI's thought process when making trading decisions.

    Attributes:
        id: Primary key
        model_id: FK to llm_models table
        timestamp: When reasoning was generated
        content: Full text of model's reasoning
        decision: Resulting action (buy, sell, hold, close)
        symbol: Related trading pair (if applicable)
        confidence: Model's stated confidence (if available)
    """

    __tablename__ = "model_chats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey("llm_models.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    content = Column(Text, nullable=False)
    decision = Column(
        Enum("buy", "sell", "hold", "close", "none", name="chat_decision"),
        nullable=True,
    )
    symbol = Column(String(50), nullable=True)
    confidence = Column(Numeric(5, 2), nullable=True)
    raw_data = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    model = relationship("LLMModel", back_populates="model_chats")

    def __repr__(self) -> str:
        return f"<ModelChat(id={self.id}, model_id={self.model_id}, decision={self.decision})>"
```

---

### Database Config (src/nof1_tracker/database/config.py)

```python
"""
Database configuration using Pydantic Settings.

Loads settings from environment variables with validation.
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """PostgreSQL database configuration.

    Loads from environment variables with NOF1_DB_ prefix.
    """

    host: str = Field(default="localhost", alias="NOF1_DB_HOST")
    port: int = Field(default=5432, alias="NOF1_DB_PORT")
    name: str = Field(default="nof1_tracker", alias="NOF1_DB_NAME")
    user: str = Field(default="nof1_user", alias="NOF1_DB_USER")
    password: str = Field(default="", alias="NOF1_DB_PASSWORD")
    pool_size: int = Field(default=5, alias="NOF1_DB_POOL_SIZE")
    max_overflow: int = Field(default=10, alias="NOF1_DB_MAX_OVERFLOW")

    @field_validator("pool_size")
    @classmethod
    def validate_pool_size(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("pool_size must be greater than 0")
        return v

    @field_validator("max_overflow")
    @classmethod
    def validate_max_overflow(cls, v: int) -> int:
        if v < 0:
            raise ValueError("max_overflow must be non-negative")
        return v

    @property
    def url(self) -> str:
        """Generate PostgreSQL connection URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def async_url(self) -> str:
        """Generate async PostgreSQL connection URL."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class ScraperSettings(BaseSettings):
    """Scraper configuration."""

    headless: bool = Field(default=True, alias="SCRAPER_HEADLESS")
    timeout: int = Field(default=30000, alias="SCRAPER_TIMEOUT")
    rate_limit: int = Field(default=30, alias="SCRAPER_RATE_LIMIT")

    class Config:
        env_file = ".env"
        extra = "ignore"


class AppSettings(BaseSettings):
    """Application-wide settings."""

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    refresh_interval: int = Field(default=15, alias="REFRESH_INTERVAL")

    class Config:
        env_file = ".env"
        extra = "ignore"


# Singleton instances
db_settings = DatabaseSettings()
scraper_settings = ScraperSettings()
app_settings = AppSettings()
```

---

### Database Connection (src/nof1_tracker/database/connection.py)

```python
"""
Database connection utilities.

Provides session management and connection pooling for PostgreSQL.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .config import db_settings
from .models import Base


def create_db_engine(database_url: str | None = None) -> Engine:
    """Create SQLAlchemy engine with connection pooling.

    Args:
        database_url: Optional database URL. Uses settings if not provided.

    Returns:
        SQLAlchemy Engine instance with pooling configured.
    """
    url = database_url or db_settings.url
    return create_engine(
        url,
        pool_size=db_settings.pool_size,
        max_overflow=db_settings.max_overflow,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=3600,   # Recycle connections after 1 hour
    )


# Module-level engine (lazy initialization)
_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


def _get_engine() -> Engine:
    """Get or create the database engine (singleton)."""
    global _engine
    if _engine is None:
        _engine = create_db_engine()
    return _engine


def get_session_maker() -> sessionmaker:
    """Get or create the session maker (singleton).

    Returns:
        SQLAlchemy sessionmaker configured for the database.
    """
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=_get_engine(),
        )
    return _SessionLocal


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Get a database session as a context manager.

    Yields:
        SQLAlchemy Session instance.

    Example:
        with get_session() as session:
            models = session.query(LLMModel).all()
    """
    session_maker = get_session_maker()
    session = session_maker()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Initialize database tables.

    Creates all tables defined in models if they don't exist.
    For production, use Alembic migrations instead.
    """
    engine = _get_engine()
    Base.metadata.create_all(bind=engine)


def reset_engine() -> None:
    """Reset the database engine (for testing)."""
    global _engine, _SessionLocal
    if _engine:
        _engine.dispose()
    _engine = None
    _SessionLocal = None
```

---

### Database __init__.py (src/nof1_tracker/database/__init__.py)

```python
"""
Database module for nof1-tracker.

Provides database models, configuration, and session management.
"""

from .config import db_settings, DatabaseSettings
from .connection import get_session, get_session_maker, init_db, reset_engine
from .models import (
    Base,
    Season,
    LLMModel,
    LeaderboardSnapshot,
    Trade,
    ModelChat,
)

__all__ = [
    # Config
    "db_settings",
    "DatabaseSettings",
    # Connection
    "get_session",
    "get_session_maker",
    "init_db",
    "reset_engine",
    # Models
    "Base",
    "Season",
    "LLMModel",
    "LeaderboardSnapshot",
    "Trade",
    "ModelChat",
]
```

---

### Test Fixtures (tests/conftest.py)

```python
"""
Pytest fixtures for nof1-tracker tests.

Provides test database setup and teardown.
"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from nof1_tracker.database.models import Base
from nof1_tracker.database import reset_engine


@pytest.fixture(scope="session")
def test_database_url():
    """Get test database URL from environment or use SQLite."""
    return os.environ.get(
        "TEST_DATABASE_URL",
        "sqlite:///./test_nof1_tracker.db"
    )


@pytest.fixture(scope="session")
def test_engine(test_database_url):
    """Create test database engine."""
    engine = create_engine(
        test_database_url,
        echo=False,
        pool_pre_ping=True,
    )
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield engine
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create a test database session with transaction rollback."""
    connection = test_engine.connect()
    transaction = connection.begin()

    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(autouse=True)
def reset_db_engine():
    """Reset the database engine before each test."""
    reset_engine()
    yield
```

---

### Initial Migration (migrations/init/001_init.sql)

```sql
-- Initial database setup for nof1-tracker
-- This script runs automatically on first PostgreSQL container start

-- Enable UUID extension (optional, for future use)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
DO $$ BEGIN
    CREATE TYPE season_status AS ENUM ('active', 'completed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE trade_side AS ENUM ('long', 'short');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE trade_status AS ENUM ('open', 'closed', 'liquidated');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE chat_decision AS ENUM ('buy', 'sell', 'hold', 'close', 'none');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Grant permissions (if using specific roles)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO nof1_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO nof1_user;
```

---

## Definition of Done

### Task 001 Checklist

- [ ] **RED Phase**: Tests written first and failing
  - [ ] `test_database_url_generation`
  - [ ] `test_session_context_manager`
  - [ ] `test_model_creation`
  - [ ] `test_leaderboard_snapshot_creation`
  - [ ] `test_trade_creation`

- [ ] **GREEN Phase**: Minimal code to pass tests
  - [ ] All models defined
  - [ ] Connection manager working
  - [ ] Config loading from env

- [ ] **REFACTOR Phase**: Code cleanup
  - [ ] Type hints complete
  - [ ] Docstrings added
  - [ ] Black/Ruff passing

- [ ] **Docker**
  - [ ] `docker compose up postgres` starts successfully
  - [ ] `docker compose up app` connects to database
  - [ ] Health checks passing

- [ ] **Migrations**
  - [ ] Alembic initialized
  - [ ] Initial migration created
  - [ ] `alembic upgrade head` succeeds

---

## Next Tasks (Future PRDs)

After completing this foundation:

1. **Task 002**: Leaderboard Scraper - Playwright scraper for nof1.ai leaderboard
2. **Task 003**: Trade History Scraper - Fetch and store trade data
3. **Task 004**: ModelChat Scraper - Capture AI reasoning logs
4. **Task 005**: CLI Interface - Typer-based command interface
5. **Task 006**: Performance Analytics - Calculate metrics, generate reports
6. **Task 007**: Continuous Monitor - Background service for real-time tracking

---

## Quick Start Commands

```bash
# Clone and setup
git clone https://github.com/your-username/nof1-tracker.git
cd nof1-tracker
cp .env.example .env
# Edit .env with your credentials

# Start PostgreSQL
docker compose up -d postgres

# Install dependencies
pip install -e ".[dev]"

# Run migrations
alembic upgrade head

# Run tests
pytest

# Start scraper
docker compose --profile scraper run --rm scraper
```
