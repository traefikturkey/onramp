"""Tests for DockerClient wrapper."""

import pytest
from docker.errors import NotFound, APIError


class TestDockerClientListContainers:
    """Tests for list_containers method."""

    def test_list_containers_returns_all(self, docker_client):
        """Should return all containers as dictionaries."""
        containers = docker_client.list_containers()

        assert len(containers) == 3
        names = [c["name"] for c in containers]
        assert "traefik" in names
        assert "plex" in names
        assert "sonarr" in names

    def test_list_containers_includes_status(self, docker_client):
        """Should include container status."""
        containers = docker_client.list_containers()

        traefik = next(c for c in containers if c["name"] == "traefik")
        assert traefik["status"] == "running"

        sonarr = next(c for c in containers if c["name"] == "sonarr")
        assert sonarr["status"] == "exited"

    def test_list_containers_includes_labels(self, docker_client):
        """Should include container labels."""
        containers = docker_client.list_containers()

        traefik = next(c for c in containers if c["name"] == "traefik")
        assert traefik["labels"]["joyride.host.name"] == "traefik.example.com"


class TestDockerClientGetContainer:
    """Tests for get_container method."""

    def test_get_container_by_name(self, docker_client):
        """Should find container by exact name."""
        container = docker_client.get_container("traefik")

        assert container is not None
        assert container["name"] == "traefik"
        assert container["status"] == "running"

    def test_get_container_not_found(self, docker_client):
        """Should return None for non-existent container."""
        container = docker_client.get_container("nonexistent")

        assert container is None

    def test_get_container_includes_health(self, docker_client):
        """Should include health status."""
        container = docker_client.get_container("traefik")

        assert container["health"] == "healthy"

    def test_get_container_includes_image(self, docker_client):
        """Should include image name."""
        container = docker_client.get_container("traefik")

        assert container["image"] == "traefik:latest"


class TestDockerClientContainerOperations:
    """Tests for start/stop/restart methods."""

    def test_start_container(self, docker_client):
        """Should start a stopped container."""
        success, message = docker_client.start("sonarr")

        assert success is True
        assert "started" in message

    def test_start_nonexistent_container(self, docker_client):
        """Should return error for non-existent container."""
        success, message = docker_client.start("nonexistent")

        assert success is False
        assert "not found" in message

    def test_stop_container(self, docker_client):
        """Should stop a running container."""
        success, message = docker_client.stop("traefik")

        assert success is True
        assert "stopped" in message

    def test_stop_nonexistent_container(self, docker_client):
        """Should return error for non-existent container."""
        success, message = docker_client.stop("nonexistent")

        assert success is False
        assert "not found" in message

    def test_restart_container(self, docker_client):
        """Should restart a container."""
        success, message = docker_client.restart("plex")

        assert success is True
        assert "restarted" in message

    def test_restart_nonexistent_container(self, docker_client):
        """Should return error for non-existent container."""
        success, message = docker_client.restart("nonexistent")

        assert success is False
        assert "not found" in message


class TestDockerClientLogs:
    """Tests for get_logs method."""

    def test_get_logs(self, docker_client):
        """Should return container logs."""
        logs = docker_client.get_logs("traefik")

        assert "Log line 1" in logs
        assert "Log line 2" in logs

    def test_get_logs_nonexistent(self, docker_client):
        """Should return error message for non-existent container."""
        logs = docker_client.get_logs("nonexistent")

        assert "not found" in logs


class TestDockerClientStats:
    """Tests for get_stats method."""

    def test_get_stats(self, docker_client):
        """Should return parsed stats."""
        stats = docker_client.get_stats("traefik")

        assert stats is not None
        assert "cpu_percent" in stats
        assert "memory_percent" in stats
        assert "memory_usage" in stats
        assert "memory_limit" in stats

    def test_get_stats_nonexistent(self, docker_client):
        """Should return None for non-existent container."""
        stats = docker_client.get_stats("nonexistent")

        assert stats is None


class TestDockerClientPing:
    """Tests for ping method."""

    def test_ping_success(self, docker_client):
        """Should return True when Docker is reachable."""
        assert docker_client.ping() is True
