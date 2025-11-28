"""Mock command executor for testing."""

import sys
sys.path.insert(0, str(__file__).replace("\\", "/").rsplit("/tests/", 1)[0] + "/scripts")

from ports.command import CommandResult


class MockCommandExecutor:
    """Mock command executor that returns preconfigured responses."""

    def __init__(self):
        self.responses: dict[str, CommandResult] = {}
        self.calls: list[tuple[list[str], str | None, bool, bool, str | None]] = []
        self.default_response = CommandResult(0, "", "")

    def set_response(self, cmd_key: str, result: CommandResult) -> None:
        """Configure a response for a command.

        Args:
            cmd_key: Command identifier (typically cmd[0] like 'tar', 'mount')
            result: CommandResult to return
        """
        self.responses[cmd_key] = result

    def set_default_response(self, returncode: int = 0, stdout: str = "", stderr: str = "") -> None:
        """Set the default response for unmatched commands."""
        self.default_response = CommandResult(returncode, stdout, stderr)

    def run(
        self,
        cmd: list[str],
        input: str | None = None,
        capture_output: bool = True,
        check: bool = False,
        cwd: str | None = None,
    ) -> CommandResult:
        """Mock command execution that returns preconfigured response.

        Records the call for later assertion.
        """
        self.calls.append((cmd, input, capture_output, check, cwd))

        # Try to find a matching response
        if cmd and cmd[0] in self.responses:
            return self.responses[cmd[0]]

        # Try full command match
        cmd_str = " ".join(cmd)
        if cmd_str in self.responses:
            return self.responses[cmd_str]

        return self.default_response

    def assert_called_once(self) -> None:
        """Assert that exactly one command was executed."""
        assert len(self.calls) == 1, f"Expected 1 call, got {len(self.calls)}"

    def assert_called_with_command(self, expected_cmd: str | list[str]) -> None:
        """Assert that a specific command was executed."""
        if isinstance(expected_cmd, str):
            expected_cmd = [expected_cmd]

        for cmd, _, _, _, _ in self.calls:
            if cmd[0] == expected_cmd[0]:
                return
        raise AssertionError(f"No call found starting with {expected_cmd[0]}. Calls: {[c[0] for c, *_ in self.calls]}")

    def get_calls_for(self, cmd_prefix: str) -> list[list[str]]:
        """Get all calls that start with a specific command."""
        return [cmd for cmd, *_ in self.calls if cmd and cmd[0] == cmd_prefix]

    def reset(self) -> None:
        """Clear all recorded calls."""
        self.calls.clear()
