"""Tests for operations.py - conditions and path resolution."""

import os
import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from operations import (
    OperationContext,
    Condition,
    Operation,
    MkdirOp,
    DeleteOp,
    GenerateRsaKeyOp,
    GenerateRandomOp,
    DownloadOp,
    ChownOp,
    ChmodOp,
    OPERATIONS,
)
from tests.mocks.command import MockCommandExecutor
from ports.command import CommandResult


@pytest.fixture
def mock_exec():
    """Create a mock command executor for tests."""
    return MockCommandExecutor()


@pytest.fixture
def ctx(tmp_path, mock_exec):
    """Create a standard OperationContext for tests."""
    etc_dir = tmp_path / "etc"
    etc_dir.mkdir()
    return OperationContext(
        service="testservice",
        base_dir=tmp_path,
        scaffold_dir=tmp_path / "services-scaffold",
        etc_dir=etc_dir,
        services_enabled=tmp_path / "services-enabled",
        command_executor=mock_exec,
    )


class TestOperationContext:
    """Tests for OperationContext dataclass."""

    def test_resolve_path(self, tmp_path):
        ctx = OperationContext(
            service="plex",
            base_dir=tmp_path,
            scaffold_dir=tmp_path / "services-scaffold",
            etc_dir=tmp_path / "etc",
            services_enabled=tmp_path / "services-enabled",
        )

        result = ctx.resolve_path("config.yml")
        assert result == tmp_path / "etc" / "plex" / "config.yml"

    def test_resolve_nested_path(self, tmp_path):
        ctx = OperationContext(
            service="plex",
            base_dir=tmp_path,
            scaffold_dir=tmp_path / "services-scaffold",
            etc_dir=tmp_path / "etc",
            services_enabled=tmp_path / "services-enabled",
        )

        result = ctx.resolve_path("subdir/nested.conf")
        assert result == tmp_path / "etc" / "plex" / "subdir" / "nested.conf"


class TestConditionFileExists:
    """Tests for Condition type=file_exists."""

    def test_true_when_file_exists(self, ctx):
        # Create the file
        service_dir = ctx.etc_dir / ctx.service
        service_dir.mkdir(parents=True)
        (service_dir / "config.yml").write_text("content")

        condition = Condition({"type": "file_exists", "path": "config.yml"}, ctx)
        assert condition.evaluate() is True

    def test_false_when_file_missing(self, ctx):
        condition = Condition({"type": "file_exists", "path": "config.yml"}, ctx)
        assert condition.evaluate() is False

    def test_false_when_path_is_directory(self, ctx):
        # Create a directory (not file)
        service_dir = ctx.etc_dir / ctx.service
        (service_dir / "config.yml").mkdir(parents=True)

        condition = Condition({"type": "file_exists", "path": "config.yml"}, ctx)
        assert condition.evaluate() is False


class TestConditionFileNotExists:
    """Tests for Condition type=file_not_exists."""

    def test_true_when_file_missing(self, ctx):
        condition = Condition({"type": "file_not_exists", "path": "config.yml"}, ctx)
        assert condition.evaluate() is True

    def test_false_when_file_exists(self, ctx):
        service_dir = ctx.etc_dir / ctx.service
        service_dir.mkdir(parents=True)
        (service_dir / "config.yml").write_text("content")

        condition = Condition({"type": "file_not_exists", "path": "config.yml"}, ctx)
        assert condition.evaluate() is False


class TestConditionDirEmpty:
    """Tests for Condition type=dir_empty."""

    def test_false_when_dir_missing(self, ctx):
        """Non-existent directory should not be treated as empty."""
        condition = Condition({"type": "dir_empty", "path": "data"}, ctx)
        assert condition.evaluate() is False

    def test_true_when_dir_empty(self, ctx):
        service_dir = ctx.etc_dir / ctx.service
        (service_dir / "data").mkdir(parents=True)

        condition = Condition({"type": "dir_empty", "path": "data"}, ctx)
        assert condition.evaluate() is True

    def test_false_when_dir_has_files(self, ctx):
        service_dir = ctx.etc_dir / ctx.service
        data_dir = service_dir / "data"
        data_dir.mkdir(parents=True)
        (data_dir / "file.txt").write_text("content")

        condition = Condition({"type": "dir_empty", "path": "data"}, ctx)
        assert condition.evaluate() is False


