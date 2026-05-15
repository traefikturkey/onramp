# Logging Quick Start Guide

## 5-Minute Setup for New Scripts

### 1. Import and Initialize

```python
from logging_config import get_logger, setup_logging

logger = get_logger(__name__)
```

### 2. Setup in main()

```python
def main():
    setup_logging(level="INFO", enable_colors=True)
    # ... your code
```

### 3. Use Logger

```python
# Information messages
logger.info("Operation started")
logger.info("Processing complete", extra={"count": 42})

# Debug messages (hidden by default)
logger.debug("Detailed diagnostics", extra={"path": str(path)})

# Warnings (recoverable issues)
logger.warning("Deprecated feature used", extra={"feature": "old_api"})

# Errors (operation failed)
logger.error("Failed to connect", extra={"host": hostname})

# Critical (system failure)
logger.critical("Database unreachable", extra={"timeout": 30})
```

### 4. Exception Handling

```python
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    # exc_info=True includes full traceback
```

## Common Patterns

### Pattern 1: File Operations

```python
# Before
print(f"Created file: {path}")

# After
logger.info("Created file", extra={"path": str(path)})
```

### Pattern 2: Skipped Operations

```python
# Before
if exists:
    print(f"Skipped (exists): {path}")
    return

# After
if exists:
    logger.debug("Skipped existing file", extra={"path": str(path)})
    return
```

### Pattern 3: Progress Messages

```python
# Before
print(f"Processing {i}/{total}...")

# After
logger.info("Processing item", extra={"current": i, "total": total})
```

### Pattern 4: Error Recovery

```python
# Before
try:
    operation()
except PermissionError:
    print("Warning: Permission denied (may be expected)")
    return True

# After
try:
    operation()
except PermissionError as e:
    logger.warning("Permission denied (may be expected)", exc_info=False)
    return True
```

### Pattern 5: Context-Rich Operations

```python
from logging_config import LogContext

with LogContext(service="adguard", operation="build"):
    logger.info("Starting scaffold")  # Includes service and operation
    do_template_rendering()
    logger.info("Completed scaffold")  # Includes service and operation
```

## When to Use Each Level

| Level | When | Example |
|-------|------|---------|
| DEBUG | Detailed diagnostic info | "Checking if file exists", "Parsing YAML line 42" |
| INFO | Normal successful operations | "Service enabled", "Backup completed" |
| WARNING | Recoverable issues, deprecations | "Using legacy config format", "Rate limit approaching" |
| ERROR | Operation failed, user action needed | "Cannot write file", "Invalid configuration" |
| CRITICAL | System failure, immediate attention | "Out of disk space", "Cannot connect to Docker" |

## CLI Integration

### Environment Variable Support

Add to your script:

```python
import os

def main():
    level = os.getenv("LOGLEVEL", "INFO")
    structured = os.getenv("STRUCTURED", "false").lower() == "true"
    
    setup_logging(
        level=level,
        enable_colors=not structured,
        structured=structured
    )
```

Users can then control logging:

```bash
# Verbose
LOGLEVEL=DEBUG make enable-service adguard

# Quiet
LOGLEVEL=WARNING make backup

# Machine-readable
STRUCTURED=true make backup > backup.log
```

## Testing

### Mock Logger in Tests

```python
from unittest.mock import patch

def test_my_function():
    with patch('mymodule.logger') as mock_logger:
        result = my_function()
        
        # Assert logging happened
        mock_logger.info.assert_called_once()
        mock_logger.error.assert_not_called()
```

### Check Log Messages

```python
import logging
from logging_config import setup_logging

def test_logging_output():
    setup_logging(level="DEBUG")
    logger = logging.getLogger("mymodule")
    
    with self.assertLogs(logger, level="INFO") as cm:
        logger.info("Test message", extra={"key": "value"})
    
    assert "Test message" in cm.output[0]
```

## Tips & Tricks

### 1. Lazy String Formatting

```python
# Good - only formats if logged
logger.debug("Processing %s", filename)

# Avoid - always formats even if DEBUG is disabled
logger.debug(f"Processing {filename}")
```

### 2. Conditional Expensive Operations

```python
if logger.isEnabledFor(logging.DEBUG):
    expensive_debug_data = compute_expensive_info()
    logger.debug("Debug info", extra={"data": expensive_debug_data})
```

### 3. Rich Context in Loops

```python
from logging_config import LogContext

with LogContext(operation="batch_process", total=len(items)):
    for i, item in enumerate(items):
        logger.debug("Processing item", extra={"index": i, "item": item.name})
```

### 4. Clean Error Messages

```python
# Include enough context to debug
logger.error(
    "Failed to process file",
    extra={
        "file": str(path),
        "size": path.stat().st_size,
        "permissions": oct(path.stat().st_mode),
    },
    exc_info=True  # Include full exception traceback
)
```

## Cheat Sheet

```python
# Setup (once per script)
from logging_config import get_logger, setup_logging
logger = get_logger(__name__)

def main():
    setup_logging(level="INFO", enable_colors=True)

# Usage
logger.debug("...")      # Diagnostics
logger.info("...")       # Normal operations
logger.warning("...")    # Recoverable issues
logger.error("...")      # Failures
logger.critical("...")   # System failures

# With context
logger.info("...", extra={"key": "value"})

# With exceptions
logger.error("...", exc_info=True)

# Bulk context
from logging_config import LogContext
with LogContext(service="x", operation="y"):
    logger.info("...")
```

## Migration Checklist

When converting a file:

- [ ] Add `from logging_config import get_logger` at top
- [ ] Add `logger = get_logger(__name__)` after imports
- [ ] Add `setup_logging()` call in `main()`
- [ ] Replace `print()` with appropriate `logger.*()` calls
- [ ] Extract variables to `extra` dict
- [ ] Add `exc_info=True` to exception logging
- [ ] Test output at DEBUG and INFO levels
- [ ] Review log levels are appropriate
