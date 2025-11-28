"""Command executor implementation using subprocess."""

import subprocess
from ports.command import CommandResult


class SubprocessCommandExecutor:
    """Command executor using Python's subprocess module."""

    def run(
        self,
        cmd: list[str],
        input: str | None = None,
        capture_output: bool = True,
        check: bool = False,
        cwd: str | None = None,
    ) -> CommandResult:
        """Execute a shell command using subprocess.run().

        Args:
            cmd: Command and arguments as list
            input: Optional stdin input
            capture_output: Whether to capture stdout/stderr
            check: Whether to raise on non-zero return code
            cwd: Working directory for command

        Returns:
            CommandResult with returncode, stdout, stderr
        """
        try:
            result = subprocess.run(
                cmd,
                input=input,
                capture_output=capture_output,
                text=True,
                check=check,
                cwd=cwd,
            )
            return CommandResult(
                returncode=result.returncode,
                stdout=result.stdout or "",
                stderr=result.stderr or "",
            )
        except subprocess.CalledProcessError as e:
            return CommandResult(
                returncode=e.returncode,
                stdout=e.stdout or "",
                stderr=e.stderr or "",
            )
        except Exception as e:
            return CommandResult(
                returncode=1,
                stdout="",
                stderr=str(e),
            )
