# NOF1 Tracker Docker Image
# Multi-stage build for optimized production image

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies required for psycopg2 and Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first for better layer caching
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir -e ".[dev]"

# Install Playwright browsers (Chromium only for scraping)
RUN playwright install chromium --with-deps

# Copy application code
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY tests/ ./tests/

# Set Python path to include src directory
ENV PYTHONPATH=/app/src

# Default command shows help
CMD ["python", "-m", "nof1_tracker.main", "--help"]
