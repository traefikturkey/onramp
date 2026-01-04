"""Tests for traefik_hosts.py - Traefik external Host() rule extraction."""

import pytest
import sys
from pathlib import Path

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from traefik_hosts import TraefikHostsExtractor


# Helper function to create Traefik YAML with proper formatting
def traefik_yaml(router_name: str, host_var: str, domain_var: str = "HOST_DOMAIN") -> str:
    """Generate Traefik YAML with Host() rule using Go template syntax."""
    return (
        f'http:\n'
        f'  routers:\n'
        f'    {router_name}:\n'
        f'      rule: "Host(`{{{{env "{host_var}"}}}}.{{{{env "{domain_var}"}}}}`)"'
    )


class TestJoyrideEnabledCheck:
    """Tests for joyride enabled check."""

    def test_returns_false_when_joyride_not_enabled(self, tmp_path):
        """Should return False when joyride.yml does not exist."""
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()

        extractor = TraefikHostsExtractor(base_dir=tmp_path)

        assert extractor.check_joyride_enabled() is False

    def test_returns_true_when_joyride_enabled(self, tmp_path):
        """Should return True when joyride.yml exists."""
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (services_enabled / "joyride.yml").write_text("# joyride config")

        extractor = TraefikHostsExtractor(base_dir=tmp_path)

        assert extractor.check_joyride_enabled() is True


class TestEnvFileLoading:
    """Tests for environment file loading."""

    def test_loads_env_file(self, tmp_path):
        """Should load variables from .env file."""
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (services_enabled / ".env").write_text("HOST_DOMAIN=example.com\nHOSTIP=192.168.1.10\n")

        extractor = TraefikHostsExtractor(base_dir=tmp_path, env_vars={})
        extractor.load_env_files()

        assert extractor.env_vars["HOST_DOMAIN"] == "example.com"
        assert extractor.env_vars["HOSTIP"] == "192.168.1.10"

    def test_loads_env_external_file(self, tmp_path):
        """Should load variables from .env.external file."""
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (services_enabled / ".env.external").write_text("HOMEASSISTANT_HOST_NAME=hass\n")

        extractor = TraefikHostsExtractor(base_dir=tmp_path, env_vars={})
        extractor.load_env_files()

        assert extractor.env_vars["HOMEASSISTANT_HOST_NAME"] == "hass"

    def test_skips_comments_and_empty_lines(self, tmp_path):
        """Should skip comments and empty lines in env files."""
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (services_enabled / ".env").write_text(
            "# This is a comment\n"
            "\n"
            "VALID_VAR=value\n"
            "# Another comment\n"
        )

        extractor = TraefikHostsExtractor(base_dir=tmp_path, env_vars={})
        extractor.load_env_files()

        assert extractor.env_vars.get("VALID_VAR") == "value"
        assert "# This is a comment" not in extractor.env_vars

    def test_removes_quotes_from_values(self, tmp_path):
        """Should remove surrounding quotes from values."""
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (services_enabled / ".env").write_text(
            'DOUBLE_QUOTED="value1"\n'
            "SINGLE_QUOTED='value2'\n"
            "UNQUOTED=value3\n"
        )

        extractor = TraefikHostsExtractor(base_dir=tmp_path, env_vars={})
        extractor.load_env_files()

        assert extractor.env_vars["DOUBLE_QUOTED"] == "value1"
        assert extractor.env_vars["SINGLE_QUOTED"] == "value2"
        assert extractor.env_vars["UNQUOTED"] == "value3"

    def test_does_not_override_existing_env_vars(self, tmp_path):
        """Should not override existing env vars (allows CLI override)."""
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (services_enabled / ".env").write_text("HOSTIP=192.168.1.10\n")

        extractor = TraefikHostsExtractor(
            base_dir=tmp_path,
            env_vars={"HOSTIP": "10.0.0.1"},  # Pre-set
        )
        extractor.load_env_files()

        assert extractor.env_vars["HOSTIP"] == "10.0.0.1"


