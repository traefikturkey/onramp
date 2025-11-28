"""Tests for services.py - service listing and metadata parsing."""

import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from services import ServiceManager


class TestStripExtension:
    """Tests for _strip_extension() - filename cleanup."""

    def test_removes_yml_extension(self):
        mgr = ServiceManager.__new__(ServiceManager)
        assert mgr._strip_extension("plex.yml") == "plex"
        assert mgr._strip_extension("radarr.yml") == "radarr"

    def test_handles_no_extension(self):
        mgr = ServiceManager.__new__(ServiceManager)
        assert mgr._strip_extension("plex") == "plex"

    def test_only_removes_yml(self):
        mgr = ServiceManager.__new__(ServiceManager)
        # .yaml is NOT removed (only .yml)
        assert mgr._strip_extension("plex.yaml") == "plex.yaml"

    def test_handles_multiple_dots(self):
        mgr = ServiceManager.__new__(ServiceManager)
        assert mgr._strip_extension("my.service.yml") == "my.service"


class TestParseMetadata:
    """Tests for _parse_metadata() - YAML header comment parsing."""

    def test_parses_description(self, tmp_path):
        yml = tmp_path / "test.yml"
        yml.write_text("# description: A test service\nservices:\n")

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        assert meta["description"] == "A test service"

    def test_parses_category(self, tmp_path):
        yml = tmp_path / "test.yml"
        yml.write_text("# category: media\nservices:\n")

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        assert meta["category"] == "media"

    def test_parses_url(self, tmp_path):
        yml = tmp_path / "test.yml"
        yml.write_text("# https://github.com/example/repo\nservices:\n")

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        assert meta["url"] == "https://github.com/example/repo"

    def test_parses_http_url(self, tmp_path):
        yml = tmp_path / "test.yml"
        yml.write_text("# http://example.com\nservices:\n")

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        assert meta["url"] == "http://example.com"

    def test_parses_skip_services_file_true(self, tmp_path):
        yml = tmp_path / "test.yml"
        yml.write_text("# skip_services_file: true\nservices:\n")

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        assert meta["skip_services_file"] is True

    def test_parses_skip_services_file_yes(self, tmp_path):
        yml = tmp_path / "test.yml"
        yml.write_text("# skip_services_file: yes\nservices:\n")

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        assert meta["skip_services_file"] is True

    def test_skip_services_file_defaults_false(self, tmp_path):
        yml = tmp_path / "test.yml"
        yml.write_text("# description: Test\nservices:\n")

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        assert meta["skip_services_file"] is False

    def test_parses_all_metadata(self, tmp_path):
        yml = tmp_path / "test.yml"
        yml.write_text(
            "# description: Media server\n"
            "# category: media\n"
            "# https://plex.tv\n"
            "services:\n"
        )

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        assert meta["description"] == "Media server"
        assert meta["category"] == "media"
        assert meta["url"] == "https://plex.tv"

    def test_stops_at_non_comment_line(self, tmp_path):
        yml = tmp_path / "test.yml"
        yml.write_text(
            "# description: Before content\n"
            "services:\n"
            "# description: After content\n"
        )

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        # Should only get the first description
        assert meta["description"] == "Before content"

    def test_handles_empty_file(self, tmp_path):
        yml = tmp_path / "test.yml"
        yml.write_text("")

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        assert meta["description"] is None
        assert meta["category"] is None
        assert meta["url"] is None

    def test_handles_missing_file(self, tmp_path):
        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(tmp_path / "nonexistent.yml")

        # Should return defaults without error
        assert meta["description"] is None

    def test_skips_empty_lines(self, tmp_path):
        yml = tmp_path / "test.yml"
        yml.write_text(
            "\n"
            "# description: With empty lines\n"
            "\n"
            "# category: test\n"
            "services:\n"
        )

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        assert meta["description"] == "With empty lines"
        assert meta["category"] == "test"


