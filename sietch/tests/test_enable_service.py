"""Tests for enable_service.py - service dependency resolution and enabling wizard."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from enable_service import EnableServiceWizard


class TestIsEnabled:
    """Tests for _is_enabled() - check if service is enabled."""

    def test_returns_true_when_enabled(self, tmp_path):
        """Should return True when service symlink exists."""
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (services_enabled / "plex.yml").write_text("services:\n")

        wizard = EnableServiceWizard(str(tmp_path))
        assert wizard._is_enabled("plex") is True

    def test_returns_false_when_not_enabled(self, tmp_path):
        """Should return False when service symlink does not exist."""
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()

        wizard = EnableServiceWizard(str(tmp_path))
        assert wizard._is_enabled("plex") is False


class TestPromptYesNo:
    """Tests for _prompt_yes_no() - user prompts."""

    def test_yes_response_returns_true(self, tmp_path, monkeypatch):
        """Should return True for 'y' response."""
        monkeypatch.setattr('builtins.input', lambda _: 'y')

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard._prompt_yes_no("Enable service?")

        assert result is True

    def test_yes_full_response_returns_true(self, tmp_path, monkeypatch):
        """Should return True for 'yes' response."""
        monkeypatch.setattr('builtins.input', lambda _: 'yes')

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard._prompt_yes_no("Enable service?")

        assert result is True

    def test_no_response_returns_false(self, tmp_path, monkeypatch):
        """Should return False for 'n' response."""
        monkeypatch.setattr('builtins.input', lambda _: 'n')

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard._prompt_yes_no("Enable service?")

        assert result is False

    def test_empty_response_uses_default_true(self, tmp_path, monkeypatch):
        """Should use default when user presses enter (default=True)."""
        monkeypatch.setattr('builtins.input', lambda _: '')

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard._prompt_yes_no("Enable service?", default=True)

        assert result is True

    def test_empty_response_uses_default_false(self, tmp_path, monkeypatch):
        """Should use default when user presses enter (default=False)."""
        monkeypatch.setattr('builtins.input', lambda _: '')

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard._prompt_yes_no("Enable service?", default=False)

        assert result is False

    def test_eoferror_defaults_to_false(self, tmp_path, monkeypatch):
        """Should default to False on EOFError (non-TTY context)."""
        def raise_eoferror(_):
            raise EOFError

        monkeypatch.setattr('builtins.input', raise_eoferror)

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard._prompt_yes_no("Enable service?", default=False)

        assert result is False

    def test_keyboard_interrupt_defaults_to_false(self, tmp_path, monkeypatch):
        """Should default to False on KeyboardInterrupt."""
        def raise_interrupt(_):
            raise KeyboardInterrupt

        monkeypatch.setattr('builtins.input', raise_interrupt)

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard._prompt_yes_no("Enable service?", default=False)

        assert result is False


class TestDoEnable:
    """Tests for _do_enable() - actually enable a service."""

    def test_creates_symlink(self, tmp_path):
        """Should create symlink from services-available to services-enabled."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (tmp_path / "services-scaffold").mkdir()
        (tmp_path / "etc").mkdir()

        service_yml = services_available / "plex.yml"
        service_yml.write_text("services:\n  plex:\n    image: plex:latest\n")

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard._do_enable("plex")

        assert result is True
        symlink = services_enabled / "plex.yml"
        assert symlink.exists()
        assert symlink.is_symlink()

    def test_already_enabled_skips_symlink(self, tmp_path):
        """Should skip symlink creation if already exists."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (tmp_path / "services-scaffold").mkdir()
        (tmp_path / "etc").mkdir()

        service_yml = services_available / "plex.yml"
        service_yml.write_text("services:\n  plex:\n    image: plex:latest\n")

        # Create symlink manually
        (services_enabled / "plex.yml").symlink_to(service_yml)

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard._do_enable("plex")

        # Should succeed (no error if symlink exists)
        assert result is True

    def test_nonexistent_service_returns_false(self, tmp_path, capsys):
        """Should return False when service doesn't exist."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard._do_enable("nonexistent")

        assert result is False
        captured = capsys.readouterr()
        assert "not found" in captured.out

    def test_runs_scaffolding(self, tmp_path):
        """Should run scaffolding after creating symlink."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        scaffold_dir = tmp_path / "services-scaffold" / "plex"
        scaffold_dir.mkdir(parents=True)
        (tmp_path / "etc").mkdir()

        service_yml = services_available / "plex.yml"
        service_yml.write_text("services:\n  plex:\n    image: plex:latest\n")

        # Create scaffold template
        (scaffold_dir / "env.template").write_text("PLEX_TAG=${PLEX_TAG:-latest}")

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard._do_enable("plex")

        assert result is True
        # Check that scaffolding created env file
        assert (services_enabled / "plex.env").exists()

    def test_restores_archived_env(self, tmp_path, monkeypatch):
        """Should restore archived .env if it exists."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (tmp_path / "services-scaffold").mkdir()
        (tmp_path / "etc").mkdir()

        # Create archive
        backups_dir = tmp_path / "backups" / "env-archives" / "plex"
        backups_dir.mkdir(parents=True)
        (backups_dir / "plex.env").write_text("ARCHIVED_VAR=archived_value")

        service_yml = services_available / "plex.yml"
        service_yml.write_text("services:\n  plex:\n    image: plex:latest\n")

        # Mock user input to select restore (choice 1)
        monkeypatch.setattr('builtins.input', lambda _: '1')

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard._do_enable("plex")

        assert result is True


