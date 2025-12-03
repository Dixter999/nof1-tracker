# NOF1 Tracker

Web scraper and data tracker for [nof1.ai](https://nof1.ai) Alpha Arena - an AI trading competition where LLM models trade cryptocurrencies.

## Features

- **Leaderboard Scraping**: Captures model rankings, PnL, win rates, and performance metrics
- **Trade Tracking**: Records individual trades with entry/exit prices, leverage, and status
- **Chat/Reasoning Logs**: Captures AI model decision-making content from live feed
- **Historical Data**: Stores point-in-time snapshots for trend analysis
- **Continuous Monitoring**: Scheduled scraping with configurable intervals

## Quick Start

### Prerequisites

- Docker and Docker Compose
- PostgreSQL database (external or local via Docker)

### 1. Clone and Configure

```bash
git clone https://github.com/yourusername/nof1-tracker.git
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
docker compose run --rm scraper alembic upgrade head
```

### 4. Run Scraper

```bash
# Single scrape (test)
docker compose --profile scraper up

# Continuous scraping (every 15 minutes)
docker compose --profile monitor up -d

# View logs
docker compose logs -f monitor
```

## CLI Options

Run the scraper with custom options:

```bash
docker compose run --rm scraper python -m nof1_tracker.scraper [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--continuous, -c` | Run continuously at specified interval |
| `--interval, -i N` | Minutes between scrapes (default: 15) |
| `--max-models, -m N` | Max model pages to scrape (default: 32) |
| `--no-headless` | Show browser window (debugging) |
| `--verbose, -v` | Enable debug logging |

Examples:

```bash
# Run once with verbose output
docker compose run --rm scraper python -m nof1_tracker.scraper -v

# Run continuously every 5 minutes
docker compose run --rm scraper python -m nof1_tracker.scraper -c -i 5

# Scrape only top 10 models
docker compose run --rm scraper python -m nof1_tracker.scraper -m 10
```

## Project Structure

```
nof1-tracker/
├── src/nof1_tracker/
│   ├── database/           # Database models and connection
│   │   ├── models.py       # SQLAlchemy ORM models
│   │   ├── connection.py   # Connection management
│   │   └── config.py       # Pydantic settings
│   └── scraper/            # Web scraping components
│       ├── base.py         # Base scraper with Playwright
│       ├── leaderboard.py  # Leaderboard page scraper
│       ├── models.py       # Model page & live chat scraper
│       ├── persistence.py  # Data persistence layer
│       └── runner.py       # Orchestration & scheduling
├── migrations/             # Alembic database migrations
├── tests/                  # Test suite
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

## License

MIT License - see [LICENSE](LICENSE) for details.

## Disclaimer

This project is for educational and research purposes. Always respect website terms of service and rate limits when scraping.
