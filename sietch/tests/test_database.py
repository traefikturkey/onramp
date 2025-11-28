"""Tests for database.py with mocked Docker executor."""

import pytest
import sys
from pathlib import Path

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from database import DatabaseManager
from tests.mocks.docker import MockDockerExecutor


class TestDatabaseManagerInit:
    """Tests for DatabaseManager initialization."""

    def test_default_container_name(self):
        """Should use mariadb as default container name."""
        mock_docker = MockDockerExecutor()
        mgr = DatabaseManager(docker=mock_docker)
        assert mgr.container_name == "mariadb"

    def test_custom_container_name(self):
        """Should accept custom container name."""
        mock_docker = MockDockerExecutor()
        mgr = DatabaseManager(container_name="custom-db", docker=mock_docker)
        assert mgr.container_name == "custom-db"

    def test_uses_injected_docker_executor(self):
        """Should use injected docker executor."""
        mock_docker = MockDockerExecutor()
        mgr = DatabaseManager(docker=mock_docker)
        assert mgr._docker is mock_docker


class TestGeneratePassword:
    """Tests for generate_password() - pure function."""

    def test_default_length(self):
        """Should generate 32-char password by default."""
        mock_docker = MockDockerExecutor()
        mgr = DatabaseManager(docker=mock_docker)

        password = mgr.generate_password()

        assert len(password) == 32
        assert password.isalnum()  # hex chars only

    def test_custom_length(self):
        """Should generate password of specified length."""
        mock_docker = MockDockerExecutor()
        mgr = DatabaseManager(docker=mock_docker)

        password = mgr.generate_password(length=16)

        assert len(password) == 16

    def test_uniqueness(self):
        """Should generate unique passwords."""
        mock_docker = MockDockerExecutor()
        mgr = DatabaseManager(docker=mock_docker)

        passwords = [mgr.generate_password() for _ in range(10)]

        assert len(set(passwords)) == 10  # All unique


class TestSavePassword:
    """Tests for save_password() - filesystem operation."""

    def test_creates_password_file(self, tmp_path):
        """Should create password file with correct content."""
        mock_docker = MockDockerExecutor()
        mgr = DatabaseManager(base_dir=str(tmp_path), docker=mock_docker)

        result = mgr.save_password("testuser", "testpass123")

        assert result.exists()
        content = result.read_text()
        assert "testuser" in content
        assert "testpass123" in content

    def test_creates_parent_directories(self, tmp_path):
        """Should create parent directories if they don't exist."""
        mock_docker = MockDockerExecutor()
        mgr = DatabaseManager(base_dir=str(tmp_path), docker=mock_docker)

        # etc/.db_passwords/ should be created
        result = mgr.save_password("myuser", "mypass")

        assert result.parent.exists()
        assert ".db_passwords" in str(result.parent)


class TestListDatabases:
    """Tests for list_databases() - docker exec operation."""

    @pytest.fixture
    def mock_docker(self):
        return MockDockerExecutor()

    @pytest.fixture
    def mgr(self, mock_docker, tmp_path):
        return DatabaseManager(base_dir=str(tmp_path), docker=mock_docker)

    def test_parses_output(self, mgr, mock_docker):
        """Should parse database list from mysql output."""
        mock_docker.set_response(
            "mysql",
            0,
            "Database\nmysql\ntest_db\ninformation_schema\n",
            "",
        )

        code, databases = mgr.list_databases()

        assert code == 0
        assert "mysql" in databases
        assert "test_db" in databases
        assert "information_schema" in databases

    def test_handles_error(self, mgr, mock_docker, capsys):
        """Should handle errors gracefully."""
        mock_docker.set_response("mysql", 1, "", "Connection refused")

        code, databases = mgr.list_databases()

        assert code == 1
        assert databases == []


