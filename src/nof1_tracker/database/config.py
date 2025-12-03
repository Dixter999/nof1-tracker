"""Configuration management using Pydantic Settings.

This module provides type-safe configuration classes for the NOF1 Tracker
application. All configuration is loaded from environment variables with
appropriate defaults for local development.

Classes:
    DatabaseSettings: PostgreSQL connection configuration (NOF1_DB_ prefix)
    ScraperSettings: Web scraper configuration (SCRAPER_ prefix)
    AppSettings: Application-level settings (no prefix)

Singleton Instances:
    db_settings: Pre-instantiated DatabaseSettings
    scraper_settings: Pre-instantiated ScraperSettings
    app_settings: Pre-instantiated AppSettings

Example:
    >>> from nof1_tracker.database.config import db_settings
    >>> print(db_settings.url)
    postgresql://nof1_user:@localhost:5432/nof1_tracker
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """PostgreSQL database connection configuration.

    Loads configuration from environment variables with the NOF1_DB_ prefix.

    Attributes:
        host: Database server hostname. Default: "localhost".
            Env var: NOF1_DB_HOST
        port: Database server port. Default: 5432.
            Env var: NOF1_DB_PORT
        name: Database name. Default: "nof1_tracker".
            Env var: NOF1_DB_NAME
        user: Database user. Default: "nof1_user".
            Env var: NOF1_DB_USER
        password: Database password. Default: "" (empty).
            Env var: NOF1_DB_PASSWORD
        pool_size: SQLAlchemy connection pool size. Must be > 0. Default: 5.
            Env var: NOF1_DB_POOL_SIZE
        max_overflow: Maximum connections beyond pool_size. Must be >= 0.
            Default: 10. Env var: NOF1_DB_MAX_OVERFLOW

    Properties:
        url: Synchronous PostgreSQL connection URL.
        async_url: Asynchronous PostgreSQL connection URL (asyncpg).

    Example:
        >>> settings = DatabaseSettings()
        >>> settings.url
        'postgresql://nof1_user:@localhost:5432/nof1_tracker'
    """

    model_config = SettingsConfigDict(env_prefix="NOF1_DB_")

    host: str = "localhost"
    port: int = 5432
    name: str = "nof1_tracker"
    user: str = "nof1_user"
    password: str = ""
    pool_size: int = 5
    max_overflow: int = 10

    @field_validator("pool_size")
    @classmethod
    def validate_pool_size(cls, v: int) -> int:
        """Validate pool_size is greater than 0.

        Args:
            v: The pool_size value to validate.

        Returns:
            The validated pool_size value.

        Raises:
            ValueError: If pool_size is not greater than 0.
        """
        if v <= 0:
            raise ValueError("pool_size must be greater than 0")
        return v

    @field_validator("max_overflow")
    @classmethod
    def validate_max_overflow(cls, v: int) -> int:
        """Validate max_overflow is not negative.

        Args:
            v: The max_overflow value to validate.

        Returns:
            The validated max_overflow value.

        Raises:
            ValueError: If max_overflow is negative.
        """
        if v < 0:
            raise ValueError("max_overflow must be >= 0")
        return v

    @property
    def url(self) -> str:
        """Generate PostgreSQL connection URL for synchronous operations.

        Returns:
            Connection URL in format: postgresql://user:pass@host:port/dbname
        """
        return (
            f"postgresql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )

    @property
    def async_url(self) -> str:
        """Generate async PostgreSQL connection URL using asyncpg driver.

        Returns:
            Connection URL in format: postgresql+asyncpg://user:pass@host:port/dbname
        """
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class ScraperSettings(BaseSettings):
    """Web scraper configuration using Playwright.

    Loads configuration from environment variables with the SCRAPER_ prefix.

    Attributes:
        headless: Run browser in headless mode. Default: True.
            Env var: SCRAPER_HEADLESS
        timeout: Page load timeout in milliseconds. Default: 30000 (30s).
            Env var: SCRAPER_TIMEOUT
        rate_limit: Minimum seconds between requests. Default: 30.
            Env var: SCRAPER_RATE_LIMIT

    Example:
        >>> settings = ScraperSettings()
        >>> settings.headless
        True
    """

    model_config = SettingsConfigDict(env_prefix="SCRAPER_")

    headless: bool = True
    timeout: int = 30000
    rate_limit: int = 30


class AppSettings(BaseSettings):
    """Application-level settings.

    These settings use standard environment variable names without a prefix.

    Attributes:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            Default: "INFO". Env var: LOG_LEVEL
        refresh_interval: Data refresh interval in minutes. Default: 15.
            Env var: REFRESH_INTERVAL

    Example:
        >>> settings = AppSettings()
        >>> settings.log_level
        'INFO'
    """

    log_level: str = "INFO"
    refresh_interval: int = 15


# Singleton instances for convenient access throughout the application.
# These are instantiated at module load time with current environment values.
db_settings = DatabaseSettings()
scraper_settings = ScraperSettings()
app_settings = AppSettings()
