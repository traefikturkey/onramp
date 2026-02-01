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

    def test_last_metadata_wins(self, tmp_path):
        """When duplicate metadata exists, the last one wins (scans whole file)."""
        yml = tmp_path / "test.yml"
        yml.write_text(
            "# description: First description\n"
            "services:\n"
            "# description: Second description\n"
        )

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        # Parser scans entire file, last value wins
        assert meta["description"] == "Second description"

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

    def test_parses_optional_service_with_prompt(self, tmp_path):
        """Parse individual optional service with custom prompt."""
        yml = tmp_path / "test.yml"
        yml.write_text(
            "# description: Test service\n"
            "# optional-service: ollama\n"
            "# optional-prompt: Enable Ollama for AI document processing?\n"
            "services:\n"
        )

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        assert len(meta["optional_services"]) == 1
        assert meta["optional_services"][0]["service"] == "ollama"
        assert meta["optional_services"][0]["prompt"] == "Enable Ollama for AI document processing?"

    def test_optional_service_default_prompt(self, tmp_path):
        """Parse optional service without explicit prompt gets default."""
        yml = tmp_path / "test.yml"
        yml.write_text(
            "# description: Test service\n"
            "# optional-service: ollama\n"
            "services:\n"
        )

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        assert len(meta["optional_services"]) == 1
        assert meta["optional_services"][0]["service"] == "ollama"
        assert meta["optional_services"][0]["prompt"] == "Enable ollama?"

    def test_parses_multiple_optional_services(self, tmp_path):
        """Parse multiple optional services in a single file."""
        yml = tmp_path / "test.yml"
        yml.write_text(
            "# description: Test service\n"
            "# optional-service: ollama\n"
            "# optional-prompt: Enable Ollama?\n"
            "# optional-service: openwebui\n"
            "# optional-prompt: Enable OpenWebUI?\n"
            "services:\n"
        )

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        assert len(meta["optional_services"]) == 2
        assert meta["optional_services"][0]["service"] == "ollama"
        assert meta["optional_services"][1]["service"] == "openwebui"

    def test_parses_optional_group_with_services(self, tmp_path):
        """Parse optional group with services list."""
        yml = tmp_path / "test.yml"
        yml.write_text(
            "# description: Test service\n"
            "# optional-group: ai-features\n"
            "# optional-group-prompt: Enable AI features (Ollama + OpenWebUI)?\n"
            "# optional-group-services: ollama, openwebui\n"
            "services:\n"
        )

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        assert len(meta["optional_groups"]) == 1
        assert meta["optional_groups"][0]["name"] == "ai-features"
        assert meta["optional_groups"][0]["prompt"] == "Enable AI features (Ollama + OpenWebUI)?"
        assert meta["optional_groups"][0]["services"] == ["ollama", "openwebui"]

    def test_optional_group_default_prompt(self, tmp_path):
        """Parse optional group without explicit prompt gets default."""
        yml = tmp_path / "test.yml"
        yml.write_text(
            "# description: Test service\n"
            "# optional-group: ai-features\n"
            "# optional-group-services: ollama, openwebui\n"
            "services:\n"
        )

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        assert len(meta["optional_groups"]) == 1
        assert meta["optional_groups"][0]["name"] == "ai-features"
        assert meta["optional_groups"][0]["prompt"] == "Enable ai-features?"
        assert meta["optional_groups"][0]["services"] == ["ollama", "openwebui"]

    def test_optional_group_trims_whitespace_in_services(self, tmp_path):
        """Parse optional group with whitespace in service list."""
        yml = tmp_path / "test.yml"
        yml.write_text(
            "# optional-group: ai-features\n"
            "# optional-group-prompt: Enable AI?\n"
            "# optional-group-services: ollama,  openwebui  , langchain\n"
            "services:\n"
        )

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        assert meta["optional_groups"][0]["services"] == ["ollama", "openwebui", "langchain"]

    def test_parses_multiple_optional_groups(self, tmp_path):
        """Parse multiple optional groups in a single file."""
        yml = tmp_path / "test.yml"
        yml.write_text(
            "# description: Test\n"
            "# optional-group: ai-features\n"
            "# optional-group-prompt: Enable AI?\n"
            "# optional-group-services: ollama, openwebui\n"
            "# optional-group: media-features\n"
            "# optional-group-prompt: Enable media?\n"
            "# optional-group-services: plex, radarr\n"
            "services:\n"
        )

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        assert len(meta["optional_groups"]) == 2
        assert meta["optional_groups"][0]["name"] == "ai-features"
        assert meta["optional_groups"][1]["name"] == "media-features"

    def test_mixed_optional_services_and_groups(self, tmp_path):
        """Parse both optional services and groups in same file."""
        yml = tmp_path / "test.yml"
        yml.write_text(
            "# description: Complex service\n"
            "# optional-service: extra-service\n"
            "# optional-prompt: Enable extra?\n"
            "# optional-group: ai-features\n"
            "# optional-group-prompt: Enable AI?\n"
            "# optional-group-services: ollama, openwebui\n"
            "services:\n"
        )

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        assert len(meta["optional_services"]) == 1
        assert len(meta["optional_groups"]) == 1
        assert meta["optional_services"][0]["service"] == "extra-service"
        assert meta["optional_groups"][0]["name"] == "ai-features"

    def test_optional_defaults_empty_lists(self, tmp_path):
        """Files without optional services/groups get empty lists."""
        yml = tmp_path / "test.yml"
        yml.write_text("# description: Simple service\nservices:\n")

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        assert meta["optional_services"] == []
        assert meta["optional_groups"] == []

    def test_optional_group_without_services_list(self, tmp_path):
        """Optional group without services list still parses."""
        yml = tmp_path / "test.yml"
        yml.write_text(
            "# optional-group: ai-features\n"
            "# optional-group-prompt: Enable AI?\n"
            "services:\n"
        )

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        assert len(meta["optional_groups"]) == 1
        assert meta["optional_groups"][0]["services"] == []

    def test_optional_group_single_service(self, tmp_path):
        """Optional group with single service (no comma)."""
        yml = tmp_path / "test.yml"
        yml.write_text(
            "# optional-group: single-group\n"
            "# optional-group-services: ollama\n"
            "services:\n"
        )

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        assert meta["optional_groups"][0]["services"] == ["ollama"]

    def test_preserves_existing_metadata_with_optionals(self, tmp_path):
        """Optional parsing doesn't interfere with existing metadata."""
        yml = tmp_path / "test.yml"
        yml.write_text(
            "# description: Full service\n"
            "# category: media\n"
            "# https://example.com\n"
            "# optional-service: extra\n"
            "# optional-prompt: Enable extra?\n"
            "services:\n"
        )

        mgr = ServiceManager(str(tmp_path))
        meta = mgr._parse_metadata(yml)

        assert meta["description"] == "Full service"
        assert meta["category"] == "media"
        assert meta["url"] == "https://example.com"
        assert len(meta["optional_services"]) == 1


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