class TestConditionDirNotEmpty:
    """Tests for Condition type=dir_not_empty."""

    def test_false_when_dir_missing(self, ctx):
        condition = Condition({"type": "dir_not_empty", "path": "data"}, ctx)
        assert condition.evaluate() is False

    def test_false_when_dir_empty(self, ctx):
        service_dir = ctx.etc_dir / ctx.service
        (service_dir / "data").mkdir(parents=True)

        condition = Condition({"type": "dir_not_empty", "path": "data"}, ctx)
        assert condition.evaluate() is False

    def test_true_when_dir_has_files(self, ctx):
        service_dir = ctx.etc_dir / ctx.service
        data_dir = service_dir / "data"
        data_dir.mkdir(parents=True)
        (data_dir / "file.txt").write_text("content")

        condition = Condition({"type": "dir_not_empty", "path": "data"}, ctx)
        assert condition.evaluate() is True


class TestConditionUnknownType:
    """Tests for unknown condition types."""

    def test_returns_false_for_unknown(self, ctx, capsys):
        condition = Condition({"type": "unknown_type", "path": "data"}, ctx)
        result = condition.evaluate()

        assert result is False
        captured = capsys.readouterr()
        assert "Unknown condition type" in captured.out


class TestOperationShouldExecute:
    """Tests for Operation.should_execute() with conditions."""

    def test_executes_without_condition(self, ctx):
        config = {"type": "mkdir", "path": "data"}
        op = MkdirOp(config, ctx)

        assert op.should_execute() is True

    def test_skips_when_condition_false(self, ctx):
        # Condition: file must exist (but doesn't)
        service_dir = ctx.etc_dir / ctx.service
        service_dir.mkdir(parents=True)
        (service_dir / "marker.txt").write_text("exists")

        config = {
            "type": "mkdir",
            "path": "data",
            "condition": {"type": "file_not_exists", "path": "marker.txt"},
        }
        op = MkdirOp(config, ctx)

        assert op.should_execute() is False

    def test_executes_when_condition_true(self, ctx):
        config = {
            "type": "mkdir",
            "path": "data",
            "condition": {"type": "file_not_exists", "path": "marker.txt"},
        }
        op = MkdirOp(config, ctx)

        assert op.should_execute() is True


class TestOperationExpandEnv:
    """Tests for Operation.expand_env()."""

    def test_expands_env_vars(self, ctx, monkeypatch):
        monkeypatch.setenv("TEST_USER", "myuser")

        config = {"type": "mkdir", "path": "data"}
        op = MkdirOp(config, ctx)

        result = op.expand_env("$TEST_USER")
        assert result == "myuser"

    def test_expands_braced_env_vars(self, ctx, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "value123")

        config = {"type": "mkdir", "path": "data"}
        op = MkdirOp(config, ctx)

        result = op.expand_env("${TEST_VAR}")
        assert result == "value123"

    def test_leaves_unset_vars(self, ctx, monkeypatch):
        monkeypatch.delenv("UNSET_VAR", raising=False)

        config = {"type": "mkdir", "path": "data"}
        op = MkdirOp(config, ctx)

        result = op.expand_env("$UNSET_VAR")
        # Unset vars are left as-is or empty depending on OS
        assert result in ("$UNSET_VAR", "")


