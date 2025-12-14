#!/usr/bin/env python
"""
operations.py - Declarative operations for OnRamp scaffold manifests

Implements operation handlers for scaffold.yml manifests:
- mkdir: Create directories
- generate_rsa_key: Generate RSA keypair via OpenSSL
- generate_random: Generate random bytes (base64/hex)
- download: Download file from URL
- delete: Delete file
- chown: Change file ownership
- chmod: Change file permissions
"""

import os
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ports.command import CommandExecutor


@dataclass
class OperationContext:
    """Context passed to all operations."""

    service: str
    base_dir: Path
    scaffold_dir: Path
    etc_dir: Path
    services_enabled: Path
    command_executor: "CommandExecutor | None" = field(default=None)

    def __post_init__(self):
        """Initialize command executor if not provided."""
        if self.command_executor is None:
            from adapters.subprocess_cmd import SubprocessCommandExecutor

            self.command_executor = SubprocessCommandExecutor()

    def resolve_path(self, path: str) -> Path:
        """Resolve a path relative to etc/<service>/."""
        return self.etc_dir / self.service / path


class Condition:
    """Evaluates conditional execution logic."""

    def __init__(self, config: dict[str, Any], ctx: OperationContext):
        self.config = config
        self.ctx = ctx

    def evaluate(self) -> bool:
        """Evaluate the condition, return True if operation should execute."""
        cond_type = self.config.get("type", "")
        path = self.ctx.resolve_path(self.config.get("path", ""))

        if cond_type == "file_exists":
            return path.exists() and path.is_file()
        elif cond_type == "file_not_exists":
            return not path.exists()
        elif cond_type == "dir_empty":
            # Non-existent directory is NOT empty - it doesn't exist
            # Operations using this condition likely assume the directory exists
            if not path.exists() or not path.is_dir():
                return False
            return len(list(path.iterdir())) == 0
        elif cond_type == "dir_not_empty":
            if not path.exists() or not path.is_dir():
                return False
            return len(list(path.iterdir())) > 0
        else:
            print(f"    Unknown condition type: {cond_type}")
            return False


class Operation(ABC):
    """Base class for scaffold operations."""

    def __init__(self, config: dict[str, Any], ctx: OperationContext):
        self.config = config
        self.ctx = ctx

    @abstractmethod
    def execute(self) -> bool:
        """Execute the operation. Returns True on success."""
        pass

    def should_execute(self) -> bool:
        """Check if operation should run based on conditions."""
        if "condition" not in self.config:
            return True
        condition = Condition(self.config["condition"], self.ctx)
        return condition.evaluate()

    def resolve_path(self, path: str) -> Path:
        """Resolve output path relative to etc/<service>/."""
        return self.ctx.resolve_path(path)

    def expand_env(self, value: str) -> str:
        """Expand environment variables in a string."""
        return os.path.expandvars(value)


class MkdirOp(Operation):
    """Create directory."""

    def execute(self) -> bool:
        path = self.resolve_path(self.config["path"])
        mode = int(self.config.get("mode", "0755"), 8)

        try:
            path.mkdir(parents=True, exist_ok=True)
            path.chmod(mode)
            print(f"    Created directory: {path}")
            return True
        except Exception as e:
            print(f"    Error creating directory {path}: {e}")
            return False


class GenerateRsaKeyOp(Operation):
    """Generate RSA keypair using OpenSSL."""

    def execute(self) -> bool:
        private_path = self.resolve_path(self.config["output"])
        public_key_name = self.config.get("public_key", "")
        public_path = self.resolve_path(public_key_name) if public_key_name else None
        bits = self.config.get("bits", 2048)
        skip_if_exists = self.config.get("skip_if_exists", True)

        # Check if should skip
        if skip_if_exists and private_path.exists():
            print(f"    Skipped (exists): {private_path}")
            return True

        try:
            # Ensure parent directory exists
            private_path.parent.mkdir(parents=True, exist_ok=True)

            # Generate private key
            executor = self.ctx.command_executor
            result = executor.run(
                [
                    "openssl",
                    "genpkey",
                    "-algorithm",
                    "RSA",
                    "-pkeyopt",
                    f"rsa_keygen_bits:{bits}",
                ],
                capture_output=True,
                check=True,
            )
            if result.returncode != 0:
                print(f"    OpenSSL error: {result.stderr}")
                return False

            private_path.write_text(result.stdout)
            private_path.chmod(0o644)
            print(f"    Generated private key: {private_path}")

            # Extract public key if requested
            if public_path:
                result = executor.run(
                    ["openssl", "rsa", "-pubout"],
                    input=private_path.read_text(),
                    capture_output=True,
                    check=True,
                )
                if result.returncode != 0:
                    print(f"    OpenSSL error: {result.stderr}")
                    return False
                public_path.write_text(result.stdout)
                public_path.chmod(0o644)
                print(f"    Extracted public key: {public_path}")

            return True
        except Exception as e:
            print(f"    Error generating RSA key: {e}")
            return False


