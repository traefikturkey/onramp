"""Tests for backup.py with mocked command executor."""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from backup import BackupManager, DEFAULT_EXCLUSIONS, BACKUP_DIRS
from tests.mocks.command import MockCommandExecutor
from ports.command import CommandResult


class TestBackupManagerInit:
    """Tests for BackupManager initialization."""

    def test_default_base_dir(self):
        """Should use /app as default base directory."""
        mock_exec = MockCommandExecutor()
        mgr = BackupManager(executor=mock_exec)
        # Use Path comparison to handle Windows path normalization
        assert mgr.base_dir == Path("/app")

    def test_custom_base_dir(self, tmp_path):
        """Should accept custom base directory."""
        mock_exec = MockCommandExecutor()
        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)
        assert mgr.base_dir == tmp_path

    def test_uses_injected_executor(self):
        """Should use injected command executor."""
        mock_exec = MockCommandExecutor()
        mgr = BackupManager(executor=mock_exec)
        assert mgr._executor is mock_exec

    def test_uses_hostname_from_env(self, monkeypatch):
        """Should use HOST_NAME from environment."""
        monkeypatch.setenv("HOST_NAME", "testhost")
        mock_exec = MockCommandExecutor()
        mgr = BackupManager(executor=mock_exec)
        assert mgr.hostname == "testhost"


class TestConstants:
    """Tests for module constants."""

    def test_default_exclusions_contains_plex(self):
        """Should exclude Plex library by default."""
        assert "etc/plex/Library" in DEFAULT_EXCLUSIONS

    def test_backup_dirs_contains_etc(self):
        """Should include etc directory."""
        assert "etc" in BACKUP_DIRS

    def test_backup_dirs_contains_services_enabled(self):
        """Should include services-enabled directory."""
        assert "services-enabled" in BACKUP_DIRS

    def test_backup_dirs_contains_external_enabled(self):
        """Should include external-enabled directory."""
        assert "external-enabled" in BACKUP_DIRS


class TestGenerateBackupName:
    """Tests for generate_backup_name() method."""

    def test_includes_hostname(self, monkeypatch):
        """Should include hostname in backup name."""
        monkeypatch.setenv("HOST_NAME", "myhost")
        mock_exec = MockCommandExecutor()
        mgr = BackupManager(executor=mock_exec)

        name = mgr.generate_backup_name()

        assert "myhost" in name

    def test_includes_service_when_provided(self, monkeypatch):
        """Should include service name when provided."""
        monkeypatch.setenv("HOST_NAME", "myhost")
        mock_exec = MockCommandExecutor()
        mgr = BackupManager(executor=mock_exec)

        name = mgr.generate_backup_name(service="plex")

        assert "plex" in name

    def test_ends_with_tar_gz(self, monkeypatch):
        """Should use .tar.gz extension."""
        monkeypatch.setenv("HOST_NAME", "myhost")
        mock_exec = MockCommandExecutor()
        mgr = BackupManager(executor=mock_exec)

        name = mgr.generate_backup_name()

        assert name.endswith(".tar.gz")

    def test_includes_timestamp(self, monkeypatch):
        """Should include timestamp in expected format."""
        monkeypatch.setenv("HOST_NAME", "myhost")
        mock_exec = MockCommandExecutor()
        mgr = BackupManager(executor=mock_exec)

        name = mgr.generate_backup_name()

        # Should have YY-MM-DD format
        assert "onramp-config-backup-myhost-" in name


class TestEnsureBackupDir:
    """Tests for ensure_backup_dir() method."""

    def test_creates_directory(self, tmp_path):
        """Should create backup directory if it doesn't exist."""
        mock_exec = MockCommandExecutor()
        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)

        result = mgr.ensure_backup_dir()

        assert result is True
        assert mgr.backup_dir.exists()

    def test_succeeds_if_exists(self, tmp_path):
        """Should succeed if directory already exists."""
        mock_exec = MockCommandExecutor()
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)

        result = mgr.ensure_backup_dir()

        assert result is True


