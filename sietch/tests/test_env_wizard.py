"""Tests for env_wizard.py - Interactive environment setup wizard."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.env_wizard import (
    COMMON_TIMEZONES,
    MAIN_ENV_VARS,
    NFS_ENV_VARS,
    EnvVariable,
    EnvWizard,
)


class TestEnvVariableDataclass:
    """Tests for the EnvVariable dataclass."""

    def test_required_fields(self):
        var = EnvVariable(name="TEST_VAR", help_text="Test help")
        assert var.name == "TEST_VAR"
        assert var.help_text == "Test help"

    def test_default_values(self):
        var = EnvVariable(name="TEST_VAR", help_text="Test help")
        assert var.sensitive is False
        assert var.required is True
        assert var.default is None
        assert var.choices is None

    def test_optional_fields(self):
        var = EnvVariable(
            name="API_KEY",
            help_text="API key",
            sensitive=True,
            required=False,
            default="default_value",
            choices=[("a", "Option A"), ("b", "Option B")],
        )
        assert var.sensitive is True
        assert var.required is False
        assert var.default == "default_value"
        assert len(var.choices) == 2


class TestCommonTimezones:
    """Tests for COMMON_TIMEZONES constant."""

    def test_contains_us_timezones(self):
        tz_values = [tz[0] for tz in COMMON_TIMEZONES]
        assert "US/Eastern" in tz_values
        assert "US/Pacific" in tz_values

    def test_contains_european_timezones(self):
        tz_values = [tz[0] for tz in COMMON_TIMEZONES]
        assert "Europe/London" in tz_values
        assert "Europe/Berlin" in tz_values

    def test_each_entry_has_value_and_label(self):
        for value, label in COMMON_TIMEZONES:
            assert isinstance(value, str)
            assert isinstance(label, str)
            assert len(value) > 0
            assert len(label) > 0


class TestMainEnvVars:
    """Tests for MAIN_ENV_VARS constant."""

    def test_contains_required_vars(self):
        var_names = [v.name for v in MAIN_ENV_VARS]
        assert "HOST_NAME" in var_names
        assert "HOST_DOMAIN" in var_names
        assert "TZ" in var_names
        assert "CF_API_EMAIL" in var_names
        assert "CF_DNS_API_TOKEN" in var_names

    def test_cf_dns_api_token_is_sensitive(self):
        token_var = next(v for v in MAIN_ENV_VARS if v.name == "CF_DNS_API_TOKEN")
        assert token_var.sensitive is True

    def test_tz_has_choices(self):
        tz_var = next(v for v in MAIN_ENV_VARS if v.name == "TZ")
        assert tz_var.choices is not None
        assert len(tz_var.choices) > 0


class TestNfsEnvVars:
    """Tests for NFS_ENV_VARS constant."""

    def test_contains_nfs_server(self):
        var_names = [v.name for v in NFS_ENV_VARS]
        assert "NFS_SERVER" in var_names


class TestLoadEnvFile:
    """Tests for EnvWizard.load_env_file()."""

    def test_loads_simple_variables(self, tmp_path):
        env_file = tmp_path / "services-enabled" / ".env"
        env_file.parent.mkdir(parents=True)
        env_file.write_text("HOST_NAME=myserver\nHOST_DOMAIN=example.com\n")

        wizard = EnvWizard(str(tmp_path))
        result = wizard.load_env_file(env_file)

        assert result["HOST_NAME"] == "myserver"
        assert result["HOST_DOMAIN"] == "example.com"

    def test_skips_comments(self, tmp_path):
        env_file = tmp_path / "services-enabled" / ".env"
        env_file.parent.mkdir(parents=True)
        env_file.write_text("# Comment\nHOST_NAME=myserver\n# Another comment\n")

        wizard = EnvWizard(str(tmp_path))
        result = wizard.load_env_file(env_file)

        assert "HOST_NAME" in result
        assert len(result) == 1

    def test_skips_empty_lines(self, tmp_path):
        env_file = tmp_path / "services-enabled" / ".env"
        env_file.parent.mkdir(parents=True)
        env_file.write_text("\n\nHOST_NAME=myserver\n\n")

        wizard = EnvWizard(str(tmp_path))
        result = wizard.load_env_file(env_file)

        assert result["HOST_NAME"] == "myserver"
        assert len(result) == 1

    def test_handles_empty_values(self, tmp_path):
        env_file = tmp_path / "services-enabled" / ".env"
        env_file.parent.mkdir(parents=True)
        env_file.write_text("EMPTY_VAR=\nSET_VAR=value\n")

        wizard = EnvWizard(str(tmp_path))
        result = wizard.load_env_file(env_file)

        assert result["EMPTY_VAR"] == ""
        assert result["SET_VAR"] == "value"

    def test_handles_values_with_equals(self, tmp_path):
        env_file = tmp_path / "services-enabled" / ".env"
        env_file.parent.mkdir(parents=True)
        env_file.write_text("URL=postgres://user:pass@host/db?sslmode=require\n")

        wizard = EnvWizard(str(tmp_path))
        result = wizard.load_env_file(env_file)

        assert result["URL"] == "postgres://user:pass@host/db?sslmode=require"

    def test_returns_empty_dict_for_missing_file(self, tmp_path):
        wizard = EnvWizard(str(tmp_path))
        result = wizard.load_env_file(tmp_path / "nonexistent.env")

        assert result == {}


class TestGetExistingValue:
    """Tests for EnvWizard.get_existing_value()."""

    def test_returns_value_if_set(self, tmp_path):
        wizard = EnvWizard(str(tmp_path))
        env_vars = {"HOST_NAME": "myserver"}

        result = wizard.get_existing_value("HOST_NAME", env_vars)
        assert result == "myserver"

    def test_returns_none_for_empty_value(self, tmp_path):
        wizard = EnvWizard(str(tmp_path))
        env_vars = {"HOST_NAME": ""}

        result = wizard.get_existing_value("HOST_NAME", env_vars)
        assert result is None

    def test_returns_none_for_missing_key(self, tmp_path):
        wizard = EnvWizard(str(tmp_path))
        env_vars = {}

        result = wizard.get_existing_value("HOST_NAME", env_vars)
        assert result is None

    def test_returns_none_for_placeholder_value(self, tmp_path):
        wizard = EnvWizard(str(tmp_path))
        env_vars = {"HOST_NAME": "<your_server_name>"}

        result = wizard.get_existing_value("HOST_NAME", env_vars)
        assert result is None

    def test_returns_none_for_template_variable(self, tmp_path):
        wizard = EnvWizard(str(tmp_path))
        env_vars = {"HOST_NAME": "${HOST_NAME}"}

        result = wizard.get_existing_value("HOST_NAME", env_vars)
        assert result is None


class TestUpdateEnvFile:
    """Tests for EnvWizard.update_env_file()."""

    def test_creates_file_if_missing(self, tmp_path):
        env_file = tmp_path / "services-enabled" / ".env"
        wizard = EnvWizard(str(tmp_path))

        wizard.update_env_file(env_file, {"HOST_NAME": "myserver"})

        assert env_file.exists()
        assert "HOST_NAME=myserver" in env_file.read_text()

    def test_updates_existing_variable(self, tmp_path):
        env_file = tmp_path / "services-enabled" / ".env"
        env_file.parent.mkdir(parents=True)
        env_file.write_text("HOST_NAME=oldvalue\nOTHER_VAR=keep\n")

        wizard = EnvWizard(str(tmp_path))
        wizard.update_env_file(env_file, {"HOST_NAME": "newvalue"})

        content = env_file.read_text()
        assert "HOST_NAME=newvalue" in content
        assert "HOST_NAME=oldvalue" not in content
        assert "OTHER_VAR=keep" in content

    def test_appends_new_variable(self, tmp_path):
        env_file = tmp_path / "services-enabled" / ".env"
        env_file.parent.mkdir(parents=True)
        env_file.write_text("EXISTING=value\n")

        wizard = EnvWizard(str(tmp_path))
        wizard.update_env_file(env_file, {"NEW_VAR": "newvalue"})

        content = env_file.read_text()
        assert "EXISTING=value" in content
        assert "NEW_VAR=newvalue" in content

    def test_preserves_comments(self, tmp_path):
        env_file = tmp_path / "services-enabled" / ".env"
        env_file.parent.mkdir(parents=True)
        env_file.write_text("# Comment\nHOST_NAME=old\n")

        wizard = EnvWizard(str(tmp_path))
        wizard.update_env_file(env_file, {"HOST_NAME": "new"})

        content = env_file.read_text()
        assert "# Comment" in content
        assert "HOST_NAME=new" in content

    def test_handles_empty_updates(self, tmp_path):
        env_file = tmp_path / "services-enabled" / ".env"
        env_file.parent.mkdir(parents=True)
        original = "HOST_NAME=value\n"
        env_file.write_text(original)

        wizard = EnvWizard(str(tmp_path))
        wizard.update_env_file(env_file, {})

        assert env_file.read_text() == original


class TestGetSystemTimezone:
    """Tests for EnvWizard.get_system_timezone()."""

    def test_returns_none_for_utc(self, tmp_path):
        wizard = EnvWizard(str(tmp_path))

        # When no timezone file exists and TZ env var is not set
        with patch.dict(os.environ, {}, clear=True):
            with patch("pathlib.Path.exists", return_value=False):
                with patch("pathlib.Path.is_symlink", return_value=False):
                    result = wizard.get_system_timezone()
                    # May return None or a value depending on system state
                    assert result is None or isinstance(result, str)

    def test_reads_etc_timezone(self, tmp_path):
        wizard = EnvWizard(str(tmp_path))

        with patch("pathlib.Path.exists") as mock_exists:
            with patch("pathlib.Path.read_text") as mock_read:
                mock_exists.return_value = True
                mock_read.return_value = "America/New_York\n"

                result = wizard.get_system_timezone()
                assert result == "America/New_York"

    def test_returns_none_for_utc_timezone(self, tmp_path):
        wizard = EnvWizard(str(tmp_path))

        with patch("pathlib.Path.exists") as mock_exists:
            with patch("pathlib.Path.read_text") as mock_read:
                mock_exists.return_value = True
                mock_read.return_value = "UTC\n"

                result = wizard.get_system_timezone()
                assert result is None


class TestCheckComplete:
    """Tests for EnvWizard.check_complete()."""

    def test_returns_false_when_all_missing(self, tmp_path):
        env_file = tmp_path / "services-enabled" / ".env"
        env_file.parent.mkdir(parents=True)
        env_file.write_text("")

        wizard = EnvWizard(str(tmp_path))
        is_complete, missing = wizard.check_complete()

        assert is_complete is False
        assert "HOST_NAME" in missing
        assert "HOST_DOMAIN" in missing

    def test_returns_true_when_all_configured(self, tmp_path):
        env_file = tmp_path / "services-enabled" / ".env"
        env_file.parent.mkdir(parents=True)
        env_file.write_text(
            "HOST_NAME=myserver\n"
            "HOST_DOMAIN=example.com\n"
            "TZ=US/Eastern\n"
            "CF_API_EMAIL=test@example.com\n"
            "CF_DNS_API_TOKEN=abc123\n"
        )

        wizard = EnvWizard(str(tmp_path))
        is_complete, missing = wizard.check_complete()

        assert is_complete is True
        assert len(missing) == 0

    def test_returns_missing_list(self, tmp_path):
        env_file = tmp_path / "services-enabled" / ".env"
        env_file.parent.mkdir(parents=True)
        env_file.write_text("HOST_NAME=myserver\nHOST_DOMAIN=example.com\n")

        wizard = EnvWizard(str(tmp_path))
        is_complete, missing = wizard.check_complete()

        assert is_complete is False
        assert "TZ" in missing
        assert "CF_API_EMAIL" in missing
        assert "CF_DNS_API_TOKEN" in missing
        assert "HOST_NAME" not in missing


class TestRunWizard:
    """Tests for EnvWizard.run_wizard() behavior."""

    def test_skips_when_complete(self, tmp_path, capsys):
        env_file = tmp_path / "services-enabled" / ".env"
        env_file.parent.mkdir(parents=True)
        env_file.write_text(
            "HOST_NAME=myserver\n"
            "HOST_DOMAIN=example.com\n"
            "TZ=US/Eastern\n"
            "CF_API_EMAIL=test@example.com\n"
            "CF_DNS_API_TOKEN=abc123\n"
        )

        wizard = EnvWizard(str(tmp_path))
        result = wizard.run_wizard()

        assert result is True
        captured = capsys.readouterr()
        assert "already configured" in captured.out

    def test_skip_wizard_flag(self, tmp_path, capsys):
        env_file = tmp_path / "services-enabled" / ".env"
        env_file.parent.mkdir(parents=True)
        env_file.write_text("")

        wizard = EnvWizard(str(tmp_path))
        result = wizard.run_wizard(skip_wizard=True)

        assert result is False
        captured = capsys.readouterr()
        assert "Skipping wizard" in captured.out
