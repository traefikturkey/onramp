"""Tests for ServiceManager.

Tests both the dashboard.core.service_manager.ServiceManager wrapper
and the underlying scripts.services.ServiceManager.
"""

import pytest


class TestServiceManagerListAvailable:
    """Tests for list_available method (returns list of dicts)."""

    def test_list_available_services(self, service_manager):
        """Should list all available services with metadata."""
        services = service_manager.list_available()

        assert len(services) == 2
        names = [s["name"] for s in services]
        assert "plex" in names
        assert "sonarr" in names

    def test_list_available_returns_dicts(self, service_manager):
        """Should return list of dicts with service info."""
        services = service_manager.list_available()

        for service in services:
            assert isinstance(service, dict)
            assert "name" in service
            assert "description" in service
            assert "category" in service

    def test_list_available_empty_dir(self, tmp_path):
        """Should return empty list for empty directory."""
        from dashboard.core.service_manager import ServiceManager

        (tmp_path / "services-available").mkdir()
        mgr = ServiceManager(str(tmp_path))

        assert mgr.list_available() == []

    def test_list_available_no_dir(self, tmp_path):
        """Should return empty list if directory doesn't exist."""
        from dashboard.core.service_manager import ServiceManager

        mgr = ServiceManager(str(tmp_path))

        assert mgr.list_available() == []


class TestServiceManagerListEnabled:
    """Tests for list_enabled method (returns list of dicts)."""

    def test_list_enabled_services(self, service_manager):
        """Should list enabled services with metadata."""
        services = service_manager.list_enabled()

        assert len(services) == 1
        names = [s["name"] for s in services]
        assert "plex" in names
        assert "sonarr" not in names

    def test_list_enabled_returns_dicts(self, service_manager):
        """Should return list of dicts with service info."""
        services = service_manager.list_enabled()

        for service in services:
            assert isinstance(service, dict)
            assert "name" in service
            assert "enabled" in service
            assert service["enabled"] is True

    def test_list_enabled_empty(self, tmp_path):
        """Should return empty list if no services enabled."""
        from dashboard.core.service_manager import ServiceManager

        (tmp_path / "services-available").mkdir()
        (tmp_path / "services-enabled").mkdir()
        mgr = ServiceManager(str(tmp_path))

        assert mgr.list_enabled() == []


class TestServiceManagerGetNames:
    """Tests for get_available_names and get_enabled_names."""

    def test_get_available_names(self, service_manager):
        """Should return list of available service names."""
        names = service_manager.get_available_names()

        assert isinstance(names, list)
        assert "plex" in names
        assert "sonarr" in names

    def test_get_enabled_names(self, service_manager):
        """Should return list of enabled service names."""
        names = service_manager.get_enabled_names()

        assert isinstance(names, list)
        assert "plex" in names
        assert "sonarr" not in names


class TestServiceManagerParseMetadata:
    """Tests for _parse_metadata method (on underlying scripts.services.ServiceManager)."""

    def test_parse_description(self, temp_services_dir):
        """Should parse description from comments."""
        from scripts.services import ServiceManager

        mgr = ServiceManager(str(temp_services_dir))
        yml_path = temp_services_dir / "services-available" / "plex.yml"
        metadata = mgr._parse_metadata(yml_path)

        assert (
            metadata["description"]
            == "Media server for streaming movies, tv shows, and music"
        )

    def test_parse_category(self, temp_services_dir):
        """Should parse category from comments."""
        from scripts.services import ServiceManager

        mgr = ServiceManager(str(temp_services_dir))
        yml_path = temp_services_dir / "services-available" / "plex.yml"
        metadata = mgr._parse_metadata(yml_path)

        assert metadata["category"] == "media"

    def test_parse_url(self, temp_services_dir):
        """Should parse URL from comments."""
        from scripts.services import ServiceManager

        mgr = ServiceManager(str(temp_services_dir))
        yml_path = temp_services_dir / "services-available" / "plex.yml"
        metadata = mgr._parse_metadata(yml_path)

        assert metadata["url"] == "https://plex.tv"

    def test_parse_nonexistent_file(self, tmp_path):
        """Should return empty metadata for non-existent file."""
        from scripts.services import ServiceManager

        mgr = ServiceManager(str(tmp_path))
        metadata = mgr._parse_metadata(tmp_path / "nonexistent.yml")

        assert metadata["description"] is None
        assert metadata["category"] is None
        assert metadata["url"] is None

    def test_parse_metadata_anywhere_in_file(self, tmp_path):
        """Should find metadata comments anywhere in file."""
        from scripts.services import ServiceManager

        services_dir = tmp_path / "services-available"
        services_dir.mkdir()

        yml_file = services_dir / "test.yml"
        yml_file.write_text(
            """networks:
  traefik:
    external: true

# description: Test service
# category: testing

services:
  test:
    image: test:latest
"""
        )

        mgr = ServiceManager(str(tmp_path))
        metadata = mgr._parse_metadata(yml_file)

        assert metadata["description"] == "Test service"
        assert metadata["category"] == "testing"


class TestServiceManagerGetServiceInfo:
    """Tests for get_service_info method."""

    def test_get_service_info_enabled(self, service_manager):
        """Should return info for enabled service."""
        info = service_manager.get_service_info("plex")

        assert info is not None
        assert info["name"] == "plex"
        assert info["enabled"] is True
        assert info["has_env"] is True
        assert info["has_etc"] is True
        assert (
            info["description"]
            == "Media server for streaming movies, tv shows, and music"
        )
        assert info["category"] == "media"

    def test_get_service_info_not_enabled(self, service_manager):
        """Should return info for non-enabled service."""
        info = service_manager.get_service_info("sonarr")

        assert info is not None
        assert info["name"] == "sonarr"
        assert info["enabled"] is False
        assert info["has_env"] is False
        assert info["has_etc"] is False

    def test_get_service_info_nonexistent(self, service_manager):
        """Should return None for non-existent service."""
        info = service_manager.get_service_info("nonexistent")

        assert info is None


class TestServiceManagerValidate:
    """Tests for validate_service method (on underlying scripts.services.ServiceManager)."""

    def test_validate_valid_service(self, temp_services_dir):
        """Should validate enabled service."""
        from scripts.services import ServiceManager

        mgr = ServiceManager(str(temp_services_dir))
        valid, errors = mgr.validate_service("plex")

        assert valid is True
        assert len(errors) == 0

    def test_validate_nonexistent_service(self, temp_services_dir):
        """Should fail for non-existent service."""
        from scripts.services import ServiceManager

        mgr = ServiceManager(str(temp_services_dir))
        valid, errors = mgr.validate_service("nonexistent")

        assert valid is False
        assert len(errors) > 0
        assert "not found" in errors[0]


class TestServiceManagerGetCategories:
    """Tests for get_categories method."""

    def test_get_categories(self, service_manager):
        """Should return unique categories."""
        categories = service_manager.get_categories()

        assert isinstance(categories, list)
        assert "media" in categories

    def test_get_categories_sorted(self, service_manager):
        """Should return sorted categories."""
        categories = service_manager.get_categories()

        assert categories == sorted(categories)
