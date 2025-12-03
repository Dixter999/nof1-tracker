# Database Documentation

NOF1 Tracker uses PostgreSQL to store scraped data from the nof1.ai Alpha Arena competition.

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────────────┐       ┌─────────────┐
│   seasons   │       │ leaderboard_snapshots│       │ llm_models  │
├─────────────┤       ├──────────────────────┤       ├─────────────┤
│ id (PK)     │◄──────│ season_id (FK)       │       │ id (PK)     │
│ season_num  │       │ model_id (FK)        │──────►│ name        │
│ name        │       │ timestamp            │       │ provider    │
│ start_date  │       │ rank                 │       │ model_id    │
│ end_date    │       │ total_assets         │       │ is_active   │
│ status      │       │ pnl, pnl_percent     │       │ created_at  │
└─────────────┘       │ win_rate, roi        │       └──────┬──────┘
                      │ total_trades         │              │
                      │ raw_data (JSONB)     │              │
                      └──────────────────────┘              │
                                                           │
                      ┌──────────────────────┐              │
                      │       trades         │              │
                      ├──────────────────────┤              │
                      │ id (PK)              │              │
                      │ model_id (FK)        │◄─────────────┤
                      │ trade_id (unique)    │              │
                      │ symbol               │              │
                      │ side (buy/sell)      │              │
                      │ entry_price          │              │
                      │ exit_price           │              │
                      │ size, leverage       │              │
                      │ pnl, pnl_percent     │              │
                      │ status               │              │
                      │ opened_at, closed_at │              │
                      │ raw_data (JSONB)     │              │
                      └──────────────────────┘              │
                                                           │
                      ┌──────────────────────┐              │
                      │    model_chats       │              │
                      ├──────────────────────┤              │
                      │ id (PK)              │              │
                      │ model_id (FK)        │◄─────────────┘
                      │ timestamp            │
                      │ content (TEXT)       │
                      │ decision             │
                      │ symbol               │
                      │ confidence           │
                      │ raw_data (JSONB)     │
                      └──────────────────────┘
```

## Tables

### seasons

Trading competition seasons/periods.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Auto-increment ID |
| `season_number` | INTEGER | UNIQUE, NOT NULL | Season identifier (1, 2, 3...) |
| `name` | VARCHAR(100) | NOT NULL | Display name ("Season 1") |
| `start_date` | TIMESTAMP | NOT NULL | Season start time |
| `end_date` | TIMESTAMP | NULLABLE | Season end time (null if ongoing) |
| `initial_capital` | NUMERIC(15,2) | DEFAULT 10000.00 | Starting capital for all models |
| `status` | VARCHAR | DEFAULT 'active' | Season status (see enum) |
| `created_at` | TIMESTAMP | NOT NULL | Record creation time |
| `updated_at` | TIMESTAMP | NULLABLE | Last update time |

### llm_models

AI/LLM models participating in the competition.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Auto-increment ID |
| `name` | VARCHAR(100) | UNIQUE, NOT NULL | Model display name ("Claude Sonnet 4.5") |
| `provider` | VARCHAR(50) | NOT NULL | Company/org ("Anthropic", "OpenAI") |
| `model_id` | VARCHAR(100) | NOT NULL | Internal identifier |
| `is_active` | BOOLEAN | DEFAULT true | Whether model is currently active |
| `created_at` | TIMESTAMP | NOT NULL | Record creation time |
| `updated_at` | TIMESTAMP | NULLABLE | Last update time |

### leaderboard_snapshots

Point-in-time performance snapshots from the leaderboard.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Auto-increment ID |
| `season_id` | INTEGER | FK → seasons.id | Associated season |
| `model_id` | INTEGER | FK → llm_models.id | Associated model |
| `timestamp` | TIMESTAMP | NOT NULL | Snapshot time |
| `rank` | INTEGER | NOT NULL | Leaderboard position |
| `total_assets` | NUMERIC(15,2) | NOT NULL | Total account value (USD) |
| `pnl` | NUMERIC(15,2) | NOT NULL | Profit/Loss (USD) |
| `pnl_percent` | NUMERIC(10,4) | NOT NULL | PnL as percentage |
| `roi` | NUMERIC(10,4) | NULLABLE | Return on investment |
| `win_rate` | NUMERIC(5,2) | NULLABLE | Winning trade percentage |
| `total_trades` | INTEGER | DEFAULT 0 | Number of trades |
| `raw_data` | JSONB | NULLABLE | Original scraped data |
| `created_at` | TIMESTAMP | NOT NULL | Record creation time |

**Indexes:**
- `ix_leaderboard_model_id` on `model_id`
- `ix_leaderboard_timestamp` on `timestamp`
- `uix_model_timestamp` UNIQUE on (`model_id`, `timestamp`)

### trades

Individual trade records for each model.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Auto-increment ID |
| `model_id` | INTEGER | FK → llm_models.id | Model that made the trade |
| `trade_id` | VARCHAR(100) | UNIQUE, NOT NULL | External trade identifier |
| `symbol` | VARCHAR(20) | NOT NULL | Trading pair ("BTC-PERP", "ETH-PERP") |
| `side` | VARCHAR | NOT NULL | Trade direction (see enum) |
| `entry_price` | NUMERIC(20,8) | NOT NULL | Entry price |
| `exit_price` | NUMERIC(20,8) | NULLABLE | Exit price (null if open) |
| `size` | NUMERIC(20,8) | NOT NULL | Position size |
| `leverage` | INTEGER | DEFAULT 1 | Leverage multiplier |
| `pnl` | NUMERIC(15,2) | NULLABLE | Profit/Loss (USD) |
| `pnl_percent` | NUMERIC(10,4) | NULLABLE | PnL as percentage |
| `status` | VARCHAR | NOT NULL | Trade status (see enum) |
| `opened_at` | TIMESTAMP | NOT NULL | Trade open time |
| `closed_at` | TIMESTAMP | NULLABLE | Trade close time |
| `raw_data` | JSONB | NULLABLE | Original scraped data |
| `created_at` | TIMESTAMP | NOT NULL | Record creation time |

**Indexes:**
- `ix_trades_model_id` on `model_id`
- `ix_trades_symbol` on `symbol`
- `ix_trades_opened_at` on `opened_at`

### model_chats

AI model reasoning and decision logs from the live feed.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Auto-increment ID |
| `model_id` | INTEGER | FK → llm_models.id | Model that created the chat |
| `timestamp` | TIMESTAMP | NOT NULL | Chat timestamp |
| `content` | TEXT | NOT NULL | Full chat/reasoning text |
| `decision` | VARCHAR | NULLABLE | Trading decision (see enum) |
| `symbol` | VARCHAR(20) | NULLABLE | Related trading pair |
| `confidence` | NUMERIC(5,2) | NULLABLE | Confidence level (0-100) |
| `raw_data` | JSONB | NULLABLE | Original scraped data |
| `created_at` | TIMESTAMP | NOT NULL | Record creation time |

**Indexes:**
- `ix_model_chats_model_id` on `model_id`
- `ix_model_chats_timestamp` on `timestamp`

## Enum Values

### SeasonStatus
| Value | Description |
|-------|-------------|
| `active` | Season currently running |
| `completed` | Season finished normally |
| `cancelled` | Season cancelled |

### TradeSide
| Value | Description |
|-------|-------------|
| `buy` | Long position (buy/long) |
| `sell` | Short position (sell/short) |

### TradeStatus
| Value | Description |
|-------|-------------|
| `open` | Trade currently active |
| `closed` | Trade closed normally |
| `cancelled` | Trade cancelled/liquidated |

### ChatDecision
| Value | Description |
|-------|-------------|
| `buy` | Decision to buy/go long |
| `sell` | Decision to sell/go short |
| `hold` | Decision to hold current position |
| `none` | No trading decision (close position) |

## Example Queries

### Get Current Leaderboard

```sql
SELECT
    m.name AS model_name,
    m.provider,
    ls.rank,
    ls.total_assets,
    ls.pnl_percent,
    ls.win_rate,
    ls.total_trades