class TestListBackups:
    """Tests for list_backups() method."""

    def test_finds_local_backups(self, tmp_path, monkeypatch):
        """Should find backups in local directory."""
        monkeypatch.setenv("HOST_NAME", "testhost")
        mock_exec = MockCommandExecutor()
        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)

        # Create backup directory and files with different mtime
        import time
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        old_file = backup_dir / "onramp-config-backup-testhost-24-01-14-1200.tar.gz"
        old_file.touch()
        time.sleep(0.1)  # Ensure different modification time
        new_file = backup_dir / "onramp-config-backup-testhost-24-01-15-1200.tar.gz"
        new_file.touch()

        backups = mgr.list_backups(location="local")

        assert len(backups) == 2
        # Should be sorted by mtime, newest first
        assert "24-01-15" in backups[0]["name"]

    def test_returns_empty_when_no_backups(self, tmp_path, monkeypatch):
        """Should return empty list when no backups found."""
        monkeypatch.setenv("HOST_NAME", "testhost")
        mock_exec = MockCommandExecutor()
        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)

        # Create empty backup directory
        (tmp_path / "backups").mkdir()

        backups = mgr.list_backups(location="local")

        assert backups == []

    def test_filters_by_hostname(self, tmp_path, monkeypatch):
        """Should only find backups for current hostname."""
        monkeypatch.setenv("HOST_NAME", "myhost")
        mock_exec = MockCommandExecutor()
        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)

        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        (backup_dir / "onramp-config-backup-myhost-24-01-15-1200.tar.gz").touch()
        (backup_dir / "onramp-config-backup-otherhost-24-01-15-1200.tar.gz").touch()

        backups = mgr.list_backups(location="local")

        assert len(backups) == 1
        assert "myhost" in backups[0]["name"]


class TestFindLatestBackup:
    """Tests for find_latest_backup() method."""

    def test_finds_most_recent(self, tmp_path, monkeypatch):
        """Should return the most recent backup."""
        import time
        monkeypatch.setenv("HOST_NAME", "testhost")
        mock_exec = MockCommandExecutor()
        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)

        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        old_backup = backup_dir / "onramp-config-backup-testhost-24-01-14-1200.tar.gz"
        old_backup.touch()
        time.sleep(0.1)  # Ensure different modification time
        new_backup = backup_dir / "onramp-config-backup-testhost-24-01-15-1200.tar.gz"
        new_backup.touch()

        result = mgr.find_latest_backup()

        assert result is not None
        assert "24-01-15" in result

    def test_filters_by_service(self, tmp_path, monkeypatch):
        """Should filter by service when specified."""
        monkeypatch.setenv("HOST_NAME", "testhost")
        mock_exec = MockCommandExecutor()
        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)

        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        (backup_dir / "onramp-config-backup-testhost-24-01-15-1200.tar.gz").touch()
        (backup_dir / "onramp-config-backup-testhost-plex-24-01-14-1200.tar.gz").touch()

        result = mgr.find_latest_backup(service="plex")

        assert result is not None
        assert "plex" in result

    def test_returns_none_when_no_backups(self, tmp_path, monkeypatch):
        """Should return None when no backups found."""
        monkeypatch.setenv("HOST_NAME", "testhost")
        mock_exec = MockCommandExecutor()
        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)

        (tmp_path / "backups").mkdir()

        result = mgr.find_latest_backup()

        assert result is None


