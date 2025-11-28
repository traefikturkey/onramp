"""Tests for System API endpoints."""

import pytest


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
