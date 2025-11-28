"""Mock Docker executor for testing."""


class MockDockerExecutor:
    """Mock Docker executor that returns preconfigured responses."""

    def __init__(self):
        self.responses: dict[str, tuple[int, str, str]] = {}
        self.calls: list[tuple[str, list[str], bool]] = []
        self.default_response: tuple[int, str, str] = (0, "", "")

    def set_response(self, cmd_key: str, returncode: int, stdout: str = "", stderr: str = "") -> None:
        """Configure a response for a command.

        Args:
            cmd_key: Command identifier (typically first element of cmd)
            returncode: Exit code to return
            stdout: Standard output to return
            stderr: Standard error to return
        """
        self.responses[cmd_key] = (returncode, stdout, stderr)

    def set_default_response(self, returncode: int = 0, stdout: str = "", stderr: str = "") -> None:
        """Set the default response for unmatched commands."""
        self.default_response = (returncode, stdout, stderr)

    def exec(
        self,
        container: str,
        cmd: list[str],
        interactive: bool = False,
    ) -> tuple[int, str, str]:
        """Mock docker exec that returns preconfigured response.

        Records the call for later assertion.
        """
        self.calls.append((container, cmd, interactive))

        # Try to find a matching response
        if cmd and cmd[0] in self.responses:
            return self.responses[cmd[0]]

        # Try SQL command matching (for mysql -e "SQL")
        if len(cmd) >= 3 and cmd[0] == "mysql" and "-e" in cmd:
            sql_idx = cmd.index("-e") + 1
            if sql_idx < len(cmd):
                sql = cmd[sql_idx]
                # Match by SQL command type
                for key in self.responses:
                    if key.upper() in sql.upper():
                        return self.responses[key]

        return self.default_response

    def assert_called_once(self) -> None:
        """Assert that exactly one exec was performed."""
        assert len(self.calls) == 1, f"Expected 1 call, got {len(self.calls)}"

    def assert_called_with_container(self, container: str) -> None:
        """Assert that a specific container was used."""
        for c, _, _ in self.calls:
            if c == container:
                return
        raise AssertionError(f"No call found for container {container}. Calls: {self.calls}")

    def assert_sql_executed(self, sql_fragment: str) -> None:
        """Assert that a SQL statement containing the fragment was executed."""
        for _, cmd, _ in self.calls:
            if len(cmd) >= 3 and cmd[0] == "mysql" and "-e" in cmd:
                sql_idx = cmd.index("-e") + 1
                if sql_idx < len(cmd) and sql_fragment.upper() in cmd[sql_idx].upper():
                    return
        raise AssertionError(f"No SQL containing '{sql_fragment}' found. Calls: {self.calls}")

    def reset(self) -> None:
        """Clear all recorded calls."""
        self.calls.clear()