class TestMkdirOp:
    """Tests for MkdirOp operation."""

    def test_creates_directory(self, ctx):
        config = {"type": "mkdir", "path": "data"}
        op = MkdirOp(config, ctx)

        result = op.execute()

        assert result is True
        expected = ctx.etc_dir / ctx.service / "data"
        assert expected.exists()
        assert expected.is_dir()

    def test_creates_nested_directory(self, ctx):
        config = {"type": "mkdir", "path": "data/subdir/nested"}
        op = MkdirOp(config, ctx)

        result = op.execute()

        assert result is True
        expected = ctx.etc_dir / ctx.service / "data" / "subdir" / "nested"
        assert expected.exists()

    @pytest.mark.skipif(sys.platform == "win32", reason="chmod not supported on Windows")
    def test_applies_mode(self, ctx):
        config = {"type": "mkdir", "path": "data", "mode": "0700"}
        op = MkdirOp(config, ctx)

        result = op.execute()

        assert result is True
        expected = ctx.etc_dir / ctx.service / "data"
        # Check mode (masking to get permission bits)
        mode = expected.stat().st_mode & 0o777
        assert mode == 0o700


class TestDeleteOp:
    """Tests for DeleteOp operation."""

    def test_deletes_file(self, ctx):
        service_dir = ctx.etc_dir / ctx.service
        service_dir.mkdir(parents=True)
        target = service_dir / "delete_me.txt"
        target.write_text("content")

        config = {"type": "delete", "path": "delete_me.txt"}
        op = DeleteOp(config, ctx)

        result = op.execute()

        assert result is True
        assert not target.exists()

    def test_deletes_directory(self, ctx):
        service_dir = ctx.etc_dir / ctx.service
        target = service_dir / "delete_dir"
        target.mkdir(parents=True)
        (target / "file.txt").write_text("content")

        config = {"type": "delete", "path": "delete_dir"}
        op = DeleteOp(config, ctx)

        result = op.execute()

        assert result is True
        assert not target.exists()

    def test_succeeds_when_missing(self, ctx):
        config = {"type": "delete", "path": "nonexistent"}
        op = DeleteOp(config, ctx)

        result = op.execute()

        assert result is True  # Missing is not an error


class TestOperationsRegistry:
    """Tests for OPERATIONS registry."""

    def test_contains_expected_operations(self):
        expected = ["mkdir", "generate_rsa_key", "generate_random", "download", "delete", "chown", "chmod"]
        for op_type in expected:
            assert op_type in OPERATIONS

    def test_operations_are_classes(self):
        for op_type, op_class in OPERATIONS.items():
            assert issubclass(op_class, Operation)


class TestGenerateRsaKeyOp:
    """Tests for GenerateRsaKeyOp with mocked executor."""

    @pytest.mark.skipif(sys.platform == "win32", reason="chmod not supported on Windows")
    def test_generates_private_key(self, ctx, mock_exec, capsys):
        """Should call openssl genpkey and write output."""
        mock_exec.set_response("openssl", CommandResult(0, "---PRIVATE KEY---", ""))

        # Create service directory
        service_dir = ctx.etc_dir / ctx.service
        service_dir.mkdir(parents=True, exist_ok=True)

        config = {"type": "generate_rsa_key", "output": "key.pem", "bits": 2048}
        op = GenerateRsaKeyOp(config, ctx)

        result = op.execute()

        assert result is True
        mock_exec.assert_called_with_command("openssl")
        captured = capsys.readouterr()
        assert "Generated private key" in captured.out

    def test_generates_public_key_when_requested(self, ctx, mock_exec, capsys):
        """Should extract public key when public_key is specified."""
        mock_exec.set_response("openssl", CommandResult(0, "---KEY DATA---", ""))

        config = {
            "type": "generate_rsa_key",
            "output": "private.pem",
            "public_key": "public.pem",
        }
        op = GenerateRsaKeyOp(config, ctx)

        result = op.execute()

        assert result is True
        # Should have called openssl twice
        openssl_calls = mock_exec.get_calls_for("openssl")
        assert len(openssl_calls) == 2

    def test_skips_if_exists(self, ctx, mock_exec, capsys):
        """Should skip generation if key already exists."""
        # Create the key file
        service_dir = ctx.etc_dir / ctx.service
        service_dir.mkdir(parents=True)
        (service_dir / "key.pem").write_text("existing key")

        config = {"type": "generate_rsa_key", "output": "key.pem", "skip_if_exists": True}
        op = GenerateRsaKeyOp(config, ctx)

        result = op.execute()

        assert result is True
        # Should not have called openssl
        assert len(mock_exec.calls) == 0
        captured = capsys.readouterr()
        assert "Skipped" in captured.out

    def test_handles_openssl_error(self, ctx, mock_exec, capsys):
        """Should return False on OpenSSL failure."""
        mock_exec.set_response("openssl", CommandResult(1, "", "OpenSSL error"))

        config = {"type": "generate_rsa_key", "output": "key.pem"}
        op = GenerateRsaKeyOp(config, ctx)

        result = op.execute()

        assert result is False


