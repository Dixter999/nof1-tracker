"""Tests for Docker setup configuration.

These tests validate the Docker configuration files required for local development.
Following TDD: RED phase - these tests should FAIL initially.
"""

import subprocess
from pathlib import Path

import pytest

# Path to project root
PROJECT_ROOT = Path(__file__).parent.parent


class TestDockerFilesExist:
    """Test that required Docker configuration files exist."""

    def test_docker_compose_file_exists(self) -> None:
        """Test that docker-compose.yml exists in project root."""
        docker_compose_path = PROJECT_ROOT / "docker-compose.yml"
        assert docker_compose_path.exists(), (
            f"docker-compose.yml not found at {docker_compose_path}"
        )

    def test_dockerfile_exists(self) -> None:
        """Test that Dockerfile exists in project root."""
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        assert dockerfile_path.exists(), (
            f"Dockerfile not found at {dockerfile_path}"
        )

    def test_migrations_init_directory_exists(self) -> None:
        """Test that migrations/init directory exists."""
        init_dir = PROJECT_ROOT / "migrations" / "init"
        assert init_dir.exists(), (
            f"migrations/init directory not found at {init_dir}"
        )
        assert init_dir.is_dir(), "migrations/init should be a directory"

    def test_init_sql_exists(self) -> None:
        """Test that migrations/init/001_init.sql exists."""
        init_sql_path = PROJECT_ROOT / "migrations" / "init" / "001_init.sql"
        assert init_sql_path.exists(), (
            f"001_init.sql not found at {init_sql_path}"
        )