class TestTemplateResolution:
    """Tests for {{env "VAR"}} template resolution."""

    def test_resolves_single_variable(self):
        """Should resolve a single {{env "VAR"}} template."""
        extractor = TraefikHostsExtractor(
            env_vars={"HOST_DOMAIN": "example.com"},
        )

        result = extractor.resolve_template('{{env "HOST_DOMAIN"}}')

        assert result == "example.com"

    def test_resolves_multiple_variables(self):
        """Should resolve multiple {{env "VAR"}} templates."""
        extractor = TraefikHostsExtractor(
            env_vars={
                "HOMEASSISTANT_HOST_NAME": "hass",
                "HOST_DOMAIN": "example.com",
            },
        )

        result = extractor.resolve_template(
            '{{env "HOMEASSISTANT_HOST_NAME"}}.{{env "HOST_DOMAIN"}}'
        )

        assert result == "hass.example.com"

    def test_returns_none_for_missing_variable(self):
        """Should return None when variable is not set."""
        extractor = TraefikHostsExtractor(env_vars={})

        result = extractor.resolve_template('{{env "MISSING_VAR"}}')

        assert result is None

    def test_returns_none_for_empty_variable(self):
        """Should return None when variable is empty."""
        extractor = TraefikHostsExtractor(
            env_vars={"EMPTY_VAR": ""},
        )

        result = extractor.resolve_template('{{env "EMPTY_VAR"}}')

        assert result is None

    def test_returns_none_if_any_variable_missing(self):
        """Should return None if any variable in the template is missing."""
        extractor = TraefikHostsExtractor(
            env_vars={"HOST_DOMAIN": "example.com"},
        )

        result = extractor.resolve_template(
            '{{env "MISSING_NAME"}}.{{env "HOST_DOMAIN"}}'
        )

        assert result is None


class TestHostExtraction:
    """Tests for Host() rule extraction from YAML files."""

    def test_extracts_single_host(self, tmp_path):
        """Should extract a single Host() rule."""
        external_enabled = tmp_path / "external-enabled"
        external_enabled.mkdir()
        (external_enabled / "homeassistant.yml").write_text(
            traefik_yaml("homeassistant", "HOMEASSISTANT_HOST_NAME")
        )

        extractor = TraefikHostsExtractor(
            base_dir=tmp_path,
            env_vars={
                "HOMEASSISTANT_HOST_NAME": "hass",
                "HOST_DOMAIN": "example.com",
            },
        )

        hosts = extractor.extract_hosts_from_file(
            external_enabled / "homeassistant.yml"
        )

        assert len(hosts) == 1
        assert hosts[0] == ("hass.example.com", "homeassistant")

    def test_extracts_multiple_hosts_from_file(self, tmp_path):
        """Should extract multiple Host() rules from a single file."""
        yaml_content = (
            'http:\n'
            '  routers:\n'
            '    service1:\n'
            '      rule: "Host(`{{env "SVC1_HOST_NAME"}}.{{env "HOST_DOMAIN"}}`)"'
            '\n'
            '    service2:\n'
            '      rule: "Host(`{{env "SVC2_HOST_NAME"}}.{{env "HOST_DOMAIN"}}`)"'
        )
        external_enabled = tmp_path / "external-enabled"
        external_enabled.mkdir()
        (external_enabled / "multi.yml").write_text(yaml_content)

        extractor = TraefikHostsExtractor(
            base_dir=tmp_path,
            env_vars={
                "SVC1_HOST_NAME": "svc1",
                "SVC2_HOST_NAME": "svc2",
                "HOST_DOMAIN": "example.com",
            },
        )

        hosts = extractor.extract_hosts_from_file(external_enabled / "multi.yml")

        assert len(hosts) == 2
        assert ("svc1.example.com", "multi") in hosts
        assert ("svc2.example.com", "multi") in hosts

    def test_skips_host_with_missing_variable(self, tmp_path, capsys):
        """Should skip hosts where required variable is missing."""
        external_enabled = tmp_path / "external-enabled"
        external_enabled.mkdir()
        (external_enabled / "service.yml").write_text(
            traefik_yaml("service", "MISSING_HOST_NAME")
        )

        extractor = TraefikHostsExtractor(
            base_dir=tmp_path,
            env_vars={"HOST_DOMAIN": "example.com"},
        )

        hosts = extractor.extract_hosts_from_file(external_enabled / "service.yml")

        assert len(hosts) == 0

        # Check that warning was printed
        captured = capsys.readouterr()
        assert "Skipped service" in captured.err
        assert "MISSING_HOST_NAME" in captured.err


