# NOF1 Tracker

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Data aggregation and analytics platform for [nof1.ai](https://nof1.ai) Alpha Arena** - an AI trading competition where LLM models trade cryptocurrencies in real-time.

## Overview

NOF1 Tracker provides automated data collection and analysis for the Alpha Arena competition, enabling researchers and analysts to study AI trading behavior and performance patterns.

### Key Features

- **Leaderboard Tracking**: Captures model rankings, PnL, win rates, and performance metrics
- **Trade Analytics**: Records individual trades with entry/exit prices, leverage, and outcomes
- **Decision Logging**: Captures AI model reasoning and decision-making content
- **Historical Analysis**: Stores point-in-time snapshots for trend analysis and backtesting
- **Continuous Monitoring**: Scheduled data collection with configurable intervals

## Quick Start

### Prerequisites

- Docker and Docker Compose
- PostgreSQL database (external or local via Docker)

### 1. Clone and Configure

```bash
git clone https://github.com/Dixter999/nof1-tracker.git
cd nof1-tracker

# Copy environment template
cp .env.example .env

# Edit .env with your database credentials
nano .env
```

### 2. Configure Database

Edit `.env` with your PostgreSQL credentials:

```bash
NOF1_DB_HOST=localhost      # or your database host
NOF1_DB_PORT=5432
NOF1_DB_NAME=nof1_tracker
NOF1_DB_USER=nof1_user
NOF1_DB_PASSWORD=your_secure_password
```

### 3. Initialize Database

```bash
# Build the Docker image
docker compose build

# Run database migrations
docker compose run --rm collector alembic upgrade head
```

### 4. Run Data Collector

```bash
# Single collection run (test)
docker compose --profile collector up

# Continuous collection (every 15 minutes)
docker compose --profile monitor up -d

# View logs
docker compose logs -f monitor
```

## CLI Options

Run the data collector with custom options:

```bash
docker compose run --rm collector python -m nof1_tracker.scraper [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--continuous, -c` | Run continuously at specified interval |
| `--interval, -i N` | Minutes between collections (default: 15) |
| `--max-models, -m N` | Max model pages to process (default: 32) |
| `--no-headless` | Show browser window (debugging) |
| `--verbose, -v` | Enable debug logging |

### Examples

```bash
# Run once with verbose output
docker compose run --rm collector python -m nof1_tracker.scraper -v

# Run continuously every 5 minutes
docker compose run --rm collector python -m nof1_tracker.scraper -c -i 5

# Process only top 10 models
docker compose run --rm collector python -m nof1_tracker.scraper -m 10
```

## Project Structure

```
nof1-tracker/
├── src/nof1_tracker/
│   ├── database/           # Database models and connection
│   │   ├── models.py       # SQLAlchemy ORM models
│   │   ├── connection.py   # Connection management
│   │   └── config.py       # Pydantic settings
│   └── scraper/            # Data collection components
│       ├── base.py         # Base collector with Playwright
│       ├── leaderboard.py  # Leaderboard data collector
│       ├── models.py       # Model page & live feed collector
│       ├── persistence.py  # Data persistence layer
│       └── runner.py       # Orchestration & scheduling
├── migrations/             # Alembic database migrations
├── tests/                  # Test suite
├── docs/                   # Documentation
├── docker-compose.yml      # Docker orchestration
├── Dockerfile              # Container definition
└── .env.example            # Environment template
```

## Database Schema

See [docs/DATABASE.md](docs/DATABASE.md) for complete database documentation including:
- Table schemas and relationships
- Column descriptions and data types
- Enum values and indexes
- Query examples

## Development

### Local Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=nof1_tracker

# Format code
black src/ tests/
ruff check src/ tests/
```

### Docker Development

```bash
# Start local PostgreSQL
docker compose up -d postgres

# Run tests in container
docker compose run --rm app pytest

# Access database
docker compose exec postgres psql -U nof1_user -d nof1_tracker
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NOF1_DB_HOST` | PostgreSQL host | `localhost` |
| `NOF1_DB_PORT` | PostgreSQL port | `5432` |
| `NOF1_DB_NAME` | Database name | `nof1_tracker` |
| `NOF1_DB_USER` | Database user | `nof1_user` |
| `NOF1_DB_PASSWORD` | Database password | (required) |
| `SCRAPER_HEADLESS` | Run browser headless | `true` |
| `SCRAPER_TIMEOUT` | Page timeout (ms) | `30000` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

For security concerns, please see our [Security Policy](SECURITY.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Season Transitions

### Switching to Season 2

When Alpha Arena Season 2 officially starts, use the automated transition script:

```bash
# Automated transition (recommended)
./switch-to-season-2.sh
```

**Or manually:**

```bash
# 1. Stop the current monitor
docker stop nof1-tracker-monitor

# 2. Update season in code
sed -i 's/get_or_create_season("1.5")/get_or_create_season("2")/g' \
  src/nof1_tracker/scraper/runner.py

# 3. Rebuild and restart
docker compose build monitor
docker compose --profile monitor up -d

# 4. Verify Season 2 is scraping
docker logs -f nof1-tracker-monitor
```

### Season Status

Check current season data:

```bash
# Connect to database
docker exec -e PGPASSWORD='your_password' your-postgres-container \
  psql -h your_host -p your_port -U your_user -d your_db \
  -c "SELECT * FROM seasons ORDER BY id;"

# Check recent data collection
docker exec -e PGPASSWORD='your_password' your-postgres-container \
  psql -h your_host -p your_port -U your_user -d your_db \
  -c "SELECT season_number, COUNT(*) as trades, MAX(opened_at) as last_trade
      FROM trades t JOIN seasons s ON t.season_id = s.id
      GROUP BY s.season_number ORDER BY s.season_number;"
```

**Note:** The monitor automatically creates new season entries in the database when transitioning.

## Disclaimer

This project is intended for educational and research purposes. Users are responsible for ensuring compliance with applicable terms of service and regulations. The authors are not responsible for any misuse of this software.

## Acknowledgments

- [nof1.ai](https://nof1.ai) for creating the Alpha Arena competition
- [Playwright](https://playwright.dev/) for browser automation
- [SQLAlchemy](https://www.sqlalchemy.org/) for database ORM
