"""Configuration management using Pydantic Settings.

Provides type-safe configuration classes for:
- DatabaseSettings: PostgreSQL connection configuration
- ScraperSettings: Web scraper configuration
- AppSettings: Application-level settings
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """PostgreSQL database connection configuration.

    Environment variables use the NOF1_DB_ prefix.
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
        """Validate pool_size is greater than 0."""
        if v <= 0:
            raise ValueError("pool_size must be greater than 0")
        return v

    @field_validator("max_overflow")
    @classmethod
    def validate_max_overflow(cls, v: int) -> int:
        """Validate max_overflow is not negative."""
        if v < 0:
            raise ValueError("max_overflow must be >= 0")
        return v

    @property
    def url(self) -> str:
        """Generate PostgreSQL connection URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def async_url(self) -> str:
        """Generate async PostgreSQL connection URL using asyncpg."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class ScraperSettings(BaseSettings):
    """Web scraper configuration.

    Environment variables use the SCRAPER_ prefix.
    """

    model_config = SettingsConfigDict(env_prefix="SCRAPER_")

    headless: bool = True
    timeout: int = 30000
    rate_limit: int = 30


class AppSettings(BaseSettings):
    """Application-level settings.

    Environment variables have no prefix.
    """

    log_level: str = "INFO"
    refresh_interval: int = 15


# Singleton instances
db_settings = DatabaseSettings()
scraper_settings = ScraperSettings()
app_settings = AppSettings()