class TestGenerateRandomOp:
    """Tests for GenerateRandomOp with mocked executor."""

    def test_generates_random_data(self, ctx, mock_exec, capsys):
        """Should call openssl rand and write output."""
        mock_exec.set_response("openssl", CommandResult(0, "random-base64-data", ""))

        config = {"type": "generate_random", "output": "secret.txt", "bytes": 32}
        op = GenerateRandomOp(config, ctx)

        result = op.execute()

        assert result is True
        mock_exec.assert_called_with_command("openssl")
        captured = capsys.readouterr()
        assert "Generated random data" in captured.out

    def test_uses_encoding_parameter(self, ctx, mock_exec):
        """Should pass encoding to openssl rand."""
        mock_exec.set_response("openssl", CommandResult(0, "hexdata", ""))

        config = {"type": "generate_random", "output": "secret.txt", "encoding": "hex"}
        op = GenerateRandomOp(config, ctx)

        op.execute()

        # Check that -hex was passed
        openssl_calls = mock_exec.get_calls_for("openssl")
        cmd_str = " ".join(openssl_calls[0])
        assert "-hex" in cmd_str

    def test_skips_if_exists(self, ctx, mock_exec, capsys):
        """Should skip if file already exists."""
        service_dir = ctx.etc_dir / ctx.service
        service_dir.mkdir(parents=True)
        (service_dir / "secret.txt").write_text("existing")

        config = {"type": "generate_random", "output": "secret.txt", "skip_if_exists": True}
        op = GenerateRandomOp(config, ctx)

        result = op.execute()

        assert result is True
        assert len(mock_exec.calls) == 0


class TestDownloadOp:
    """Tests for DownloadOp with mocked executor."""

    def test_downloads_file(self, ctx, mock_exec, capsys):
        """Should call wget and report success."""
        mock_exec.set_response("wget", CommandResult(0, "", ""))

        config = {
            "type": "download",
            "url": "https://example.com/file.txt",
            "output": "downloaded.txt",
        }
        op = DownloadOp(config, ctx)

        result = op.execute()

        assert result is True
        mock_exec.assert_called_with_command("wget")
        captured = capsys.readouterr()
        assert "Downloaded" in captured.out

    def test_skips_if_exists(self, ctx, mock_exec, capsys):
        """Should skip download if file exists."""
        service_dir = ctx.etc_dir / ctx.service
        service_dir.mkdir(parents=True)
        (service_dir / "downloaded.txt").write_text("existing")

        config = {
            "type": "download",
            "url": "https://example.com/file.txt",
            "output": "downloaded.txt",
            "skip_if_exists": True,
        }
        op = DownloadOp(config, ctx)

        result = op.execute()

        assert result is True
        assert len(mock_exec.calls) == 0

    def test_handles_download_error(self, ctx, mock_exec, capsys):
        """Should return False on download failure."""
        mock_exec.set_response("wget", CommandResult(1, "", "Connection refused"))

        config = {
            "type": "download",
            "url": "https://example.com/file.txt",
            "output": "downloaded.txt",
        }
        op = DownloadOp(config, ctx)

        result = op.execute()

        assert result is False