class TestMiddlewareExclusion:
    """Tests for middleware-only file exclusion."""

    def test_excludes_middleware_yml(self, tmp_path):
        """Should exclude middleware.yml from file list."""
        external_enabled = tmp_path / "external-enabled"
        external_enabled.mkdir()
        (external_enabled / "middleware.yml").write_text("# middlewares only")
        (external_enabled / "homeassistant.yml").write_text("# has routers")

        extractor = TraefikHostsExtractor(base_dir=tmp_path)
        files = extractor.get_external_files()

        filenames = [f.name for f in files]
        assert "middleware.yml" not in filenames
        assert "homeassistant.yml" in filenames

    def test_excludes_all_middleware_only_files(self, tmp_path):
        """Should exclude all middleware-only files."""
        external_enabled = tmp_path / "external-enabled"
        external_enabled.mkdir()

        middleware_files = [
            "middleware.yml",
            "authentik_middleware.yml",
            "authelia_middlewares.yml",
            "crowdsec-bouncer.yml",
        ]

        for name in middleware_files:
            (external_enabled / name).write_text("# middleware only")

        (external_enabled / "valid.yml").write_text("# has routers")

        extractor = TraefikHostsExtractor(base_dir=tmp_path)
        files = extractor.get_external_files()

        filenames = [f.name for f in files]
        for name in middleware_files:
            assert name not in filenames
        assert "valid.yml" in filenames


class TestHostsFileDeduplication:
    """Tests for FQDN-based deduplication."""

    def test_deduplicates_by_fqdn(self, tmp_path):
        """Should deduplicate entries by FQDN, keeping latest."""
        # Set up joyride as enabled
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (services_enabled / "joyride.yml").write_text("# enabled")
        (services_enabled / ".env").write_text("HOSTIP=192.168.1.10\nHOST_DOMAIN=example.com\n")
        (services_enabled / ".env.external").write_text("SVC_HOST_NAME=svc\n")

        # Create existing hosts file with old IP
        hosts_dir = tmp_path / "etc" / "joyride" / "hosts.d"
        hosts_dir.mkdir(parents=True)
        (hosts_dir / "hosts").write_text("10.0.0.1 svc.example.com\n")

        # Create external config
        external_enabled = tmp_path / "external-enabled"
        external_enabled.mkdir()
        (external_enabled / "service.yml").write_text(
            traefik_yaml("svc", "SVC_HOST_NAME")
        )

        extractor = TraefikHostsExtractor(base_dir=tmp_path, env_vars={})

        result = extractor.sync()

        assert result == 0

        # Verify the old IP was replaced with new HOSTIP
        content = (hosts_dir / "hosts").read_text()
        assert "192.168.1.10 svc.example.com" in content
        assert "10.0.0.1" not in content

    def test_preserves_comment_lines(self, tmp_path):
        """Should preserve comment lines from existing hosts file."""
        # Set up joyride as enabled
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (services_enabled / "joyride.yml").write_text("# enabled")
        (services_enabled / ".env").write_text("HOSTIP=192.168.1.10\nHOST_DOMAIN=example.com\n")
        (services_enabled / ".env.external").write_text("SVC_HOST_NAME=svc\n")

        # Create existing hosts file with comments
        hosts_dir = tmp_path / "etc" / "joyride" / "hosts.d"
        hosts_dir.mkdir(parents=True)
        (hosts_dir / "hosts").write_text(
            "# Manual entries\n"
            "# Do not remove\n"
            "192.168.1.50 manual.example.com\n"
        )

        # Create external config
        external_enabled = tmp_path / "external-enabled"
        external_enabled.mkdir()
        (external_enabled / "service.yml").write_text(
            traefik_yaml("svc", "SVC_HOST_NAME")
        )

        extractor = TraefikHostsExtractor(base_dir=tmp_path, env_vars={})

        result = extractor.sync()

        assert result == 0

        # Verify comments are preserved
        content = (hosts_dir / "hosts").read_text()
        assert "# Manual entries" in content
        assert "# Do not remove" in content
        assert "manual.example.com" in content


