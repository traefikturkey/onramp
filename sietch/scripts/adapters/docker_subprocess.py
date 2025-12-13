"""Docker executor implementation using subprocess."""

import subprocess


class SubprocessDockerExecutor:
    """Docker executor using subprocess to call docker CLI."""

    def exec(
        self,
        container: str,
        cmd: list[str],
        interactive: bool = False,
    ) -> tuple[int, str, str]:
        """Execute command in a Docker container using docker exec.

        Args:
            container: Container name or ID
            cmd: Command and arguments to execute
            interactive: Whether to run in interactive mode

        Returns:
            Tuple of (returncode, stdout, stderr)
        """
        docker_cmd = ["docker", "exec"]
        if interactive:
            docker_cmd.extend(["-it"])
        docker_cmd.append(container)
        docker_cmd.extend(cmd)

        try:
            result = subprocess.run(
                docker_cmd,
                capture_output=not interactive,
                text=True,
                timeout=30,  # 30 second timeout to prevent hanging
            )
            return result.returncode, result.stdout or "", result.stderr or ""
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out after 30 seconds"
        except Exception as e:
            return 1, "", str(e)