FROM leaderboard_snapshots ls
JOIN llm_models m ON ls.model_id = m.id
WHERE ls.timestamp = (
    SELECT MAX(timestamp) FROM leaderboard_snapshots
)
ORDER BY ls.rank;
```

### Get Model Performance Over Time

```sql
SELECT
    DATE(timestamp) as date,
    rank,
    total_assets,
    pnl_percent
FROM leaderboard_snapshots
WHERE model_id = (SELECT id FROM llm_models WHERE name = 'Claude Sonnet 4.5')
ORDER BY timestamp;
```

### Get Recent Trades for a Model

```sql
SELECT
    symbol,
    side,
    entry_price,
    exit_price,
    pnl,
    pnl_percent,
    status,
    opened_at,
    closed_at
FROM trades
WHERE model_id = (SELECT id FROM llm_models WHERE name = 'GPT-5')
ORDER BY opened_at DESC
LIMIT 20;
```

### Get Trading Statistics by Model

```sql
SELECT
    m.name,
    m.provider,
    COUNT(*) as total_trades,
    SUM(CASE WHEN t.pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
    ROUND(100.0 * SUM(CASE WHEN t.pnl > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as win_rate,
    SUM(t.pnl) as total_pnl
FROM trades t
JOIN llm_models m ON t.model_id = m.id
WHERE t.status = 'closed'
GROUP BY m.id, m.name, m.provider
ORDER BY total_pnl DESC;
```

### Get Recent Chat/Reasoning

```sql
SELECT
    m.name as model_name,
    mc.timestamp,
    mc.decision,
    mc.symbol,
    mc.confidence,
    SUBSTRING(mc.content, 1, 200) as content_preview
FROM model_chats mc
JOIN llm_models m ON mc.model_id = m.id
ORDER BY mc.timestamp DESC
LIMIT 50;
```

### Get Snapshot Count by Day

```sql
SELECT
    DATE(timestamp) as date,
    COUNT(*) as snapshots,
    COUNT(DISTINCT model_id) as models_tracked
FROM leaderboard_snapshots
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

## Connection

### Python (SQLAlchemy)

```python
from nof1_tracker.database.connection import get_session

with get_session() as session:
    # Query example
    result = session.execute(text("SELECT * FROM llm_models"))
    for row in result:
        print(row)
```

### Direct PostgreSQL Connection

```bash
# Via Docker
docker compose exec postgres psql -U nof1_user -d nof1_tracker

# Direct connection
psql -h localhost -p 5432 -U nof1_user -d nof1_tracker
```

## Migrations

Database schema is managed via Alembic migrations:

```bash
# Apply all migrations
docker compose run --rm scraper alembic upgrade head

# Show current revision
docker compose run --rm scraper alembic current

# Show migration history
docker compose run --rm scraper alembic history

# Rollback one migration
docker compose run --rm scraper alembic downgrade -1

# Create new migration
docker compose run --rm scraper alembic revision --autogenerate -m "description"
```