class TestSyncEarlyExit:
    """Tests for sync early exit conditions."""

    def test_exits_when_joyride_not_enabled(self, tmp_path, capsys):
        """Should exit with error when joyride is not enabled."""
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        # No joyride.yml

        extractor = TraefikHostsExtractor(base_dir=tmp_path)

        result = extractor.sync()

        assert result == 1

        captured = capsys.readouterr()
        assert "Joyride service is not enabled" in captured.err

    def test_exits_when_hostip_not_set(self, tmp_path, capsys):
        """Should exit with error when HOSTIP is not set."""
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (services_enabled / "joyride.yml").write_text("# enabled")
        (services_enabled / ".env").write_text("HOST_DOMAIN=example.com\n")

        extractor = TraefikHostsExtractor(base_dir=tmp_path, env_vars={})

        result = extractor.sync()

        assert result == 1

        captured = capsys.readouterr()
        assert "HOSTIP not set" in captured.err

    def test_exits_when_host_domain_not_set(self, tmp_path, capsys):
        """Should exit with error when HOST_DOMAIN is not set."""
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (services_enabled / "joyride.yml").write_text("# enabled")
        (services_enabled / ".env").write_text("HOSTIP=192.168.1.10\n")

        extractor = TraefikHostsExtractor(base_dir=tmp_path, env_vars={})

        result = extractor.sync()

        assert result == 1

        captured = capsys.readouterr()
        assert "HOST_DOMAIN not set" in captured.err


class TestFullSync:
    """Integration tests for full sync operation."""

    def test_full_sync_creates_hosts_file(self, tmp_path, capsys):
        """Should create hosts file with extracted entries."""
        # Set up joyride as enabled
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        (services_enabled / "joyride.yml").write_text("# enabled")
        (services_enabled / ".env").write_text(
            "HOSTIP=192.168.1.10\n"
            "HOST_DOMAIN=lab.local\n"
        )
        (services_enabled / ".env.external").write_text(
            "HOMEASSISTANT_HOST_NAME=hass\n"
            "PROXMOX_HOST_NAME=pve\n"
        )

        # Create external configs
        external_enabled = tmp_path / "external-enabled"
        external_enabled.mkdir()
        (external_enabled / "homeassistant.yml").write_text(
            traefik_yaml("hass", "HOMEASSISTANT_HOST_NAME")
        )
        (external_enabled / "proxmox.yml").write_text(
            traefik_yaml("pve", "PROXMOX_HOST_NAME")
        )

        # Create hosts directory (simulating scaffold)
        hosts_dir = tmp_path / "etc" / "joyride" / "hosts.d"
        hosts_dir.mkdir(parents=True)

        extractor = TraefikHostsExtractor(base_dir=tmp_path, env_vars={})

        result = extractor.sync()

        assert result == 0

        # Verify hosts file was created
        hosts_file = hosts_dir / "hosts"
        assert hosts_file.exists()

        content = hosts_file.read_text()
        assert "192.168.1.10 hass.lab.local" in content
        assert "192.168.1.10 pve.lab.local" in content

        # Check output
        captured = capsys.readouterr()
        assert "Added:" in captured.out
        assert "Wrote 2 host entries" in captured.out
