"""Tests for logging configuration module."""

import logging
from pathlib import Path
from io import StringIO
import sys

import pytest

from scripts.logging_config import (
    setup_logging,
    get_logger,
    LogContext,
    ColoredFormatter,
    StructuredFormatter,
)


def test_get_logger():
    """Test logger creation."""
    logger = get_logger("test.module")
    assert logger.name == "test.module"
    assert isinstance(logger, logging.Logger)


def test_setup_logging_basic():
    """Test basic logging setup."""
    setup_logging(level="DEBUG")
    logger = get_logger("test")

    # Check level is set
    assert logging.getLogger().level == logging.DEBUG


def test_setup_logging_with_file(tmp_path):
    """Test logging to file."""
    log_file = tmp_path / "test.log"

    setup_logging(level="INFO", log_file=log_file)
    logger = get_logger("test")

    logger.info("Test message")

    # Check file was created and contains message
    assert log_file.exists()
    content = log_file.read_text()
    assert "Test message" in content


def test_structured_formatter():
    """Test structured log formatting."""
    formatter = StructuredFormatter(
        fmt="%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Create a log record
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    # Add extra fields
    record.service = "test-service"
    record.operation = "test-op"

    formatted = formatter.format(record)

    # Check key=value pairs are present
    assert "level=INFO" in formatted
    assert "message=Test message" in formatted
    assert "service=test-service" in formatted
    assert "operation=test-op" in formatted


def test_log_context():
    """Test LogContext manager adds fields to log records."""
    # Setup logging to capture output
    setup_logging(level="INFO", structured=True)
    logger = get_logger("test.context")

    # Capture log output
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(StructuredFormatter(fmt="%(message)s"))
    logging.getLogger().addHandler(handler)

    # Use context manager
    with LogContext(service="adguard", operation="test"):
        logger.info("Test message")

    output = stream.getvalue()

    # Check context fields are present
    assert "service=adguard" in output
    assert "operation=test" in output

    # Remove handler
    logging.getLogger().removeHandler(handler)


def test_log_levels():
    """Test different log levels work correctly."""
    setup_logging(level="DEBUG")
    logger = get_logger("test.levels")

    # Capture log output
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(handler)

    # Log at different levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    output = stream.getvalue()

    # Check all levels are present
    assert "Debug message" in output
    assert "Info message" in output
    assert "Warning message" in output
    assert "Error message" in output

    # Remove handler
    logging.getLogger().removeHandler(handler)


def test_exc_info_logging():
    """Test exception logging includes traceback."""
    setup_logging(level="DEBUG")
    logger = get_logger("test.exceptions")

    # Capture log output
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logging.getLogger().addHandler(handler)

    # Log an exception
    try:
        raise ValueError("Test exception")
    except ValueError as e:
        logger.error("Operation failed", exc_info=True)

    output = stream.getvalue()

    # Check exception info is present
    assert "ValueError: Test exception" in output
    assert "Traceback" in output

    # Remove handler
    logging.getLogger().removeHandler(handler)


def test_colored_formatter_no_color():
    """Test colored formatter works without colorama."""
    formatter = ColoredFormatter(fmt="%(levelname)s: %(message)s")

    record = logging.LogRecord(
        name="test",
        level=logging.ERROR,
        pathname="test.py",
        lineno=10,
        msg="Error message",
        args=(),
        exc_info=None,
    )

    formatted = formatter.format(record)

    # Check message is present (color codes may or may not be present)
    assert "Error message" in formatted
    assert "ERROR" in formatted


def test_log_filtering():
    """Test that log level filtering works."""
    setup_logging(level="WARNING")
    logger = get_logger("test.filter")

    # Capture log output
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logging.getLogger().addHandler(handler)

    # Log at different levels
    logger.debug("Debug message")  # Should be filtered
    logger.info("Info message")    # Should be filtered
    logger.warning("Warning message")  # Should appear
    logger.error("Error message")      # Should appear

    output = stream.getvalue()

    # Check filtering worked
    assert "Debug message" not in output
    assert "Info message" not in output
    assert "Warning message" in output
    assert "Error message" in output

    # Remove handler
    logging.getLogger().removeHandler(handler)


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging configuration after each test."""
    yield
    # Remove all handlers
    logger = logging.getLogger()
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    # Reset level
    logger.setLevel(logging.WARNING)
