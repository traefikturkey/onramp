"""Tests for System API endpoints."""

from unittest.mock import Mock


class TestSystemHealthAPI:
    """Tests for /api/system/health endpoint."""

    def test_health_check(self, client):
        """Should return health status."""
        response = client.get("/api/system/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "docker" in data
        assert data["docker"] is True
        assert data["status"] == "healthy"


class TestSystemInfoAPI:
    """Tests for /api/system/info endpoint."""

    def test_hides_internal_docker_errors(self, client, docker_client, find_log_record):
        """Should log internal errors without returning their details."""
        docker_client._client.info = Mock(
            side_effect=RuntimeError("private socket details")
        )

        response = client.get("/api/system/info")

        assert response.status_code == 200
        assert response.json() == {
            "error": "Unable to retrieve Docker system information"
        }
        assert "private socket details" not in response.text
        record = find_log_record("Failed to retrieve Docker system information")
        assert record.exc_info is not None


class TestSystemStatsAPI:
    """Tests for /api/system/stats endpoint."""

    def test_system_stats(self, client):
        """Should return system statistics."""
        response = client.get("/api/system/stats")

        assert response.status_code == 200
        data = response.json()

        # Check container stats
        assert "containers" in data
        assert data["containers"]["total"] == 3
        assert data["containers"]["running"] == 2  # traefik, plex
        assert data["containers"]["stopped"] == 1  # sonarr

        # Check service stats
        assert "services" in data
        assert data["services"]["available"] == 2  # plex, sonarr
        assert data["services"]["enabled"] == 1  # plex
