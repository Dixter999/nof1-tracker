# NOF1 Tracker Docker Image
# Optimized for local development with Playwright browser support
#
# Build: docker build -t nof1-tracker .
# Run:   docker compose up -d

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing bytecode and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies required for:
# - libpq-dev: PostgreSQL client library (psycopg2)
# - gcc: C compiler for building Python extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy dependency files first for better Docker layer caching
# Changes to application code won't invalidate dependency layers
COPY pyproject.toml .

# Install Python dependencies with dev extras for testing
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e ".[dev]"

# Install Playwright Chromium browser with system dependencies
# Required for web scraping functionality
RUN playwright install chromium --with-deps

# Copy application code (after dependencies for better caching)
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY tests/ ./tests/

# Set Python path to include src directory for module imports
ENV PYTHONPATH=/app/src

# Document the application does not expose ports by default
# Individual services define their own ports as needed
EXPOSE 8000

# Default command shows help (override in docker-compose.yml)
CMD ["python", "-m", "nof1_tracker.main", "--help"]
