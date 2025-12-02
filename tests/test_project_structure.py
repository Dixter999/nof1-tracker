"""Tests for project structure and scaffolding.

These tests verify that all required directories, files, and configurations
exist for the nof1-tracker project.
"""

import tomllib
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class TestDirectoryStructure:
    """Test that required directories exist."""

    def test_src_directory_exists(self) -> None:
        """Test that src/nof1_tracker directory exists."""
        src_dir = PROJECT_ROOT / "src" / "nof1_tracker"
        assert src_dir.exists(), f"Directory {src_dir} does not exist"
        assert src_dir.is_dir(), f"{src_dir} is not a directory"

    def test_scraper_module_exists(self) -> None:
        """Test that scraper module directory exists."""
        scraper_dir = PROJECT_ROOT / "src" / "nof1_tracker" / "scraper"
        assert scraper_dir.exists(), f"Directory {scraper_dir} does not exist"
        assert scraper_dir.is_dir(), f"{scraper_dir} is not a directory"

    def test_database_module_exists(self) -> None:
        """Test that database module directory exists."""
        database_dir = PROJECT_ROOT / "src" / "nof1_tracker" / "database"
        assert database_dir.exists(), f"Directory {database_dir} does not exist"
        assert database_dir.is_dir(), f"{database_dir} is not a directory"

    def test_analyzer_module_exists(self) -> None:
        """Test that analyzer module directory exists."""
        analyzer_dir = PROJECT_ROOT / "src" / "nof1_tracker" / "analyzer"
        assert analyzer_dir.exists(), f"Directory {analyzer_dir} does not exist"
        assert analyzer_dir.is_dir(), f"{analyzer_dir} is not a directory"

    def test_tests_directory_exists(self) -> None:
        """Test that tests directory exists."""
        tests_dir = PROJECT_ROOT / "tests"
        assert tests_dir.exists(), f"Directory {tests_dir} does not exist"
        assert tests_dir.is_dir(), f"{tests_dir} is not a directory"

    def test_test_database_directory_exists(self) -> None:
        """Test that tests/test_database directory exists."""
        test_db_dir = PROJECT_ROOT / "tests" / "test_database"
        assert test_db_dir.exists(), f"Directory {test_db_dir} does not exist"
        assert test_db_dir.is_dir(), f"{test_db_dir} is not a directory"

    def test_test_scraper_directory_exists(self) -> None:
        """Test that tests/test_scraper directory exists."""
        test_scraper_dir = PROJECT_ROOT / "tests" / "test_scraper"
        assert test_scraper_dir.exists(), f"Directory {test_scraper_dir} does not exist"
        assert test_scraper_dir.is_dir(), f"{test_scraper_dir} is not a directory"

    def test_migrations_directory_exists(self) -> None:
        """Test that migrations/versions directory exists."""
        migrations_dir = PROJECT_ROOT / "migrations" / "versions"
        assert migrations_dir.exists(), f"Directory {migrations_dir} does not exist"
        assert migrations_dir.is_dir(), f"{migrations_dir} is not a directory"