class TestDockerComposeSyntax:
    """Test Docker Compose file syntax and structure."""

    @pytest.fixture(autouse=True)
    def skip_if_no_docker(self) -> None:
        """Skip tests if Docker is not available."""
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            pytest.skip("Docker not available")

    def test_docker_compose_valid_syntax(self) -> None:
        """Test that docker-compose.yml has valid YAML syntax."""
        result = subprocess.run(
            ["docker", "compose", "config", "--quiet"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0, (
            f"Invalid docker-compose.yml syntax: {result.stderr}"
        )

    def test_docker_compose_has_postgres_service(self) -> None:
        """Test that docker-compose.yml defines postgres service."""
        result = subprocess.run(
            ["docker", "compose", "config", "--services"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0, f"Failed to get services: {result.stderr}"
        services = result.stdout.strip().split("\n")
        assert "postgres" in services, (
            f"postgres service not found. Available services: {services}"
        )

    def test_docker_compose_has_app_service(self) -> None:
        """Test that docker-compose.yml defines app service."""
        result = subprocess.run(
            ["docker", "compose", "config", "--services"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0, f"Failed to get services: {result.stderr}"
        services = result.stdout.strip().split("\n")
        assert "app" in services, (
            f"app service not found. Available services: {services}"
        )

    def test_docker_compose_has_scraper_profile_service(self) -> None:
        """Test that docker-compose.yml defines scraper profile service."""
        result = subprocess.run(
            ["docker", "compose", "--profile", "scraper", "config", "--services"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0, f"Failed to get services: {result.stderr}"
        services = result.stdout.strip().split("\n")
        assert "scraper" in services, (
            f"scraper service not found. Available services: {services}"
        )

    def test_docker_compose_has_monitor_profile_service(self) -> None:
        """Test that docker-compose.yml defines monitor profile service."""
        result = subprocess.run(
            ["docker", "compose", "--profile", "monitor", "config", "--services"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0, f"Failed to get services: {result.stderr}"
        services = result.stdout.strip().split("\n")
        assert "monitor" in services, (
            f"monitor service not found. Available services: {services}"
        )

    def test_docker_compose_postgres_has_healthcheck(self) -> None:
        """Test that postgres service has healthcheck configured."""
        result = subprocess.run(
            ["docker", "compose", "config"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0, f"Failed to get config: {result.stderr}"
        assert "healthcheck:" in result.stdout or "test:" in result.stdout, (
            "Postgres service should have healthcheck configured"
        )

    def test_docker_compose_has_volumes_section(self) -> None:
        """Test that docker-compose.yml defines postgres_data volume."""
        result = subprocess.run(
            ["docker", "compose", "config", "--volumes"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0, f"Failed to get volumes: {result.stderr}"
        assert "postgres_data" in result.stdout, (
            "postgres_data volume not found in docker-compose.yml"
        )


class TestDockerfileContent:
    """Test Dockerfile content and structure."""

    def test_dockerfile_uses_python_312(self) -> None:
        """Test that Dockerfile uses Python 3.12."""
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        if not dockerfile_path.exists():
            pytest.skip("Dockerfile not found")
        content = dockerfile_path.read_text()
        assert "python:3.12" in content, (
            "Dockerfile should use Python 3.12 base image"
        )

    def test_dockerfile_has_workdir(self) -> None:
        """Test that Dockerfile sets WORKDIR."""
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        if not dockerfile_path.exists():
            pytest.skip("Dockerfile not found")
        content = dockerfile_path.read_text()
        assert "WORKDIR" in content, "Dockerfile should set WORKDIR"

    def test_dockerfile_installs_playwright(self) -> None:
        """Test that Dockerfile installs Playwright browsers."""
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        if not dockerfile_path.exists():
            pytest.skip("Dockerfile not found")
        content = dockerfile_path.read_text()
        assert "playwright install" in content.lower(), (
            "Dockerfile should install Playwright browsers"
        )

    def test_dockerfile_copies_source(self) -> None:
        """Test that Dockerfile copies source code."""
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        if not dockerfile_path.exists():
            pytest.skip("Dockerfile not found")
        content = dockerfile_path.read_text()
        assert "COPY src/" in content or "COPY ./src" in content, (
            "Dockerfile should copy source code"
        )

    def test_dockerfile_sets_pythonpath(self) -> None:
        """Test that Dockerfile sets PYTHONPATH."""
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        if not dockerfile_path.exists():
            pytest.skip("Dockerfile not found")
        content = dockerfile_path.read_text()
        assert "PYTHONPATH" in content, "Dockerfile should set PYTHONPATH"


class TestInitSqlContent:
    """Test init SQL file content."""

    def test_init_sql_has_season_status_enum(self) -> None:
        """Test that init SQL creates season_status enum type."""
        init_sql_path = PROJECT_ROOT / "migrations" / "init" / "001_init.sql"
        if not init_sql_path.exists():
            pytest.skip("001_init.sql not found")
        content = init_sql_path.read_text()
        assert "season_status" in content.lower(), (
            "Init SQL should create season_status enum type"
        )

    def test_init_sql_has_trade_side_enum(self) -> None:
        """Test that init SQL creates trade_side enum type."""
        init_sql_path = PROJECT_ROOT / "migrations" / "init" / "001_init.sql"
        if not init_sql_path.exists():
            pytest.skip("001_init.sql not found")
        content = init_sql_path.read_text()
        assert "trade_side" in content.lower(), (
            "Init SQL should create trade_side enum type"
        )

    def test_init_sql_has_trade_status_enum(self) -> None:
        """Test that init SQL creates trade_status enum type."""
        init_sql_path = PROJECT_ROOT / "migrations" / "init" / "001_init.sql"
        if not init_sql_path.exists():
            pytest.skip("001_init.sql not found")
        content = init_sql_path.read_text()
        assert "trade_status" in content.lower(), (
            "Init SQL should create trade_status enum type"
        )

    def test_init_sql_has_chat_decision_enum(self) -> None:
        """Test that init SQL creates chat_decision enum type."""
        init_sql_path = PROJECT_ROOT / "migrations" / "init" / "001_init.sql"
        if not init_sql_path.exists():
            pytest.skip("001_init.sql not found")
        content = init_sql_path.read_text()
        assert "chat_decision" in content.lower(), (
            "Init SQL should create chat_decision enum type"
        )

    def test_init_sql_creates_enum_types(self) -> None:
        """Test that init SQL uses CREATE TYPE for enums."""
        init_sql_path = PROJECT_ROOT / "migrations" / "init" / "001_init.sql"
        if not init_sql_path.exists():
            pytest.skip("001_init.sql not found")
        content = init_sql_path.read_text().upper()
        assert "CREATE TYPE" in content, (
            "Init SQL should use CREATE TYPE for enum definitions"
        )
        assert "ENUM" in content, (
            "Init SQL should define ENUM types"
        )