class TestListUsers:
    """Tests for list_users() - docker exec operation."""

    @pytest.fixture
    def mock_docker(self):
        return MockDockerExecutor()

    @pytest.fixture
    def mgr(self, mock_docker, tmp_path):
        return DatabaseManager(base_dir=str(tmp_path), docker=mock_docker)

    def test_parses_output(self, mgr, mock_docker):
        """Should parse user list from mysql output."""
        mock_docker.set_response(
            "mysql",
            0,
            "User\tHost\nroot\tlocalhost\nmyapp\t%\n",
            "",
        )

        code, users = mgr.list_users()

        assert code == 0
        assert len(users) == 2

    def test_handles_error(self, mgr, mock_docker, capsys):
        """Should handle errors gracefully."""
        mock_docker.set_response("mysql", 1, "", "Access denied")

        code, users = mgr.list_users()

        assert code == 1
        assert users == []


class TestCreateDatabase:
    """Tests for create_database() - docker exec operation."""

    @pytest.fixture
    def mock_docker(self):
        return MockDockerExecutor()

    @pytest.fixture
    def mgr(self, mock_docker, tmp_path):
        return DatabaseManager(base_dir=str(tmp_path), docker=mock_docker)

    def test_creates_database(self, mgr, mock_docker, capsys):
        """Should execute CREATE DATABASE statement."""
        mock_docker.set_response("mysql", 0, "", "")

        code = mgr.create_database("testdb")

        assert code == 0
        mock_docker.assert_sql_executed("CREATE DATABASE")
        captured = capsys.readouterr()
        assert "testdb" in captured.out
        assert "created successfully" in captured.out

    def test_handles_error(self, mgr, mock_docker, capsys):
        """Should handle database creation errors."""
        mock_docker.set_response("mysql", 1, "", "Database already exists")

        code = mgr.create_database("testdb")

        assert code == 1


class TestCreateUser:
    """Tests for create_user() - docker exec operation."""

    @pytest.fixture
    def mock_docker(self):
        return MockDockerExecutor()

    @pytest.fixture
    def mgr(self, mock_docker, tmp_path):
        return DatabaseManager(base_dir=str(tmp_path), docker=mock_docker)

    def test_creates_user_with_password(self, mgr, mock_docker, capsys):
        """Should create user with provided password."""
        mock_docker.set_response("mysql", 0, "", "")

        code, returned_password = mgr.create_user("testuser", password="mypass123")

        assert code == 0
        assert returned_password is None  # Not returned when provided
        mock_docker.assert_sql_executed("CREATE USER")
        captured = capsys.readouterr()
        assert "created successfully" in captured.out

    def test_creates_user_with_generated_password(self, mgr, mock_docker, capsys):
        """Should create user with generated password."""
        mock_docker.set_response("mysql", 0, "", "")

        code, returned_password = mgr.create_user("testuser", generate=True)

        assert code == 0
        assert returned_password is not None
        assert len(returned_password) == 32
        captured = capsys.readouterr()
        assert "Password saved to" in captured.out

    def test_requires_password_or_generate(self, mgr, mock_docker, capsys):
        """Should fail when neither password nor generate is provided."""
        code, _ = mgr.create_user("testuser")

        assert code == 1


class TestGrantPrivileges:
    """Tests for grant_privileges() - docker exec operation."""

    @pytest.fixture
    def mock_docker(self):
        return MockDockerExecutor()

    @pytest.fixture
    def mgr(self, mock_docker, tmp_path):
        return DatabaseManager(base_dir=str(tmp_path), docker=mock_docker)

    def test_grants_privileges(self, mgr, mock_docker, capsys):
        """Should execute GRANT statement."""
        mock_docker.set_response("mysql", 0, "", "")

        code = mgr.grant_privileges("testdb", "testuser")

        assert code == 0
        mock_docker.assert_sql_executed("GRANT")
        captured = capsys.readouterr()
        assert "Granted" in captured.out

    def test_handles_error(self, mgr, mock_docker, capsys):
        """Should handle grant errors."""
        mock_docker.set_response("mysql", 1, "", "User not found")

        code = mgr.grant_privileges("testdb", "testuser")

        assert code == 1