class TestInitFiles:
    """Test that all __init__.py files exist."""

    def test_main_package_init_exists(self) -> None:
        """Test that src/nof1_tracker/__init__.py exists."""
        init_file = PROJECT_ROOT / "src" / "nof1_tracker" / "__init__.py"
        assert init_file.exists(), f"File {init_file} does not exist"

    def test_scraper_init_exists(self) -> None:
        """Test that scraper/__init__.py exists."""
        init_file = PROJECT_ROOT / "src" / "nof1_tracker" / "scraper" / "__init__.py"
        assert init_file.exists(), f"File {init_file} does not exist"

    def test_database_init_exists(self) -> None:
        """Test that database/__init__.py exists."""
        init_file = PROJECT_ROOT / "src" / "nof1_tracker" / "database" / "__init__.py"
        assert init_file.exists(), f"File {init_file} does not exist"

    def test_analyzer_init_exists(self) -> None:
        """Test that analyzer/__init__.py exists."""
        init_file = PROJECT_ROOT / "src" / "nof1_tracker" / "analyzer" / "__init__.py"
        assert init_file.exists(), f"File {init_file} does not exist"

    def test_tests_init_exists(self) -> None:
        """Test that tests/__init__.py exists."""
        init_file = PROJECT_ROOT / "tests" / "__init__.py"
        assert init_file.exists(), f"File {init_file} does not exist"

    def test_test_database_init_exists(self) -> None:
        """Test that tests/test_database/__init__.py exists."""
        init_file = PROJECT_ROOT / "tests" / "test_database" / "__init__.py"
        assert init_file.exists(), f"File {init_file} does not exist"

    def test_test_scraper_init_exists(self) -> None:
        """Test that tests/test_scraper/__init__.py exists."""
        init_file = PROJECT_ROOT / "tests" / "test_scraper" / "__init__.py"
        assert init_file.exists(), f"File {init_file} does not exist"


class TestMainFiles:
    """Test that main module files exist."""

    def test_main_py_exists(self) -> None:
        """Test that main.py exists."""
        main_file = PROJECT_ROOT / "src" / "nof1_tracker" / "main.py"
        assert main_file.exists(), f"File {main_file} does not exist"

    def test_conftest_py_exists(self) -> None:
        """Test that tests/conftest.py exists."""
        conftest_file = PROJECT_ROOT / "tests" / "conftest.py"
        assert conftest_file.exists(), f"File {conftest_file} does not exist"


class TestPyprojectToml:
    """Test pyproject.toml configuration."""

    def test_pyproject_toml_exists(self) -> None:
        """Test that pyproject.toml exists and is valid TOML."""
        pyproject_file = PROJECT_ROOT / "pyproject.toml"
        assert pyproject_file.exists(), f"File {pyproject_file} does not exist"

        # Verify it's valid TOML
        with open(pyproject_file, "rb") as f:
            config = tomllib.load(f)
        assert config is not None, "pyproject.toml is not valid TOML"

    def test_pyproject_has_build_system(self) -> None:
        """Test that pyproject.toml has hatchling build system."""
        pyproject_file = PROJECT_ROOT / "pyproject.toml"
        with open(pyproject_file, "rb") as f:
            config = tomllib.load(f)

        assert "build-system" in config, "build-system section missing"
        assert "hatchling" in str(
            config["build-system"].get("requires", [])
        ), "hatchling not in build-system requires"
        assert (
            config["build-system"].get("build-backend") == "hatchling.build"
        ), "hatchling.build not set as build-backend"

    def test_pyproject_has_python_version(self) -> None:
        """Test that pyproject.toml requires Python >= 3.11."""
        pyproject_file = PROJECT_ROOT / "pyproject.toml"
        with open(pyproject_file, "rb") as f:
            config = tomllib.load(f)

        requires_python = config.get("project", {}).get("requires-python", "")
        assert "3.11" in requires_python, "Python 3.11 requirement not found"

    def test_pyproject_has_required_dependencies(self) -> None:
        """Test that pyproject.toml includes all required dependencies."""
        pyproject_file = PROJECT_ROOT / "pyproject.toml"
        with open(pyproject_file, "rb") as f:
            config = tomllib.load(f)

        dependencies = config.get("project", {}).get("dependencies", [])
        deps_str = " ".join(dependencies).lower()

        required_deps = [
            "playwright",
            "sqlalchemy",
            "psycopg2-binary",
            "alembic",
            "python-dotenv",
            "pydantic",
            "pydantic-settings",
            "httpx",
            "rich",
            "typer",
        ]

        for dep in required_deps:
            assert (
                dep.lower() in deps_str
            ), f"Dependency {dep} not found in pyproject.toml"

    def test_pyproject_has_dev_dependencies(self) -> None:
        """Test that pyproject.toml includes dev dependencies."""
        pyproject_file = PROJECT_ROOT / "pyproject.toml"
        with open(pyproject_file, "rb") as f:
            config = tomllib.load(f)

        dev_deps = (
            config.get("project", {}).get("optional-dependencies", {}).get("dev", [])
        )
        deps_str = " ".join(dev_deps).lower()

        required_dev_deps = [
            "pytest",
            "pytest-cov",
            "pytest-asyncio",
            "black",
            "ruff",
            "mypy",
            "pre-commit",
        ]

        for dep in required_dev_deps:
            assert dep.lower() in deps_str, f"Dev dependency {dep} not found"

    def test_pyproject_has_entry_point(self) -> None:
        """Test that pyproject.toml has CLI entry point."""
        pyproject_file = PROJECT_ROOT / "pyproject.toml"
        with open(pyproject_file, "rb") as f:
            config = tomllib.load(f)

        scripts = config.get("project", {}).get("scripts", {})
        assert "nof1-tracker" in scripts, "nof1-tracker entry point not found"
        assert (
            scripts["nof1-tracker"] == "nof1_tracker.main:app"
        ), "Entry point should be nof1_tracker.main:app"