class TestListAvailable:
    """Tests for list_available() - service discovery."""

    def test_lists_yml_files(self, tmp_path):
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        (services_available / "plex.yml").write_text("services:\n")
        (services_available / "radarr.yml").write_text("services:\n")

        mgr = ServiceManager(str(tmp_path))
        result = mgr.list_available()

        assert "plex" in result
        assert "radarr" in result

    def test_ignores_non_yml_files(self, tmp_path):
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        (services_available / "plex.yml").write_text("services:\n")
        (services_available / "readme.md").write_text("# readme\n")
        (services_available / "config.yaml").write_text("config:\n")

        mgr = ServiceManager(str(tmp_path))
        result = mgr.list_available()

        assert result == ["plex"]

    def test_returns_sorted(self, tmp_path):
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        (services_available / "zebra.yml").write_text("services:\n")
        (services_available / "alpha.yml").write_text("services:\n")
        (services_available / "middle.yml").write_text("services:\n")

        mgr = ServiceManager(str(tmp_path))
        result = mgr.list_available()

        assert result == ["alpha", "middle", "zebra"]

    def test_empty_directory(self, tmp_path):
        services_available = tmp_path / "services-available"
        services_available.mkdir()

        mgr = ServiceManager(str(tmp_path))
        result = mgr.list_available()

        assert result == []

    def test_missing_directory(self, tmp_path):
        mgr = ServiceManager(str(tmp_path))
        result = mgr.list_available()

        assert result == []


class TestListEnabled:
    """Tests for list_enabled() - enabled service discovery."""

    def test_lists_enabled_services(self, tmp_path):
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (services_enabled / "plex.yml").write_text("services:\n")
        (services_enabled / "radarr.yml").write_text("services:\n")

        mgr = ServiceManager(str(tmp_path))
        result = mgr.list_enabled()

        assert "plex" in result
        assert "radarr" in result

    def test_ignores_env_files(self, tmp_path):
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (services_enabled / "plex.yml").write_text("services:\n")
        (services_enabled / "plex.env").write_text("VAR=value\n")
        (services_enabled / ".env").write_text("GLOBAL=value\n")

        mgr = ServiceManager(str(tmp_path))
        result = mgr.list_enabled()

        assert result == ["plex"]


class TestListGames:
    """Tests for list_games() - game service discovery."""

    def test_lists_games(self, tmp_path):
        games_dir = tmp_path / "services-available" / "games"
        games_dir.mkdir(parents=True)
        (games_dir / "minecraft.yml").write_text("services:\n")
        (games_dir / "factorio.yml").write_text("services:\n")

        mgr = ServiceManager(str(tmp_path))
        result = mgr.list_games()

        assert "minecraft" in result
        assert "factorio" in result


class TestValidateService:
    """Tests for validate_service() - service validation."""

    def test_valid_available_service(self, tmp_path):
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        (services_available / "plex.yml").write_text("# description: Test\nservices:\n")

        mgr = ServiceManager(str(tmp_path))
        valid, errors = mgr.validate_service("plex")

        assert valid is True
        assert errors == []

    def test_nonexistent_service(self, tmp_path):
        services_available = tmp_path / "services-available"
        services_available.mkdir()

        mgr = ServiceManager(str(tmp_path))
        valid, errors = mgr.validate_service("nonexistent")

        assert valid is False
        assert "not found" in errors[0]


class TestGetServiceInfo:
    """Tests for get_service_info() - service info aggregation."""

    def test_returns_basic_info(self, tmp_path):
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (services_available / "plex.yml").write_text(
            "# description: Media server\n# category: media\nservices:\n"
        )

        mgr = ServiceManager(str(tmp_path))
        info = mgr.get_service_info("plex")

        assert info["name"] == "plex"
        assert info["description"] == "Media server"
        assert info["category"] == "media"
        assert info["enabled"] is False

    def test_detects_enabled_status(self, tmp_path):
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (services_available / "plex.yml").write_text("services:\n")
        (services_enabled / "plex.yml").write_text("services:\n")

        mgr = ServiceManager(str(tmp_path))
        info = mgr.get_service_info("plex")

        assert info["enabled"] is True

    def test_detects_env_file(self, tmp_path):
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (services_available / "plex.yml").write_text("services:\n")
        (services_enabled / "plex.env").write_text("VAR=value\n")

        mgr = ServiceManager(str(tmp_path))
        info = mgr.get_service_info("plex")

        assert info["has_env"] is True

    def test_returns_none_for_missing(self, tmp_path):
        services_available = tmp_path / "services-available"
        services_available.mkdir()

        mgr = ServiceManager(str(tmp_path))
        info = mgr.get_service_info("nonexistent")

        assert info is None