class TestChownOp:
    """Tests for ChownOp with mocked executor."""

    def test_changes_ownership(self, ctx, mock_exec, capsys):
        """Should call chown command."""
        mock_exec.set_response("chown", CommandResult(0, "", ""))

        service_dir = ctx.etc_dir / ctx.service
        service_dir.mkdir(parents=True)
        (service_dir / "file.txt").write_text("content")

        config = {"type": "chown", "path": "file.txt", "user": "myuser", "group": "mygroup"}
        op = ChownOp(config, ctx)

        result = op.execute()

        assert result is True
        mock_exec.assert_called_with_command("chown")
        captured = capsys.readouterr()
        assert "Changed ownership" in captured.out

    def test_recursive_chown(self, ctx, mock_exec):
        """Should pass -R flag when recursive=True."""
        mock_exec.set_response("chown", CommandResult(0, "", ""))

        service_dir = ctx.etc_dir / ctx.service
        (service_dir / "data").mkdir(parents=True)

        config = {"type": "chown", "path": "data", "user": "myuser", "recursive": True}
        op = ChownOp(config, ctx)

        op.execute()

        chown_calls = mock_exec.get_calls_for("chown")
        assert "-R" in chown_calls[0]

    def test_skips_if_path_missing(self, ctx, mock_exec, capsys):
        """Should skip if path doesn't exist."""
        config = {"type": "chown", "path": "nonexistent", "user": "myuser"}
        op = ChownOp(config, ctx)

        result = op.execute()

        assert result is True
        assert len(mock_exec.calls) == 0
        captured = capsys.readouterr()
        assert "Skipped" in captured.out


class TestChmodOp:
    """Tests for ChmodOp with mocked executor."""

    def test_changes_permissions(self, ctx, mock_exec, capsys):
        """Should call chmod command."""
        mock_exec.set_response("chmod", CommandResult(0, "", ""))

        service_dir = ctx.etc_dir / ctx.service
        service_dir.mkdir(parents=True)
        (service_dir / "file.txt").write_text("content")

        config = {"type": "chmod", "path": "file.txt", "mode": "0644"}
        op = ChmodOp(config, ctx)

        result = op.execute()

        assert result is True
        mock_exec.assert_called_with_command("chmod")
        captured = capsys.readouterr()
        assert "Changed permissions" in captured.out

    def test_recursive_chmod(self, ctx, mock_exec):
        """Should pass -R flag when recursive=True."""
        mock_exec.set_response("chmod", CommandResult(0, "", ""))

        service_dir = ctx.etc_dir / ctx.service
        (service_dir / "data").mkdir(parents=True)

        config = {"type": "chmod", "path": "data", "mode": "0755", "recursive": True}
        op = ChmodOp(config, ctx)

        op.execute()

        chmod_calls = mock_exec.get_calls_for("chmod")
        assert "-R" in chmod_calls[0]

    def test_skips_if_path_missing(self, ctx, mock_exec, capsys):
        """Should skip if path doesn't exist."""
        config = {"type": "chmod", "path": "nonexistent", "mode": "0644"}
        op = ChmodOp(config, ctx)

        result = op.execute()

        assert result is True
        assert len(mock_exec.calls) == 0

    def test_handles_chmod_error(self, ctx, mock_exec, capsys):
        """Should return False on chmod failure."""
        mock_exec.set_response("chmod", CommandResult(1, "", "Operation not permitted"))

        service_dir = ctx.etc_dir / ctx.service
        service_dir.mkdir(parents=True)
        (service_dir / "file.txt").write_text("content")

        config = {"type": "chmod", "path": "file.txt", "mode": "0644"}
        op = ChmodOp(config, ctx)

        result = op.execute()

        assert result is False


class TestOperationContextExecutor:
    """Tests for OperationContext command_executor injection."""

    def test_uses_injected_executor(self, tmp_path, mock_exec):
        """Should use injected command executor."""
        ctx = OperationContext(
            service="test",
            base_dir=tmp_path,
            scaffold_dir=tmp_path / "scaffold",
            etc_dir=tmp_path / "etc",
            services_enabled=tmp_path / "services-enabled",
            command_executor=mock_exec,
        )

        assert ctx.command_executor is mock_exec

    def test_creates_default_executor(self, tmp_path):
        """Should create default executor when none provided."""
        ctx = OperationContext(
            service="test",
            base_dir=tmp_path,
            scaffold_dir=tmp_path / "scaffold",
            etc_dir=tmp_path / "etc",
            services_enabled=tmp_path / "services-enabled",
        )

        assert ctx.command_executor is not None