class TestEnableServiceBasic:
    """Tests for enable_service() - basic enabling."""

    def test_enable_service_creates_symlink(self, tmp_path):
        """Should create symlink when enabling service."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (tmp_path / "services-scaffold").mkdir()
        (tmp_path / "etc").mkdir()

        service_yml = services_available / "simple.yml"
        service_yml.write_text("services:\n  simple:\n    image: simple:latest\n")

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard.enable_service("simple")

        assert result is True
        assert (services_enabled / "simple.yml").exists()

    def test_already_enabled_returns_true(self, tmp_path, capsys):
        """Should return True without action if already enabled."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()

        service_yml = services_available / "plex.yml"
        service_yml.write_text("services:\n  plex:\n    image: plex:latest\n")

        # Enable it first
        (services_enabled / "plex.yml").symlink_to(service_yml)

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard.enable_service("plex")

        assert result is True
        captured = capsys.readouterr()
        assert "already enabled" in captured.out

    def test_nonexistent_service_returns_false(self, tmp_path, capsys):
        """Should return False when service doesn't exist."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard.enable_service("nonexistent")

        assert result is False
        captured = capsys.readouterr()
        assert "not found" in captured.out


class TestDependencyResolution:
    """Tests for dependency resolution."""

    def test_enables_required_dependencies_first(self, tmp_path, capsys):
        """Should enable dependencies before the service."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (tmp_path / "services-scaffold").mkdir()
        (tmp_path / "etc").mkdir()

        # Create dependency service
        (services_available / "redis.yml").write_text(
            "services:\n  redis:\n    image: redis:latest\n"
        )

        # Create service with dependency
        (services_available / "app.yml").write_text(
            "services:\n"
            "  app:\n"
            "    image: app:latest\n"
            "    depends_on:\n"
            "      - redis\n"
        )

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard.enable_service("app")

        assert result is True
        # Both should be enabled
        assert (services_enabled / "redis.yml").exists()
        assert (services_enabled / "app.yml").exists()

        captured = capsys.readouterr()
        assert "Enabling required dependency: redis" in captured.out

    def test_recursive_dependency_resolution(self, tmp_path):
        """Should recursively resolve dependencies (A -> B -> C)."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (tmp_path / "services-scaffold").mkdir()
        (tmp_path / "etc").mkdir()

        # C has no dependencies
        (services_available / "c.yml").write_text(
            "services:\n  c:\n    image: c:latest\n"
        )

        # B depends on C
        (services_available / "b.yml").write_text(
            "services:\n"
            "  b:\n"
            "    image: b:latest\n"
            "    depends_on:\n"
            "      - c\n"
        )

        # A depends on B
        (services_available / "a.yml").write_text(
            "services:\n"
            "  a:\n"
            "    image: a:latest\n"
            "    depends_on:\n"
            "      - b\n"
        )

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard.enable_service("a")

        assert result is True
        # All three should be enabled
        assert (services_enabled / "a.yml").exists()
        assert (services_enabled / "b.yml").exists()
        assert (services_enabled / "c.yml").exists()

    def test_dependency_already_enabled_skips(self, tmp_path):
        """Should skip dependencies that are already enabled."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (tmp_path / "services-scaffold").mkdir()
        (tmp_path / "etc").mkdir()

        redis_yml = services_available / "redis.yml"
        redis_yml.write_text("services:\n  redis:\n    image: redis:latest\n")

        # Enable redis manually
        (services_enabled / "redis.yml").symlink_to(redis_yml)

        # Create service depending on redis
        (services_available / "app.yml").write_text(
            "services:\n"
            "  app:\n"
            "    image: app:latest\n"
            "    depends_on:\n"
            "      - redis\n"
        )

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard.enable_service("app")

        assert result is True
        assert (services_enabled / "app.yml").exists()

    def test_circular_dependency_handled(self, tmp_path, capsys):
        """Should handle circular dependencies without infinite loop."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (tmp_path / "services-scaffold").mkdir()
        (tmp_path / "etc").mkdir()

        # A depends on B
        (services_available / "a.yml").write_text(
            "services:\n"
            "  a:\n"
            "    image: a:latest\n"
            "    depends_on:\n"
            "      - b\n"
        )

        # B depends on A (circular)
        (services_available / "b.yml").write_text(
            "services:\n"
            "  b:\n"
            "    image: b:latest\n"
            "    depends_on:\n"
            "      - a\n"
        )

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard.enable_service("a")

        # Should succeed without infinite loop
        assert result is True
        captured = capsys.readouterr()
        # Should see "already processed" message
        assert "already processed this session" in captured.out or "already enabled" in captured.out

    def test_failed_dependency_returns_false(self, tmp_path, capsys):
        """Should return False if dependency fails to enable."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()

        # Create service with dependency on nonexistent service
        (services_available / "app.yml").write_text(
            "services:\n"
            "  app:\n"
            "    image: app:latest\n"
            "    depends_on:\n"
            "      - nonexistent\n"
        )

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard.enable_service("app")

        assert result is False
        captured = capsys.readouterr()
        assert "Failed to enable dependency" in captured.out


