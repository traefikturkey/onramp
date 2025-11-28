"""Tests for Docker API endpoints."""

import pytest


class TestDockerContainersAPI:
    """Tests for /api/docker/containers endpoints."""

    def test_list_containers(self, client):
        """Should list all containers."""
        response = client.get("/api/docker/containers")

        assert response.status_code == 200
        data = response.json()
        assert "containers" in data
        assert "count" in data
        assert data["count"] == 3

    def test_list_containers_names(self, client):
        """Should include expected container names."""
        response = client.get("/api/docker/containers")

        data = response.json()
        names = [c["name"] for c in data["containers"]]
        assert "traefik" in names
        assert "plex" in names
        assert "sonarr" in names

    def test_get_container_by_name(self, client):
        """Should get specific container."""
        response = client.get("/api/docker/containers/traefik")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "traefik"
        assert data["status"] == "running"

    def test_get_container_not_found(self, client):
        """Should return 404 for non-existent container."""
        response = client.get("/api/docker/containers/nonexistent")

        assert response.status_code == 404


class TestDockerContainerActions:
    """Tests for container start/stop/restart endpoints."""

    def test_start_container(self, client):
        """Should start a container."""
        response = client.post("/api/docker/containers/sonarr/start")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "started" in data["message"]

    def test_stop_container(self, client):
        """Should stop a container."""
        response = client.post("/api/docker/containers/traefik/stop")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "stopped" in data["message"]

    def test_restart_container(self, client):
        """Should restart a container."""
        response = client.post("/api/docker/containers/plex/restart")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "restarted" in data["message"]

    def test_start_nonexistent_container(self, client):
        """Should return error for non-existent container."""
        response = client.post("/api/docker/containers/nonexistent/start")

        assert response.status_code == 400


class TestDockerContainerLogs:
    """Tests for container logs endpoint."""

    def test_get_container_logs(self, client):
        """Should return container logs."""
        response = client.get("/api/docker/containers/traefik/logs")

        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert "Log line 1" in data["logs"]


class TestDockerContainerStats:
    """Tests for container stats endpoint."""

    def test_get_container_stats(self, client):
        """Should return container stats."""
        response = client.get("/api/docker/containers/traefik/stats")

        assert response.status_code == 200
        data = response.json()
        assert "cpu_percent" in data
        assert "memory_percent" in data