class TestRemoveUser:
    """Tests for remove_user() - docker exec operation."""

    @pytest.fixture
    def mock_docker(self):
        return MockDockerExecutor()

    @pytest.fixture
    def mgr(self, mock_docker, tmp_path):
        return DatabaseManager(base_dir=str(tmp_path), docker=mock_docker)

    def test_removes_user(self, mgr, mock_docker, capsys):
        """Should execute DROP USER statement."""
        mock_docker.set_response("mysql", 0, "", "")

        code = mgr.remove_user("testuser")

        assert code == 0
        mock_docker.assert_sql_executed("DROP USER")
        captured = capsys.readouterr()
        assert "removed" in captured.out

    def test_handles_error(self, mgr, mock_docker, capsys):
        """Should handle removal errors."""
        mock_docker.set_response("mysql", 1, "", "User not found")

        code = mgr.remove_user("nonexistent")

        assert code == 1


class TestDropDatabase:
    """Tests for drop_database() - docker exec operation."""

    @pytest.fixture
    def mock_docker(self):
        return MockDockerExecutor()

    @pytest.fixture
    def mgr(self, mock_docker, tmp_path):
        return DatabaseManager(base_dir=str(tmp_path), docker=mock_docker)

    def test_drops_database(self, mgr, mock_docker, capsys):
        """Should execute DROP DATABASE statement."""
        mock_docker.set_response("mysql", 0, "", "")

        code = mgr.drop_database("testdb")

        assert code == 0
        mock_docker.assert_sql_executed("DROP DATABASE")
        captured = capsys.readouterr()
        assert "dropped" in captured.out

    def test_handles_error(self, mgr, mock_docker, capsys):
        """Should handle drop errors."""
        mock_docker.set_response("mysql", 1, "", "Database not found")

        code = mgr.drop_database("nonexistent")

        assert code == 1


class TestSetup:
    """Tests for setup() - combined workflow."""

    @pytest.fixture
    def mock_docker(self):
        return MockDockerExecutor()

    @pytest.fixture
    def mgr(self, mock_docker, tmp_path):
        return DatabaseManager(base_dir=str(tmp_path), docker=mock_docker)

    def test_complete_setup(self, mgr, mock_docker, capsys):
        """Should create user, database, and grant privileges."""
        mock_docker.set_response("mysql", 0, "", "")

        code = mgr.setup("myapp")

        assert code == 0
        captured = capsys.readouterr()
        assert "Setup complete" in captured.out
        assert "DB_USER=myapp" in captured.out
        assert "DB_NAME=myapp" in captured.out

    def test_fails_on_user_creation_error(self, mgr, mock_docker, capsys):
        """Should fail if user creation fails."""
        # First call (create_user) fails
        mock_docker.set_response("mysql", 1, "", "Error creating user")

        code = mgr.setup("myapp")

        assert code == 1


class TestDockerExec:
    """Tests for _docker_exec() method."""

    @pytest.fixture
    def mock_docker(self):
        return MockDockerExecutor()

    @pytest.fixture
    def mgr(self, mock_docker, tmp_path):
        return DatabaseManager(container_name="mydb", base_dir=str(tmp_path), docker=mock_docker)

    def test_uses_correct_container(self, mgr, mock_docker):
        """Should execute in the configured container."""
        mock_docker.set_response("mysql", 0, "test output", "")

        code, stdout, stderr = mgr._docker_exec(["mysql", "-e", "SELECT 1"])

        assert code == 0
        mock_docker.assert_called_with_container("mydb")

    def test_passes_interactive_flag(self, mgr, mock_docker):
        """Should pass interactive flag when specified."""
        mock_docker.set_default_response(0)

        mgr._docker_exec(["mysql", "-p"], interactive=True)

        # Check that interactive=True was passed
        assert any(interactive for _, _, interactive in mock_docker.calls)