class TestOptionalServices:
    """Tests for optional service prompts."""

    def test_prompts_for_optional_service(self, tmp_path, monkeypatch):
        """Should prompt user for optional service."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (tmp_path / "services-scaffold").mkdir()
        (tmp_path / "etc").mkdir()

        # Create optional service
        (services_available / "ollama.yml").write_text(
            "services:\n  ollama:\n    image: ollama:latest\n"
        )

        # Create service with optional service metadata
        (services_available / "paperless.yml").write_text(
            "# description: Document management\n"
            "# optional-service: ollama\n"
            "# optional-prompt: Enable Ollama for AI features?\n"
            "services:\n  paperless:\n    image: paperless:latest\n"
        )

        prompts = []
        monkeypatch.setattr('builtins.input', lambda p: prompts.append(p) or 'n')

        wizard = EnableServiceWizard(str(tmp_path))
        wizard.enable_service("paperless")

        # Should have prompted for ollama
        assert any("Ollama" in p for p in prompts)

    def test_optional_service_enabled_on_yes(self, tmp_path, monkeypatch):
        """Should enable optional service when user says yes."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (tmp_path / "services-scaffold").mkdir()
        (tmp_path / "etc").mkdir()

        (services_available / "ollama.yml").write_text(
            "services:\n  ollama:\n    image: ollama:latest\n"
        )

        (services_available / "paperless.yml").write_text(
            "# description: Document management\n"
            "# optional-service: ollama\n"
            "# optional-prompt: Enable Ollama?\n"
            "services:\n  paperless:\n    image: paperless:latest\n"
        )

        # Say yes to optional service
        monkeypatch.setattr('builtins.input', lambda _: 'y')

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard.enable_service("paperless")

        assert result is True
        # Both should be enabled
        assert (services_enabled / "paperless.yml").exists()
        assert (services_enabled / "ollama.yml").exists()

    def test_optional_service_skipped_on_no(self, tmp_path, monkeypatch):
        """Should skip optional service when user says no."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (tmp_path / "services-scaffold").mkdir()
        (tmp_path / "etc").mkdir()

        (services_available / "ollama.yml").write_text(
            "services:\n  ollama:\n    image: ollama:latest\n"
        )

        (services_available / "paperless.yml").write_text(
            "# description: Document management\n"
            "# optional-service: ollama\n"
            "# optional-prompt: Enable Ollama?\n"
            "services:\n  paperless:\n    image: paperless:latest\n"
        )

        # Say no to optional service
        monkeypatch.setattr('builtins.input', lambda _: 'n')

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard.enable_service("paperless")

        assert result is True
        # Only paperless should be enabled
        assert (services_enabled / "paperless.yml").exists()
        assert not (services_enabled / "ollama.yml").exists()

    def test_multiple_optional_services(self, tmp_path, monkeypatch):
        """Should prompt for multiple optional services."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (tmp_path / "services-scaffold").mkdir()
        (tmp_path / "etc").mkdir()

        (services_available / "ollama.yml").write_text(
            "services:\n  ollama:\n    image: ollama:latest\n"
        )
        (services_available / "openwebui.yml").write_text(
            "services:\n  openwebui:\n    image: openwebui:latest\n"
        )

        (services_available / "app.yml").write_text(
            "# description: App\n"
            "# optional-service: ollama\n"
            "# optional-prompt: Enable Ollama?\n"
            "# optional-service: openwebui\n"
            "# optional-prompt: Enable OpenWebUI?\n"
            "services:\n  app:\n    image: app:latest\n"
        )

        responses = iter(['y', 'n'])  # Yes to first, no to second
        monkeypatch.setattr('builtins.input', lambda _: next(responses))

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard.enable_service("app")

        assert result is True
        assert (services_enabled / "app.yml").exists()
        assert (services_enabled / "ollama.yml").exists()
        assert not (services_enabled / "openwebui.yml").exists()