class TestGetDependsOn:
    """Tests for get_depends_on() - external dependency extraction."""

    def test_internal_deps_only_returns_empty(self, tmp_path):
        """Service with only internal deps returns empty list."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()

        yml = services_available / "paperless.yml"
        yml.write_text(
            "services:\n"
            "  broker:\n"
            "    image: redis:7\n"
            "  db:\n"
            "    image: mariadb:10\n"
            "  app:\n"
            "    image: paperless:latest\n"
            "    depends_on:\n"
            "      - broker\n"
            "      - db\n"
        )

        mgr = ServiceManager(str(tmp_path))
        result = mgr.get_depends_on("paperless")

        assert result == []

    def test_external_deps_returns_those_deps(self, tmp_path):
        """Service with external deps returns those deps only."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()

        yml = services_available / "app.yml"
        yml.write_text(
            "services:\n"
            "  app:\n"
            "    image: myapp:latest\n"
            "    depends_on:\n"
            "      - ollama\n"
            "      - redis\n"
        )

        mgr = ServiceManager(str(tmp_path))
        result = mgr.get_depends_on("app")

        assert set(result) == {"ollama", "redis"}

    def test_mixed_deps_returns_only_external(self, tmp_path):
        """Service with mixed deps returns only external ones."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()

        yml = services_available / "complex.yml"
        yml.write_text(
            "services:\n"
            "  internal-db:\n"
            "    image: postgres:15\n"
            "  internal-cache:\n"
            "    image: redis:7\n"
            "  main:\n"
            "    image: app:latest\n"
            "    depends_on:\n"
            "      - internal-db\n"
            "      - internal-cache\n"
            "      - external-auth\n"
            "      - external-storage\n"
        )

        mgr = ServiceManager(str(tmp_path))
        result = mgr.get_depends_on("complex")

        assert set(result) == {"external-auth", "external-storage"}

    def test_no_depends_on_returns_empty(self, tmp_path):
        """Service without depends_on returns empty list."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()

        yml = services_available / "simple.yml"
        yml.write_text(
            "services:\n"
            "  standalone:\n"
            "    image: app:latest\n"
        )

        mgr = ServiceManager(str(tmp_path))
        result = mgr.get_depends_on("simple")

        assert result == []

    def test_depends_on_as_dict_format(self, tmp_path):
        """Handles depends_on as dict (condition syntax)."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()

        yml = services_available / "health.yml"
        yml.write_text(
            "services:\n"
            "  db:\n"
            "    image: postgres:15\n"
            "  app:\n"
            "    image: app:latest\n"
            "    depends_on:\n"
            "      db:\n"
            "        condition: service_healthy\n"
            "      external-service:\n"
            "        condition: service_started\n"
        )

        mgr = ServiceManager(str(tmp_path))
        result = mgr.get_depends_on("health")

        assert result == ["external-service"]

    def test_mixed_list_and_dict_format(self, tmp_path):
        """Handles mixed depends_on list and dict styles (though not typical)."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()

        yml = services_available / "mixed.yml"
        yml.write_text(
            "services:\n"
            "  internal:\n"
            "    image: postgres:15\n"
            "  service1:\n"
            "    image: app1:latest\n"
            "    depends_on:\n"
            "      - internal\n"
            "      - external1\n"
            "  service2:\n"
            "    image: app2:latest\n"
            "    depends_on:\n"
            "      external2:\n"
            "        condition: service_healthy\n"
        )

        mgr = ServiceManager(str(tmp_path))
        result = mgr.get_depends_on("mixed")

        assert set(result) == {"external1", "external2"}

    def test_nonexistent_service_returns_empty(self, tmp_path):
        """Non-existent service file returns empty list."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()

        mgr = ServiceManager(str(tmp_path))
        result = mgr.get_depends_on("nonexistent")

        assert result == []

    def test_invalid_yaml_returns_empty(self, tmp_path):
        """Invalid YAML returns empty list (graceful degradation)."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()

        yml = services_available / "broken.yml"
        yml.write_text("this is { not valid: yaml: [")

        mgr = ServiceManager(str(tmp_path))
        result = mgr.get_depends_on("broken")

        assert result == []

    def test_yaml_without_services_key_returns_empty(self, tmp_path):
        """YAML without 'services' key returns empty list."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()

        yml = services_available / "noservices.yml"
        yml.write_text("networks:\n  test: {}\n")

        mgr = ServiceManager(str(tmp_path))
        result = mgr.get_depends_on("noservices")

        assert result == []

    def test_multiple_services_each_with_deps(self, tmp_path):
        """Multiple services in file, collect deps from all."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()

        yml = services_available / "multi.yml"
        yml.write_text(
            "services:\n"
            "  db:\n"
            "    image: postgres:15\n"
            "  service1:\n"
            "    image: app1:latest\n"
            "    depends_on:\n"
            "      - db\n"
            "      - external-auth\n"
            "  service2:\n"
            "    image: app2:latest\n"
            "    depends_on:\n"
            "      - db\n"
            "      - external-cache\n"
        )

        mgr = ServiceManager(str(tmp_path))
        result = mgr.get_depends_on("multi")

        # Should get external deps from both service1 and service2
        assert set(result) == {"external-auth", "external-cache"}

    def test_returns_sorted_list(self, tmp_path):
        """Result is sorted for consistency."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()

        yml = services_available / "sorted.yml"
        yml.write_text(
            "services:\n"
            "  app:\n"
            "    image: app:latest\n"
            "    depends_on:\n"
            "      - zebra\n"
            "      - alpha\n"
            "      - middle\n"
        )

        mgr = ServiceManager(str(tmp_path))
        result = mgr.get_depends_on("sorted")

        assert result == ["alpha", "middle", "zebra"]

    def test_deduplicates_deps(self, tmp_path):
        """Duplicate dependencies are deduplicated."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()

        yml = services_available / "dupes.yml"
        yml.write_text(
            "services:\n"
            "  service1:\n"
            "    image: app1:latest\n"
            "    depends_on:\n"
            "      - external-service\n"
            "  service2:\n"
            "    image: app2:latest\n"
            "    depends_on:\n"
            "      - external-service\n"
            "      - another-external\n"
        )

        mgr = ServiceManager(str(tmp_path))
        result = mgr.get_depends_on("dupes")

        assert set(result) == {"external-service", "another-external"}
        # Verify it's actually a list (not dict)
        assert isinstance(result, list)

    def test_handles_empty_depends_on_list(self, tmp_path):
        """Handles empty depends_on list."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()

        yml = services_available / "empty.yml"
        yml.write_text(
            "services:\n"
            "  app:\n"
            "    image: app:latest\n"
            "    depends_on: []\n"
        )

        mgr = ServiceManager(str(tmp_path))
        result = mgr.get_depends_on("empty")

        assert result == []

    def test_handles_empty_depends_on_dict(self, tmp_path):
        """Handles empty depends_on dict."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()

        yml = services_available / "emptydict.yml"
        yml.write_text(
            "services:\n"
            "  app:\n"
            "    image: app:latest\n"
            "    depends_on: {}\n"
        )

        mgr = ServiceManager(str(tmp_path))
        result = mgr.get_depends_on("emptydict")

        assert result == []

    def test_real_world_paperless_ngx_example(self, tmp_path):
        """Real-world example: paperless-ngx with all internal deps."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()

        yml = services_available / "paperless-ngx.yml"
        yml.write_text(
            "services:\n"
            "  broker:\n"
            "    image: redis:7\n"
            "  db:\n"
            "    image: mariadb:10\n"
            "  gotenberg:\n"
            "    image: gotenberg/gotenberg:7.6\n"
            "  tika:\n"
            "    image: apache/tika:latest\n"
            "  paperless-ngx:\n"
            "    image: paperless-ngx:latest\n"
            "    depends_on:\n"
            "      - broker\n"
            "      - db\n"
            "      - gotenberg\n"
            "      - tika\n"
        )

        mgr = ServiceManager(str(tmp_path))
        result = mgr.get_depends_on("paperless-ngx")

        # All deps are internal
        assert result == []

    def test_service_depends_on_itself_excluded(self, tmp_path):
        """Service doesn't list itself as external if somehow in depends_on."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()

        yml = services_available / "self.yml"
        yml.write_text(
            "services:\n"
            "  app:\n"
            "    image: app:latest\n"
            "    depends_on:\n"
            "      - app\n"
            "      - external\n"
        )

        mgr = ServiceManager(str(tmp_path))
        result = mgr.get_depends_on("self")

        # Self-reference filtered out
        assert result == ["external"]
