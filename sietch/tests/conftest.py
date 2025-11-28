"""Pytest configuration and shared fixtures for OnRamp Dashboard tests."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

# Add sietch to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# Mock Docker Client
# =============================================================================


class MockContainer:
    """Mock Docker container object."""

    def __init__(
        self,
        name: str,
        status: str = "running",
        short_id: str = "abc123",
        image_tags: list[str] | None = None,
        labels: dict | None = None,
        ports: dict | None = None,
        health: str = "healthy",
    ):
        self.name = name
        self.status = status
        self.short_id = short_id
        self.ports = ports or {}
        self.labels = labels or {}

        # Mock image
        self.image = Mock()
        self.image.tags = image_tags or [f"{name}:latest"]

        # Mock attrs
        self.attrs = {
            "Created": "2024-01-01T00:00:00Z",
            "State": {
                "StartedAt": "2024-01-01T00:00:00Z",
                "Health": {"Status": health},
            },
        }

    def start(self):
        self.status = "running"

    def stop(self):
        self.status = "exited"

    def restart(self):
        pass

    def logs(self, tail: int = 100, timestamps: bool = True) -> bytes:
        return b"2024-01-01T00:00:00Z Log line 1\n2024-01-01T00:00:01Z Log line 2\n"

    def stats(self, stream: bool = False) -> dict:
        return {
            "cpu_stats": {
                "cpu_usage": {"total_usage": 1000000, "percpu_usage": [500000, 500000]},
                "system_cpu_usage": 100000000,
            },
            "precpu_stats": {
                "cpu_usage": {"total_usage": 900000},
                "system_cpu_usage": 99000000,
            },
            "memory_stats": {
                "usage": 104857600,  # 100 MB
                "limit": 1073741824,  # 1 GB
            },
        }


class MockDockerClient:
    """Mock Docker client for testing."""

    def __init__(self, containers: list[MockContainer] | None = None):
        self._containers = containers or []
        self._containers_by_name = {c.name: c for c in self._containers}

    def ping(self) -> bool:
        return True

    @property
    def containers(self):
        """Return mock containers manager."""
        return MockContainerManager(self._containers, self._containers_by_name)


class MockContainerManager:
    """Mock container manager (client.containers)."""

    def __init__(self, containers: list, by_name: dict):
        self._containers = containers
        self._by_name = by_name

    def list(self, all: bool = True, filters: dict | None = None) -> list:
        if filters and "label" in filters:
            label = filters["label"]
            if label.startswith("com.docker.compose.service="):
                service_name = label.split("=", 1)[1]
                return [c for c in self._containers if c.name == service_name]
        return self._containers

    def get(self, name: str):
        from docker.errors import NotFound

        if name in self._by_name:
            return self._by_name[name]
        raise NotFound(f"Container {name} not found")


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_containers():
    """Default set of mock containers."""
    return [
        MockContainer(
            name="traefik",
            status="running",
            short_id="trf123",
            labels={"joyride.host.name": "traefik.example.com"},
        ),
        MockContainer(
            name="plex",
            status="running",
            short_id="plx456",
            labels={"joyride.host.name": "plex.example.com"},
        ),
        MockContainer(
            name="sonarr",
            status="exited",
            short_id="snr789",
            health="none",
        ),
    ]


@pytest.fixture
def mock_docker_sdk(mock_containers):
    """Mock docker SDK client."""
    return MockDockerClient(mock_containers)


@pytest.fixture
def docker_client(mock_docker_sdk):
    """DockerClient instance with mocked SDK."""
    from dashboard.core.docker_client import DockerClient

    client = DockerClient()
    client._client = mock_docker_sdk
    return client


@pytest.fixture
def temp_services_dir(tmp_path):
    """Create a temporary services directory structure."""
    # Create directories
    services_available = tmp_path / "services-available"
    services_enabled = tmp_path / "services-enabled"
    etc_dir = tmp_path / "etc"

    services_available.mkdir()
    services_enabled.mkdir()
    etc_dir.mkdir()

    # Create sample service files
    plex_yml = services_available / "plex.yml"
    plex_yml.write_text(
        """networks:
  traefik:
    external: true

# description: Media server for streaming movies, tv shows, and music
# category: media
# https://plex.tv

services:
  plex:
    image: plexinc/pms-docker
    container_name: plex
"""
    )

    sonarr_yml = services_available / "sonarr.yml"
    sonarr_yml.write_text(
        """networks:
  traefik:
    external: true

# description: Manages tv show collections and downloads
# category: media
# https://sonarr.tv

services:
  sonarr:
    image: linuxserver/sonarr
    container_name: sonarr
"""
    )

    # Enable plex (create symlink and env)
    (services_enabled / "plex.yml").symlink_to(plex_yml)
    (services_enabled / "plex.env").write_text("PLEX_CLAIM=claim-xyz\n")
    (etc_dir / "plex").mkdir()

    return tmp_path


@pytest.fixture
def service_manager(temp_services_dir):
    """ServiceManager instance with temp directory."""
    from dashboard.core.service_manager import ServiceManager

    return ServiceManager(str(temp_services_dir))


@pytest.fixture
def test_app(docker_client, service_manager):
    """Create test FastAPI app with mocked dependencies."""
    from pathlib import Path
    from fastapi import FastAPI
    from fastapi.templating import Jinja2Templates

    app = FastAPI()

    # Set up state
    app.state.docker = docker_client
    app.state.services = service_manager

    # Templates
    templates_dir = Path(__file__).parent.parent / "dashboard" / "templates"
    app.state.templates = Jinja2Templates(directory=templates_dir)

    # Include routers
    from dashboard.api import docker, services, system

    app.include_router(docker.router, prefix="/api/docker")
    app.include_router(services.router, prefix="/api/services")
    app.include_router(system.router, prefix="/api/system")

    return app


@pytest.fixture
def client(test_app):
    """Test client for API requests."""
    from fastapi.testclient import TestClient

    return TestClient(test_app)