class TestEnvExample:
    """Test .env.example configuration."""

    def test_env_example_exists(self) -> None:
        """Test that .env.example exists."""
        env_file = PROJECT_ROOT / ".env.example"
        assert env_file.exists(), f"File {env_file} does not exist"

    def test_env_example_has_db_variables(self) -> None:
        """Test that .env.example has database variables."""
        env_file = PROJECT_ROOT / ".env.example"
        content = env_file.read_text()

        db_vars = [
            "NOF1_DB_HOST",
            "NOF1_DB_PORT",
            "NOF1_DB_NAME",
            "NOF1_DB_USER",
            "NOF1_DB_PASSWORD",
            "NOF1_DB_POOL_SIZE",
            "NOF1_DB_MAX_OVERFLOW",
        ]

        for var in db_vars:
            assert var in content, f"Database variable {var} not found in .env.example"

    def test_env_example_has_scraper_variables(self) -> None:
        """Test that .env.example has scraper variables."""
        env_file = PROJECT_ROOT / ".env.example"
        content = env_file.read_text()

        scraper_vars = [
            "SCRAPER_HEADLESS",
            "SCRAPER_TIMEOUT",
            "SCRAPER_RATE_LIMIT",
        ]

        for var in scraper_vars:
            assert var in content, f"Scraper variable {var} not found in .env.example"

    def test_env_example_has_app_variables(self) -> None:
        """Test that .env.example has application variables."""
        env_file = PROJECT_ROOT / ".env.example"
        content = env_file.read_text()

        app_vars = [
            "LOG_LEVEL",
            "REFRESH_INTERVAL",
        ]

        for var in app_vars:
            assert (
                var in content
            ), f"Application variable {var} not found in .env.example"


class TestPackageImportable:
    """Test that the package can be imported."""

    def test_package_importable(self) -> None:
        """Test that nof1_tracker package can be imported."""
        try:
            import nof1_tracker

            assert nof1_tracker is not None
        except ImportError as e:
            # Expected to fail until package is installed
            raise AssertionError(f"Cannot import nof1_tracker: {e}") from e

    def test_package_has_version(self) -> None:
        """Test that package has __version__ attribute."""
        try:
            import nof1_tracker

            assert hasattr(
                nof1_tracker, "__version__"
            ), "nof1_tracker missing __version__"
        except ImportError as e:
            raise AssertionError(f"Cannot import nof1_tracker: {e}") from e


class TestMigrationsGitkeep:
    """Test migrations directory setup."""

    def test_gitkeep_exists(self) -> None:
        """Test that migrations/versions/.gitkeep exists."""
        gitkeep_file = PROJECT_ROOT / "migrations" / "versions" / ".gitkeep"
        assert gitkeep_file.exists(), f"File {gitkeep_file} does not exist"
