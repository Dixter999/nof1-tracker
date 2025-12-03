"""Tests for configuration module using Pydantic Settings.

This module tests the configuration management for NOF1 Tracker:
- DatabaseSettings: PostgreSQL connection configuration
- ScraperSettings: Web scraper configuration
- AppSettings: Application-level settings
"""

import pytest
from pydantic import ValidationError


class TestDatabaseSettings:
    """Tests for DatabaseSettings class."""

    def test_database_settings_defaults(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify all default values for DatabaseSettings.

        Note: We must unset any NOF1_DB_* env vars that may be set
        by docker-compose.yml to test true defaults.
        """
        from nof1_tracker.database.config import DatabaseSettings

        # Clear any environment variables that might override defaults
        monkeypatch.delenv("NOF1_DB_HOST", raising=False)
        monkeypatch.delenv("NOF1_DB_PORT", raising=False)
        monkeypatch.delenv("NOF1_DB_NAME", raising=False)
        monkeypatch.delenv("NOF1_DB_USER", raising=False)
        monkeypatch.delenv("NOF1_DB_PASSWORD", raising=False)
        monkeypatch.delenv("NOF1_DB_POOL_SIZE", raising=False)
        monkeypatch.delenv("NOF1_DB_MAX_OVERFLOW", raising=False)

        settings = DatabaseSettings()

        assert settings.host == "localhost"
        assert settings.port == 5432
        assert settings.name == "nof1_tracker"
        assert settings.user == "nof1_user"
        assert settings.password == ""
        assert settings.pool_size == 5
        assert settings.max_overflow == 10

    def test_database_settings_from_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Load DatabaseSettings values from environment variables."""
        from nof1_tracker.database.config import DatabaseSettings

        monkeypatch.setenv("NOF1_DB_HOST", "db.example.com")
        monkeypatch.setenv("NOF1_DB_PORT", "5433")
        monkeypatch.setenv("NOF1_DB_NAME", "test_db")
        monkeypatch.setenv("NOF1_DB_USER", "test_user")
        monkeypatch.setenv("NOF1_DB_PASSWORD", "secret123")
        monkeypatch.setenv("NOF1_DB_POOL_SIZE", "10")
        monkeypatch.setenv("NOF1_DB_MAX_OVERFLOW", "20")

        settings = DatabaseSettings()

        assert settings.host == "db.example.com"
        assert settings.port == 5433
        assert settings.name == "test_db"
        assert settings.user == "test_user"
        assert settings.password == "secret123"
        assert settings.pool_size == 10
        assert settings.max_overflow == 20

    def test_database_url_generation(self) -> None:
        """Verify url property generates correct connection string."""
        from nof1_tracker.database.config import DatabaseSettings

        settings = DatabaseSettings(
            host="myhost",
            port=5432,
            name="mydb",
            user="myuser",
            password="mypass",
        )

        expected_url = "postgresql://myuser:mypass@myhost:5432/mydb"
        assert settings.url == expected_url

    def test_async_url_generation(self) -> None:
        """Verify async_url property generates correct async connection string."""
        from nof1_tracker.database.config import DatabaseSettings

        settings = DatabaseSettings(
            host="myhost",
            port=5432,
            name="mydb",
            user="myuser",
            password="mypass",
        )

        expected_url = "postgresql+asyncpg://myuser:mypass@myhost:5432/mydb"
        assert settings.async_url == expected_url

    def test_pool_size_validation_positive(self) -> None:
        """pool_size=0 should raise ValidationError."""
        from nof1_tracker.database.config import DatabaseSettings

        with pytest.raises(ValidationError) as exc_info:
            DatabaseSettings(pool_size=0)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "pool_size" in str(errors[0]["loc"])

    def test_pool_size_validation_negative(self) -> None:
        """pool_size=-1 should raise ValidationError."""
        from nof1_tracker.database.config import DatabaseSettings

        with pytest.raises(ValidationError) as exc_info:
            DatabaseSettings(pool_size=-1)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "pool_size" in str(errors[0]["loc"])

    def test_max_overflow_validation(self) -> None:
        """max_overflow=-1 should raise ValidationError."""
        from nof1_tracker.database.config import DatabaseSettings

        with pytest.raises(ValidationError) as exc_info:
            DatabaseSettings(max_overflow=-1)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "max_overflow" in str(errors[0]["loc"])


class TestScraperSettings:
    """Tests for ScraperSettings class."""

    def test_scraper_settings_defaults(self) -> None:
        """Verify all default values for ScraperSettings."""
        from nof1_tracker.database.config import ScraperSettings

        settings = ScraperSettings()

        assert settings.headless is True
        assert settings.timeout == 30000
        assert settings.rate_limit == 30


class TestAppSettings:
    """Tests for AppSettings class."""

    def test_app_settings_defaults(self) -> None:
        """Verify all default values for AppSettings."""
        from nof1_tracker.database.config import AppSettings

        settings = AppSettings()

        assert settings.log_level == "INFO"
        assert settings.refresh_interval == 15