class TestOptionalGroups:
    """Tests for optional service groups."""

    def test_prompts_for_optional_group(self, tmp_path, monkeypatch):
        """Should prompt user for optional group."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (tmp_path / "services-scaffold").mkdir()
        (tmp_path / "etc").mkdir()

        (services_available / "ollama.yml").write_text(
            "services:\n  ollama:\n    image: ollama:latest\n"
        )
        (services_available / "openwebui.yml").write_text(
            "services:\n  openwebui:\n    image: openwebui:latest\n"
        )

        (services_available / "app.yml").write_text(
            "# description: App\n"
            "# optional-group: ai-features\n"
            "# optional-group-prompt: Enable AI features (Ollama + OpenWebUI)?\n"
            "# optional-group-services: ollama, openwebui\n"
            "services:\n  app:\n    image: app:latest\n"
        )

        prompts = []
        monkeypatch.setattr('builtins.input', lambda p: prompts.append(p) or 'n')

        wizard = EnableServiceWizard(str(tmp_path))
        wizard.enable_service("app")

        # Should have prompted for AI features
        assert any("AI features" in p for p in prompts)

    def test_optional_group_enables_all_services(self, tmp_path, monkeypatch):
        """Should enable all services in group when user says yes."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (tmp_path / "services-scaffold").mkdir()
        (tmp_path / "etc").mkdir()

        (services_available / "ollama.yml").write_text(
            "services:\n  ollama:\n    image: ollama:latest\n"
        )
        (services_available / "openwebui.yml").write_text(
            "services:\n  openwebui:\n    image: openwebui:latest\n"
        )

        (services_available / "app.yml").write_text(
            "# description: App\n"
            "# optional-group: ai-features\n"
            "# optional-group-prompt: Enable AI features?\n"
            "# optional-group-services: ollama, openwebui\n"
            "services:\n  app:\n    image: app:latest\n"
        )

        # Say yes to group
        monkeypatch.setattr('builtins.input', lambda _: 'y')

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard.enable_service("app")

        assert result is True
        # All services should be enabled
        assert (services_enabled / "app.yml").exists()
        assert (services_enabled / "ollama.yml").exists()
        assert (services_enabled / "openwebui.yml").exists()

    def test_optional_group_skipped_on_no(self, tmp_path, monkeypatch):
        """Should skip all services in group when user says no."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (tmp_path / "services-scaffold").mkdir()
        (tmp_path / "etc").mkdir()

        (services_available / "ollama.yml").write_text(
            "services:\n  ollama:\n    image: ollama:latest\n"
        )
        (services_available / "openwebui.yml").write_text(
            "services:\n  openwebui:\n    image: openwebui:latest\n"
        )

        (services_available / "app.yml").write_text(
            "# description: App\n"
            "# optional-group: ai-features\n"
            "# optional-group-prompt: Enable AI features?\n"
            "# optional-group-services: ollama, openwebui\n"
            "services:\n  app:\n    image: app:latest\n"
        )

        # Say no to group
        monkeypatch.setattr('builtins.input', lambda _: 'n')

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard.enable_service("app")

        assert result is True
        # Only main service should be enabled
        assert (services_enabled / "app.yml").exists()
        assert not (services_enabled / "ollama.yml").exists()
        assert not (services_enabled / "openwebui.yml").exists()

    def test_multiple_optional_groups(self, tmp_path, monkeypatch):
        """Should handle multiple optional groups."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (tmp_path / "services-scaffold").mkdir()
        (tmp_path / "etc").mkdir()

        # AI group services
        (services_available / "ollama.yml").write_text(
            "services:\n  ollama:\n    image: ollama:latest\n"
        )

        # Media group services
        (services_available / "plex.yml").write_text(
            "services:\n  plex:\n    image: plex:latest\n"
        )

        (services_available / "app.yml").write_text(
            "# description: App\n"
            "# optional-group: ai-features\n"
            "# optional-group-prompt: Enable AI features?\n"
            "# optional-group-services: ollama\n"
            "# optional-group: media-features\n"
            "# optional-group-prompt: Enable media features?\n"
            "# optional-group-services: plex\n"
            "services:\n  app:\n    image: app:latest\n"
        )

        responses = iter(['y', 'n'])  # Yes to AI, no to media
        monkeypatch.setattr('builtins.input', lambda _: next(responses))

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard.enable_service("app")

        assert result is True
        assert (services_enabled / "app.yml").exists()
        assert (services_enabled / "ollama.yml").exists()
        assert not (services_enabled / "plex.yml").exists()