class GenerateRandomOp(Operation):
    """Generate random bytes using OpenSSL."""

    def execute(self) -> bool:
        output_path = self.resolve_path(self.config["output"])
        num_bytes = self.config.get("bytes", 32)
        encoding = self.config.get("encoding", "base64")
        skip_if_exists = self.config.get("skip_if_exists", True)

        if skip_if_exists and output_path.exists():
            print(f"    Skipped (exists): {output_path}")
            return True

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            executor = self.ctx.command_executor
            result = executor.run(
                ["openssl", "rand", f"-{encoding}", str(num_bytes)],
                capture_output=True,
                check=True,
            )
            if result.returncode != 0:
                print(f"    OpenSSL error: {result.stderr}")
                return False

            output_path.write_text(result.stdout)
            output_path.chmod(0o644)
            print(f"    Generated random data: {output_path}")
            return True
        except Exception as e:
            print(f"    Error generating random data: {e}")
            return False


class DownloadOp(Operation):
    """Download file from URL."""

    def execute(self) -> bool:
        url = self.config["url"]
        output_path = self.resolve_path(self.config["output"])
        mode = self.config.get("mode")
        skip_if_exists = self.config.get("skip_if_exists", False)

        if skip_if_exists and output_path.exists():
            print(f"    Skipped (exists): {output_path}")
            return True

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Use wget for downloads (more reliable with redirects)
            executor = self.ctx.command_executor
            result = executor.run(
                ["wget", "-q", "-O", str(output_path), url],
                capture_output=True,
                check=True,
            )
            if result.returncode != 0:
                print(f"    Download error: {result.stderr or 'unknown error'}")
                return False

            print(f"    Downloaded: {url} -> {output_path}")

            if mode:
                output_path.chmod(int(mode, 8))

            return True
        except Exception as e:
            print(f"    Error downloading {url}: {e}")
            return False


class DeleteOp(Operation):
    """Delete file or directory."""

    def execute(self) -> bool:
        path = self.resolve_path(self.config["path"])

        if not path.exists():
            print(f"    Skipped (not found): {path}")
            return True

        try:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            print(f"    Deleted: {path}")
            return True
        except Exception as e:
            print(f"    Error deleting {path}: {e}")
            return False


class ChownOp(Operation):
    """Change file/directory ownership."""

    def execute(self) -> bool:
        path = self.resolve_path(self.config["path"])
        user = self.expand_env(self.config.get("user", ""))
        group = self.expand_env(self.config.get("group", ""))
        recursive = self.config.get("recursive", False)

        if not path.exists():
            print(f"    Skipped (not found): {path}")
            return True

        try:
            # Build chown command
            ownership = f"{user}:{group}" if group else user
            cmd = ["chown"]
            if recursive:
                cmd.append("-R")
            cmd.extend([ownership, str(path)])

            executor = self.ctx.command_executor
            result = executor.run(cmd, capture_output=True, check=True)
            if result.returncode != 0:
                # chown may fail in containers - treat as warning
                print(
                    f"    Warning: chown failed (may be expected in container): {result.stderr}"
                )
                return True

            print(f"    Changed ownership: {path} -> {ownership}")
            return True
        except Exception as e:
            print(f"    Error changing ownership of {path}: {e}")
            return False


class ChmodOp(Operation):
    """Change file/directory permissions."""

    def execute(self) -> bool:
        path = self.resolve_path(self.config["path"])
        mode = self.config["mode"]
        recursive = self.config.get("recursive", False)

        if not path.exists():
            print(f"    Skipped (not found): {path}")
            return True

        try:
            cmd = ["chmod"]
            if recursive:
                cmd.append("-R")
            cmd.extend([mode, str(path)])

            executor = self.ctx.command_executor
            result = executor.run(cmd, capture_output=True, check=True)
            if result.returncode != 0:
                print(f"    Error: chmod failed: {result.stderr}")
                return False

            print(f"    Changed permissions: {path} -> {mode}")
            return True
        except Exception as e:
            print(f"    Error changing permissions of {path}: {e}")
            return False


# Registry of operation types
OPERATIONS: dict[str, type[Operation]] = {
    "mkdir": MkdirOp,
    "generate_rsa_key": GenerateRsaKeyOp,
    "generate_random": GenerateRandomOp,
    "download": DownloadOp,
    "delete": DeleteOp,
    "chown": ChownOp,
    "chmod": ChmodOp,
}


def execute_operation(config: dict[str, Any], ctx: OperationContext) -> bool:
    """Execute a single operation from manifest config."""
    op_type = config.get("type", "")

    if op_type not in OPERATIONS:
        print(f"    Unknown operation type: {op_type}")
        return False

    op_class = OPERATIONS[op_type]
    operation = op_class(config, ctx)

    if not operation.should_execute():
        print(f"    Skipped (condition not met): {op_type}")
        return True

    return operation.execute()
