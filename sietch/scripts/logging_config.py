#!/usr/bin/env python
"""
Logging configuration for OnRamp.

Provides structured logging with:
- Console output with color formatting (when available)
- File output with rotation
- JSON structured logging for automation
- Context fields (service, operation, etc.)
"""

import logging
import sys
from pathlib import Path
from typing import Any

# Try to import colorama for colored output (optional)
try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False


class ColoredFormatter(logging.Formatter):
    """Formatter that adds color to console output."""

    COLORS = {
        "DEBUG": Fore.CYAN if COLORS_AVAILABLE else "",
        "INFO": Fore.GREEN if COLORS_AVAILABLE else "",
        "WARNING": Fore.YELLOW if COLORS_AVAILABLE else "",
        "ERROR": Fore.RED if COLORS_AVAILABLE else "",
        "CRITICAL": Fore.RED + Style.BRIGHT if COLORS_AVAILABLE else "",
    }
    RESET = Style.RESET_ALL if COLORS_AVAILABLE else ""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with color."""
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"

        # Format the message
        result = super().format(record)

        # Reset levelname for other handlers
        record.levelname = levelname

        return result


class StructuredFormatter(logging.Formatter):
    """Formatter that outputs structured log data (key=value pairs)."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as structured key=value pairs."""
        parts = [
            f"timestamp={self.formatTime(record, self.datefmt)}",
            f"level={record.levelname}",
            f"logger={record.name}",
            f"message={record.getMessage()}",
        ]

        # Add extra context fields
        if hasattr(record, "service"):
            parts.append(f"service={record.service}")
        if hasattr(record, "operation"):
            parts.append(f"operation={record.operation}")
        if hasattr(record, "path"):
            parts.append(f"path={record.path}")
        if hasattr(record, "duration_ms"):
            parts.append(f"duration_ms={record.duration_ms}")

        # Add exception info if present
        if record.exc_info:
            parts.append(f"exception={self.formatException(record.exc_info)}")

        return " ".join(parts)


def setup_logging(
    level: str = "INFO",
    log_file: Path | None = None,
    enable_colors: bool = True,
    structured: bool = False,
) -> None:
    """
    Configure logging for OnRamp scripts.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to write logs to file
        enable_colors: Enable colored output in console (if colorama available)
        structured: Use structured logging format (key=value pairs)
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    if structured:
        console_formatter = StructuredFormatter(
            fmt="%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    elif enable_colors and COLORS_AVAILABLE:
        console_formatter = ColoredFormatter(
            fmt="%(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        console_formatter = logging.Formatter(
            fmt="%(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)

        # File logs are always structured
        file_formatter = StructuredFormatter(
            fmt="%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LogContext:
    """
    Context manager for adding structured fields to log records.

    Example:
        with LogContext(service="adguard", operation="scaffold"):
            logger.info("Starting operation")  # Includes service and operation fields
    """

    def __init__(self, **fields: Any):
        self.fields = fields
        self.old_factory = None

    def __enter__(self):
        """Add fields to all log records in this context."""
        self.old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.fields.items():
                setattr(record, key, value)
            return record

        logging.setLogRecordFactory(record_factory)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore original record factory."""
        if self.old_factory:
            logging.setLogRecordFactory(self.old_factory)


# Convenience function for scripts
def setup_script_logging(
    level: str = "INFO",
    enable_colors: bool = True,
    structured: bool = False,
) -> logging.Logger:
    """
    Quick setup for CLI scripts.

    Args:
        level: Log level
        enable_colors: Enable colored output
        structured: Use structured format

    Returns:
        Logger instance for the calling module
    """
    import inspect

    # Get calling module name
    frame = inspect.currentframe()
    if frame and frame.f_back:
        caller_module = frame.f_back.f_globals.get("__name__", "onramp")
    else:
        caller_module = "onramp"

    setup_logging(level=level, enable_colors=enable_colors, structured=structured)
    return get_logger(caller_module)