class TestSessionTracking:
    """Tests for session tracking to prevent duplicate processing."""

    def test_tracks_enabled_services(self, tmp_path):
        """Should track services enabled in this session."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (tmp_path / "services-scaffold").mkdir()
        (tmp_path / "etc").mkdir()

        (services_available / "service1.yml").write_text(
            "services:\n  service1:\n    image: service1:latest\n"
        )

        wizard = EnableServiceWizard(str(tmp_path))
        wizard.enable_service("service1")

        # Should be tracked
        assert "service1" in wizard.enabled_this_session

    def test_skips_already_processed_service(self, tmp_path, capsys):
        """Should skip service already processed this session."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (tmp_path / "services-scaffold").mkdir()
        (tmp_path / "etc").mkdir()

        (services_available / "service1.yml").write_text(
            "services:\n  service1:\n    image: service1:latest\n"
        )

        wizard = EnableServiceWizard(str(tmp_path))

        # Enable once
        wizard.enable_service("service1")

        # Remove symlink to simulate "not enabled"
        (services_enabled / "service1.yml").unlink()

        # Try to enable again
        result = wizard.enable_service("service1")

        assert result is True
        captured = capsys.readouterr()
        assert "already processed this session" in captured.out


class TestComplexScenarios:
    """Tests for complex real-world scenarios."""

    def test_service_with_deps_and_optionals(self, tmp_path, monkeypatch):
        """Should handle service with both dependencies and optional services."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (tmp_path / "services-scaffold").mkdir()
        (tmp_path / "etc").mkdir()

        # Required dependency
        (services_available / "redis.yml").write_text(
            "services:\n  redis:\n    image: redis:latest\n"
        )

        # Optional service
        (services_available / "ollama.yml").write_text(
            "services:\n  ollama:\n    image: ollama:latest\n"
        )

        # Main service with both
        (services_available / "app.yml").write_text(
            "# description: App\n"
            "# optional-service: ollama\n"
            "# optional-prompt: Enable Ollama?\n"
            "services:\n"
            "  app:\n"
            "    image: app:latest\n"
            "    depends_on:\n"
            "      - redis\n"
        )

        # Say yes to optional
        monkeypatch.setattr('builtins.input', lambda _: 'y')

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard.enable_service("app")

        assert result is True
        # All three should be enabled
        assert (services_enabled / "app.yml").exists()
        assert (services_enabled / "redis.yml").exists()
        assert (services_enabled / "ollama.yml").exists()

    def test_dependency_chain_with_optionals(self, tmp_path, monkeypatch):
        """Should handle dependency chain where dependencies have optionals."""
        services_available = tmp_path / "services-available"
        services_available.mkdir()
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (tmp_path / "services-scaffold").mkdir()
        (tmp_path / "etc").mkdir()

        # Base service
        (services_available / "base.yml").write_text(
            "services:\n  base:\n    image: base:latest\n"
        )

        # Optional for middleware
        (services_available / "cache.yml").write_text(
            "services:\n  cache:\n    image: cache:latest\n"
        )

        # Middleware with dependency and optional
        (services_available / "middleware.yml").write_text(
            "# optional-service: cache\n"
            "# optional-prompt: Enable caching?\n"
            "services:\n"
            "  middleware:\n"
            "    image: middleware:latest\n"
            "    depends_on:\n"
            "      - base\n"
        )

        # App depends on middleware
        (services_available / "app.yml").write_text(
            "services:\n"
            "  app:\n"
            "    image: app:latest\n"
            "    depends_on:\n"
            "      - middleware\n"
        )

        # Say yes to cache when prompted
        monkeypatch.setattr('builtins.input', lambda _: 'y')

        wizard = EnableServiceWizard(str(tmp_path))
        result = wizard.enable_service("app")

        assert result is True
        # All four should be enabled
        assert (services_enabled / "app.yml").exists()
        assert (services_enabled / "middleware.yml").exists()
        assert (services_enabled / "base.yml").exists()
        assert (services_enabled / "cache.yml").exists()
