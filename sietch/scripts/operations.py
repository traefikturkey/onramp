#!/usr/bin/env python
"""
operations.py - Declarative operations for OnRamp scaffold manifests

Implements operation handlers for scaffold.yml manifests:
- mkdir: Create directories
- touch: Create empty file
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

from logging_config import get_logger

if TYPE_CHECKING:
    from ports.command import CommandExecutor

logger = get_logger(__name__)


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
            logger.warning("Unknown condition type", extra={"type": cond_type})
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
            logger.info("Created directory", extra={"path": str(path), "mode": oct(mode)})
            return True
        except Exception as e:
            logger.error(f"Failed to create directory: {e}", extra={"path": str(path)})
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
            logger.debug("Skipped existing RSA key", extra={"path": str(private_path)})
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
                logger.error("OpenSSL key generation failed", extra={"stderr": result.stderr, "path": str(private_path)})
                return False

            private_path.write_text(result.stdout)
            private_path.chmod(0o644)
            logger.info("Generated RSA private key", extra={"path": str(private_path), "bits": bits})

            # Extract public key if requested
            if public_path:
                result = executor.run(
                    ["openssl", "rsa", "-pubout"],
                    input=private_path.read_text(),
                    capture_output=True,
                    check=True,
                )
                if result.returncode != 0:
                    logger.error("OpenSSL public key extraction failed", extra={"stderr": result.stderr})
                    return False
                public_path.write_text(result.stdout)
                public_path.chmod(0o644)
                logger.info("Extracted RSA public key", extra={"path": str(public_path)})

            return True
        except Exception as e:
            logger.error(f"Failed to generate RSA key: {e}", extra={"path": str(private_path)}, exc_info=True)
            return False


class GenerateRandomOp(Operation):
    """Generate random bytes using OpenSSL."""

    def execute(self) -> bool:
        output_path = self.resolve_path(self.config["output"])
        num_bytes = self.config.get("bytes", 32)
        encoding = self.config.get("encoding", "base64")
        skip_if_exists = self.config.get("skip_if_exists", True)

        if skip_if_exists and output_path.exists():
            logger.debug("Skipped existing random data file", extra={"path": str(output_path)})
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
                logger.error("OpenSSL random generation failed", extra={"stderr": result.stderr})
                return False

            output_path.write_text(result.stdout)
            output_path.chmod(0o644)
            logger.info("Generated random data", extra={"path": str(output_path), "bytes": num_bytes, "encoding": encoding})
            return True
        except Exception as e:
            logger.error(f"Failed to generate random data: {e}", extra={"path": str(output_path)}, exc_info=True)
            return False


class DownloadOp(Operation):
    """Download file from URL."""

    def execute(self) -> bool:
        url = self.config["url"]
        output_path = self.resolve_path(self.config["output"])
        mode = self.config.get("mode")
        skip_if_exists = self.config.get("skip_if_exists", False)

        if skip_if_exists and output_path.exists():
            logger.debug("Skipped existing download", extra={"path": str(output_path)})
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
                logger.error("Download failed", extra={"url": url, "stderr": result.stderr or "unknown error"})
                return False

            logger.info("Downloaded file", extra={"url": url, "path": str(output_path)})

            if mode:
                output_path.chmod(int(mode, 8))

            return True
        except Exception as e:
            logger.error(f"Failed to download file: {e}", extra={"url": url}, exc_info=True)
            return False


class DeleteOp(Operation):
    """Delete file or directory."""

    def execute(self) -> bool:
        path = self.resolve_path(self.config["path"])

        if not path.exists():
            logger.debug("Skipped delete - path not found", extra={"path": str(path)})
            return True

        try:
            if path.is_dir():
                shutil.rmtree(path)
                logger.info("Deleted directory", extra={"path": str(path)})
            else:
                path.unlink()
                logger.info("Deleted file", extra={"path": str(path)})
            return True
        except Exception as e:
            logger.error(f"Failed to delete path: {e}", extra={"path": str(path)}, exc_info=True)
            return False


class ChownOp(Operation):
    """Change file/directory ownership."""

    def execute(self) -> bool:
        path = self.resolve_path(self.config["path"])
        user = self.expand_env(self.config.get("user", ""))
        group = self.expand_env(self.config.get("group", ""))
        recursive = self.config.get("recursive", False)

        if not path.exists():
            logger.debug("Skipped chown - path not found", extra={"path": str(path)})
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
                logger.warning(
                    "chown failed (may be expected in container)",
                    extra={"path": str(path), "ownership": ownership, "stderr": result.stderr}
                )
                return True

            logger.info("Changed ownership", extra={"path": str(path), "ownership": ownership})
            return True
        except Exception as e:
            logger.error(f"Failed to change ownership: {e}", extra={"path": str(path)}, exc_info=True)
            return False


class ChmodOp(Operation):
    """Change file/directory permissions."""

    def execute(self) -> bool:
        path = self.resolve_path(self.config["path"])
        mode = self.config["mode"]
        recursive = self.config.get("recursive", False)

        if not path.exists():
            logger.debug("Skipped chmod - path not found", extra={"path": str(path)})
            return True

        try:
            cmd = ["chmod"]
            if recursive:
                cmd.append("-R")
            cmd.extend([mode, str(path)])

            executor = self.ctx.command_executor
            result = executor.run(cmd, capture_output=True, check=True)
            if result.returncode != 0:
                logger.error("chmod failed", extra={"path": str(path), "mode": mode, "stderr": result.stderr})
                return False

            logger.info("Changed permissions", extra={"path": str(path), "mode": mode})
            return True
        except Exception as e:
            logger.error(f"Failed to change permissions: {e}", extra={"path": str(path)}, exc_info=True)
            return False


class TouchOp(Operation):
    """Create empty file (like touch command)."""

    def execute(self) -> bool:
        path = self.resolve_path(self.config["path"])
        skip_if_exists = self.config.get("skip_if_exists", True)

        if skip_if_exists and path.exists():
            logger.debug("Skipped existing file", extra={"path": str(path)})
            return True

        try:
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
            logger.info("Created file", extra={"path": str(path)})
            return True
        except Exception as e:
            logger.error(f"Failed to create file: {e}", extra={"path": str(path)}, exc_info=True)
            return False


# Registry of operation types
OPERATIONS: dict[str, type[Operation]] = {
    "mkdir": MkdirOp,
    "touch": TouchOp,
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
        logger.warning("Unknown operation type: {op_type}")
        return False

    op_class = OPERATIONS[op_type]
    operation = op_class(config, ctx)

    if not operation.should_execute():
        logger.debug("Skipped (condition not met): {op_type}")
        return True

    return operation.execute()