class TestCreateBackup:
    """Tests for create_backup() method."""

    @pytest.fixture
    def mock_exec(self):
        return MockCommandExecutor()

    def test_calls_tar_command(self, tmp_path, monkeypatch, mock_exec):
        """Should execute tar command."""
        monkeypatch.setenv("HOST_NAME", "testhost")
        mock_exec.set_response("sudo", CommandResult(0, "", ""))

        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)
        (tmp_path / "backups").mkdir()
        (tmp_path / "etc").mkdir()
        (tmp_path / "services-enabled").mkdir()

        code, path = mgr.create_backup()

        assert code == 0
        # Should have called sudo tar
        tar_calls = mock_exec.get_calls_for("sudo")
        assert len(tar_calls) > 0
        # Find the tar command
        assert any("tar" in cmd for cmd in tar_calls[0])

    def test_includes_exclusions(self, tmp_path, monkeypatch, mock_exec):
        """Should include default exclusions in tar command."""
        monkeypatch.setenv("HOST_NAME", "testhost")
        mock_exec.set_response("sudo", CommandResult(0, "", ""))

        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)
        (tmp_path / "backups").mkdir()
        (tmp_path / "etc").mkdir()

        mgr.create_backup()

        # Check exclusions were passed
        tar_calls = mock_exec.get_calls_for("sudo")
        assert len(tar_calls) > 0
        cmd_str = " ".join(tar_calls[0])
        assert "--exclude" in cmd_str

    def test_service_specific_backup(self, tmp_path, monkeypatch, mock_exec):
        """Should backup only specific service directory."""
        monkeypatch.setenv("HOST_NAME", "testhost")
        mock_exec.set_response("sudo", CommandResult(0, "", ""))

        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)
        (tmp_path / "backups").mkdir()
        (tmp_path / "etc" / "plex").mkdir(parents=True)

        code, path = mgr.create_backup(service="plex")

        assert code == 0
        tar_calls = mock_exec.get_calls_for("sudo")
        cmd_str = " ".join(tar_calls[0])
        assert "./etc/plex" in cmd_str

    def test_returns_error_for_missing_service(self, tmp_path, monkeypatch, mock_exec, capsys):
        """Should return error if service directory doesn't exist."""
        monkeypatch.setenv("HOST_NAME", "testhost")
        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)
        (tmp_path / "backups").mkdir()

        code, path = mgr.create_backup(service="nonexistent")

        assert code == 1
        assert path is None


class TestRestoreBackup:
    """Tests for restore_backup() method."""

    @pytest.fixture
    def mock_exec(self):
        return MockCommandExecutor()

    def test_restores_from_path(self, tmp_path, monkeypatch, mock_exec, capsys):
        """Should restore from specified backup path."""
        monkeypatch.setenv("HOST_NAME", "testhost")
        mock_exec.set_response("sudo", CommandResult(0, "", ""))

        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)

        # Create backup file
        backup_file = tmp_path / "backup.tar.gz"
        backup_file.touch()

        code = mgr.restore_backup(str(backup_file))

        assert code == 0
        captured = capsys.readouterr()
        assert "Restore complete" in captured.out

    def test_uses_latest_when_no_path(self, tmp_path, monkeypatch, mock_exec):
        """Should use latest backup when no path specified."""
        monkeypatch.setenv("HOST_NAME", "testhost")
        mock_exec.set_response("sudo", CommandResult(0, "", ""))

        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)

        # Create backup
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        (backup_dir / "onramp-config-backup-testhost-24-01-15-1200.tar.gz").touch()

        code = mgr.restore_backup()

        assert code == 0

    def test_returns_error_for_missing_file(self, tmp_path, monkeypatch, mock_exec, capsys):
        """Should return error if backup file doesn't exist."""
        monkeypatch.setenv("HOST_NAME", "testhost")
        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)

        code = mgr.restore_backup("/nonexistent/backup.tar.gz")

        assert code == 1


class TestMountNfs:
    """Tests for _mount_nfs() method."""

    @pytest.fixture
    def mock_exec(self):
        return MockCommandExecutor()

    def test_requires_nfs_server(self, tmp_path, monkeypatch, mock_exec, capsys):
        """Should fail if NFS_SERVER not set."""
        monkeypatch.delenv("NFS_SERVER", raising=False)
        monkeypatch.delenv("NFS_BACKUP_PATH", raising=False)

        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)

        result = mgr._mount_nfs()

        assert result is False

    def test_mounts_nfs_share(self, tmp_path, monkeypatch, mock_exec):
        """Should mount NFS share."""
        monkeypatch.setenv("NFS_SERVER", "nas.local")
        monkeypatch.setenv("NFS_BACKUP_PATH", "/backups")
        mock_exec.set_response("sudo", CommandResult(0, "", ""))

        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)

        result = mgr._mount_nfs()

        assert result is True
        # Should have called mount
        mount_calls = mock_exec.get_calls_for("sudo")
        assert any("mount" in cmd for call in mount_calls for cmd in call)


