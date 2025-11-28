"""Command executor protocol for dependency injection."""

from dataclasses import dataclass
from typing import Protocol


@dataclass
class CommandResult:
    """Result of executing a shell command."""

    returncode: int
    stdout: str
    stderr: str


class CommandExecutor(Protocol):
    """Protocol for executing shell commands."""

    def run(
        self,
        cmd: list[str],
        input: str | None = None,
        capture_output: bool = True,
        check: bool = False,
        cwd: str | None = None,
    ) -> CommandResult:
        """Execute a shell command.

        Args:
            cmd: Command and arguments as list
            input: Optional stdin input
            capture_output: Whether to capture stdout/stderr
            check: Whether to raise on non-zero return code
            cwd: Working directory for command

        Returns:
            CommandResult with returncode, stdout, stderr
        """
        ...
