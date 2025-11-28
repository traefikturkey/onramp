"""Port interfaces (Protocols) for dependency injection."""

from ports.http import HttpClient
from ports.command import CommandExecutor, CommandResult
from ports.docker import DockerExecutor

__all__ = ["HttpClient", "CommandExecutor", "CommandResult", "DockerExecutor"]