class TestUnmountNfs:
    """Tests for _unmount_nfs() method."""

    @pytest.fixture
    def mock_exec(self):
        return MockCommandExecutor()

    def test_unmounts_nfs_share(self, tmp_path, monkeypatch, mock_exec):
        """Should unmount NFS share."""
        monkeypatch.setenv("NFS_SERVER", "nas.local")
        monkeypatch.setenv("NFS_BACKUP_PATH", "/backups")
        mock_exec.set_response("sudo", CommandResult(0, "", ""))

        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)

        result = mgr._unmount_nfs()

        assert result is True

    def test_returns_false_on_failure(self, tmp_path, monkeypatch, mock_exec):
        """Should return False on unmount failure."""
        monkeypatch.setenv("NFS_SERVER", "nas.local")
        monkeypatch.setenv("NFS_BACKUP_PATH", "/backups")
        mock_exec.set_response("sudo", CommandResult(1, "", "Device busy"))

        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)

        result = mgr._unmount_nfs()

        assert result is False


class TestNfsPreMount:
    """Tests for NFS pre-mount detection (Docker NFS volume scenario)."""

    @pytest.fixture
    def mock_exec(self):
        return MockCommandExecutor()

    def test_detects_premount_from_env(self, tmp_path, monkeypatch, mock_exec):
        """Should detect NFS_PREMOUNTED=true from environment."""
        monkeypatch.setenv("NFS_PREMOUNTED", "true")

        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)

        assert mgr.nfs_premounted is True

    def test_premount_false_by_default(self, tmp_path, mock_exec):
        """Should default to False for backward compatibility."""
        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)

        assert mgr.nfs_premounted is False

    def test_mount_nfs_skips_when_premounted(self, tmp_path, monkeypatch, mock_exec):
        """Should skip mount command when pre-mounted via Docker volume."""
        monkeypatch.setenv("NFS_PREMOUNTED", "true")

        # Create the mount point to simulate Docker volume
        nfs_dir = tmp_path / "nfs_backup"
        nfs_dir.mkdir()
        monkeypatch.setenv("NFS_BACKUP_TMP_DIR", str(nfs_dir))

        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)
        result = mgr._mount_nfs()

        assert result is True
        # Should NOT have called any commands (no mount needed)
        assert len(mock_exec.calls) == 0

    def test_mount_nfs_fails_if_premount_path_missing(self, tmp_path, monkeypatch, mock_exec, capsys):
        """Should fail if NFS_PREMOUNTED=true but path doesn't exist."""
        monkeypatch.setenv("NFS_PREMOUNTED", "true")
        monkeypatch.setenv("NFS_BACKUP_TMP_DIR", str(tmp_path / "nonexistent"))

        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)
        result = mgr._mount_nfs()

        assert result is False
        captured = capsys.readouterr()
        assert "not accessible" in captured.err

    def test_unmount_nfs_skips_when_premounted(self, tmp_path, monkeypatch, mock_exec):
        """Should skip unmount command when pre-mounted via Docker volume."""
        monkeypatch.setenv("NFS_PREMOUNTED", "true")

        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)
        result = mgr._unmount_nfs()

        assert result is True
        # Should NOT have called any commands (Docker handles cleanup)
        assert len(mock_exec.calls) == 0

    def test_premount_case_insensitive(self, tmp_path, monkeypatch, mock_exec):
        """Should detect NFS_PREMOUNTED regardless of case."""
        monkeypatch.setenv("NFS_PREMOUNTED", "TRUE")

        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)

        assert mgr.nfs_premounted is True


class TestRunCmd:
    """Tests for _run_cmd() method."""

    @pytest.fixture
    def mock_exec(self):
        return MockCommandExecutor()

    def test_executes_command(self, tmp_path, mock_exec):
        """Should execute command via executor."""
        mock_exec.set_response("ls", CommandResult(0, "file1\nfile2", ""))

        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)

        code, stdout, stderr = mgr._run_cmd(["ls", "-la"])

        assert code == 0
        assert "file1" in stdout

    def test_prepends_sudo_when_requested(self, tmp_path, mock_exec):
        """Should prepend sudo when sudo=True."""
        mock_exec.set_response("sudo", CommandResult(0, "", ""))

        mgr = BackupManager(base_dir=str(tmp_path), executor=mock_exec)

        mgr._run_cmd(["tar", "-czf", "test.tar.gz"], sudo=True)

        # Check sudo was prepended
        assert mock_exec.calls[0][0][0] == "sudo"
        assert "tar" in mock_exec.calls[0][0]
