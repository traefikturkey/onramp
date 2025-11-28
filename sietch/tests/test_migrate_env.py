"""Tests for migrate-env.py pure logic functions."""

import importlib.util
import sys
from pathlib import Path

import pytest

# Load migrate-env.py (has hyphen in name, can't use normal import)
_script_path = Path(__file__).parent.parent / "scripts" / "migrate-env.py"
_spec = importlib.util.spec_from_file_location("migrate_env", _script_path)
migrate_env = importlib.util.module_from_spec(_spec)
sys.modules["migrate_env"] = migrate_env
_spec.loader.exec_module(migrate_env)

EnvMigrator = migrate_env.EnvMigrator
GLOBAL_VARS = migrate_env.GLOBAL_VARS
NFS_PREFIXES = migrate_env.NFS_PREFIXES
EXTERNAL_PREFIXES = migrate_env.EXTERNAL_PREFIXES
EXTERNAL_SPECIFIC_VARS = migrate_env.EXTERNAL_SPECIFIC_VARS
SERVICE_PREFIXES = migrate_env.SERVICE_PREFIXES


class TestIsNfsVar:
    """Tests for _is_nfs_var() - NFS/SAMBA variable detection."""

    def test_nfs_prefix_matches(self):
        migrator = EnvMigrator.__new__(EnvMigrator)
        assert migrator._is_nfs_var("NFS_SERVER") is True
        assert migrator._is_nfs_var("NFS_BACKUP_PATH") is True

    def test_samba_prefix_matches(self):
        migrator = EnvMigrator.__new__(EnvMigrator)
        assert migrator._is_nfs_var("SAMBA_HOST") is True
        assert migrator._is_nfs_var("SAMBA_SHARE") is True

    def test_non_nfs_vars(self):
        migrator = EnvMigrator.__new__(EnvMigrator)
        assert migrator._is_nfs_var("PLEX_TOKEN") is False
        assert migrator._is_nfs_var("HOST_NAME") is False
        assert migrator._is_nfs_var("PROXMOX_URL") is False


class TestIsExternalVar:
    """Tests for _is_external_var() - external service variable detection."""

    def test_external_prefixes_match(self):
        migrator = EnvMigrator.__new__(EnvMigrator)
        assert migrator._is_external_var("HOMEASSISTANT_URL") is True
        assert migrator._is_external_var("PROXMOX_HOST") is True
        assert migrator._is_external_var("TRUENAS_API_KEY") is True
        assert migrator._is_external_var("OPNSENSE_HOST") is True

    def test_external_specific_vars_match(self):
        migrator = EnvMigrator.__new__(EnvMigrator)
        # These look like pihole service vars but are external proxying
        assert migrator._is_external_var("PIHOLE_ADDRESS") is True
        assert migrator._is_external_var("PIHOLE_HOST_NAME") is True

    def test_pihole_service_vars_not_external(self):
        migrator = EnvMigrator.__new__(EnvMigrator)
        # PIHOLE_WEBPASSWORD is for the container, not external
        assert migrator._is_external_var("PIHOLE_WEBPASSWORD") is False

    def test_non_external_vars(self):
        migrator = EnvMigrator.__new__(EnvMigrator)
        assert migrator._is_external_var("PLEX_TOKEN") is False
        assert migrator._is_external_var("HOST_NAME") is False
        assert migrator._is_external_var("NFS_SERVER") is False


class TestGetServiceForVar:
    """Tests for get_service_for_var() - service prefix matching."""

    def test_global_vars_return_none(self, tmp_path):
        migrator = EnvMigrator(str(tmp_path))
        (tmp_path / "services-enabled").mkdir()

        assert migrator.get_service_for_var("HOST_NAME") is None
        assert migrator.get_service_for_var("TZ") is None
        assert migrator.get_service_for_var("PUID") is None
        assert migrator.get_service_for_var("CF_DNS_API_TOKEN") is None

    def test_service_prefix_matching(self, tmp_path):
        migrator = EnvMigrator(str(tmp_path))
        (tmp_path / "services-enabled").mkdir()

        assert migrator.get_service_for_var("PLEX_TOKEN") == "plex"
        assert migrator.get_service_for_var("RADARR_API_KEY") == "radarr"
        assert migrator.get_service_for_var("SONARR_API_KEY") == "sonarr"
        assert migrator.get_service_for_var("GRAFANA_ADMIN_PASSWORD") == "grafana"

    def test_service_prefix_exact_match(self, tmp_path):
        migrator = EnvMigrator(str(tmp_path))
        (tmp_path / "services-enabled").mkdir()

        # Some vars might just be the prefix itself
        assert migrator.get_service_for_var("PLEX") == "plex"

    def test_alias_prefixes(self, tmp_path):
        migrator = EnvMigrator(str(tmp_path))
        (tmp_path / "services-enabled").mkdir()

        # PLEXPY -> tautulli (alias)
        assert migrator.get_service_for_var("PLEXPY_API_KEY") == "tautulli"

    def test_enabled_service_matching(self, tmp_path):
        """Test that enabled services are detected even without PREFIX mapping."""
        migrator = EnvMigrator(str(tmp_path))
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()

        # Create a service that isn't in SERVICE_PREFIXES
        (services_enabled / "custom-app.yml").write_text("# placeholder")

        # CUSTOM_APP_VAR should match custom-app service
        result = migrator.get_service_for_var("CUSTOM_APP_VAR")
        assert result == "custom-app"

    def test_unknown_var_returns_none(self, tmp_path):
        migrator = EnvMigrator(str(tmp_path))
        (tmp_path / "services-enabled").mkdir()

        assert migrator.get_service_for_var("UNKNOWN_VAR") is None
        assert migrator.get_service_for_var("RANDOM_SETTING") is None


