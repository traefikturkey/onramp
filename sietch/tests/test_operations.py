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
    OPERATIONS,
)


@pytest.fixture
def ctx(tmp_path):
    """Create a standard OperationContext for tests."""
    etc_dir = tmp_path / "etc"
    etc_dir.mkdir()
    return OperationContext(
        service="testservice",
        base_dir=tmp_path,
        scaffold_dir=tmp_path / "services-scaffold",
        etc_dir=etc_dir,
        services_enabled=tmp_path / "services-enabled",
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

    def test_true_when_dir_missing(self, ctx):
        condition = Condition({"type": "dir_empty", "path": "data"}, ctx)
        assert condition.evaluate() is True

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
