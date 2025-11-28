"""Docker executor protocol for dependency injection."""

from typing import Protocol


class DockerExecutor(Protocol):
    """Protocol for executing commands in Docker containers."""

    def exec(
        self,
        container: str,
        cmd: list[str],
        interactive: bool = False,
    ) -> tuple[int, str, str]:
        """Execute command in a Docker container.

        Args:
            container: Container name or ID
            cmd: Command and arguments to execute
            interactive: Whether to run in interactive mode

        Returns:
            Tuple of (returncode, stdout, stderr)
        """
        ...