class TestParseEnvFile:
    """Tests for parse_env_file() - env file parsing with comment preservation."""

    def test_simple_variables(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("HOST_NAME=myhost\nTZ=America/Chicago\n")

        migrator = EnvMigrator(str(tmp_path))
        result = migrator.parse_env_file(env_file)

        assert "HOST_NAME" in result
        assert result["HOST_NAME"][0] == "myhost"
        assert "TZ" in result
        assert result["TZ"][0] == "America/Chicago"

    def test_comment_preservation(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("# This is a comment\n# Another comment\nHOST_NAME=myhost\n")

        migrator = EnvMigrator(str(tmp_path))
        result = migrator.parse_env_file(env_file)

        assert "HOST_NAME" in result
        value, comments = result["HOST_NAME"]
        assert value == "myhost"
        assert len(comments) == 2
        assert comments[0] == "# This is a comment"
        assert comments[1] == "# Another comment"

    def test_empty_lines_preserved(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("\n# Section header\n\nHOST_NAME=myhost\n")

        migrator = EnvMigrator(str(tmp_path))
        result = migrator.parse_env_file(env_file)

        value, comments = result["HOST_NAME"]
        # Empty lines are preserved as comments
        assert "" in comments
        assert "# Section header" in comments

    def test_values_with_equals(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("DATABASE_URL=postgres://user:pass@host:5432/db?sslmode=require\n")

        migrator = EnvMigrator(str(tmp_path))
        result = migrator.parse_env_file(env_file)

        assert result["DATABASE_URL"][0] == "postgres://user:pass@host:5432/db?sslmode=require"

    def test_empty_values(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("EMPTY_VAR=\nNON_EMPTY=value\n")

        migrator = EnvMigrator(str(tmp_path))
        result = migrator.parse_env_file(env_file)

        assert result["EMPTY_VAR"][0] == ""
        assert result["NON_EMPTY"][0] == "value"

    def test_quoted_values_preserved(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text('MESSAGE="Hello World"\nSINGLE=\'Single Quoted\'\n')

        migrator = EnvMigrator(str(tmp_path))
        result = migrator.parse_env_file(env_file)

        # Quotes are preserved as-is
        assert result["MESSAGE"][0] == '"Hello World"'
        assert result["SINGLE"][0] == "'Single Quoted'"


class TestGlobalVarsSet:
    """Tests for GLOBAL_VARS constant - verify expected globals are defined."""

    def test_core_globals_present(self):
        assert "HOST_NAME" in GLOBAL_VARS
        assert "HOST_DOMAIN" in GLOBAL_VARS
        assert "TZ" in GLOBAL_VARS
        assert "PUID" in GLOBAL_VARS
        assert "PGID" in GLOBAL_VARS

    def test_cloudflare_globals_present(self):
        assert "CF_API_EMAIL" in GLOBAL_VARS
        assert "CF_DNS_API_TOKEN" in GLOBAL_VARS

    def test_traefik_globals_present(self):
        assert "TRAEFIK_LOG_LEVEL" in GLOBAL_VARS
        assert "TRAEFIK_DASHBOARD_ENABLE" in GLOBAL_VARS


class TestServicePrefixes:
    """Tests for SERVICE_PREFIXES constant."""

    def test_common_services_mapped(self):
        assert SERVICE_PREFIXES["PLEX"] == "plex"
        assert SERVICE_PREFIXES["RADARR"] == "radarr"
        assert SERVICE_PREFIXES["SONARR"] == "sonarr"
        assert SERVICE_PREFIXES["GRAFANA"] == "grafana"

    def test_hyphenated_services(self):
        # Services with hyphens use underscores in env vars
        assert SERVICE_PREFIXES["CLOUDFLARE_DDNS"] == "cloudflare-ddns"
        assert SERVICE_PREFIXES["CODE_SERVER"] == "code-server"
        assert SERVICE_PREFIXES["UPTIME_KUMA"] == "uptime-kuma"

    def test_aliases(self):
        # PLEXPY is alias for tautulli
        assert SERVICE_PREFIXES["PLEXPY"] == "tautulli"
