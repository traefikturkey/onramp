# Logging Framework Migration Guide

## Overview

OnRamp is migrating from `print()` statements to a structured logging framework. This provides:
- **Log levels** (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Structured context** (service name, paths, operations)
- **Color output** in terminals (when colorama is available)
- **File logging** with rotation
- **Better automation support** via structured formats

## Migration Status

### ✅ Completed
- `logging_config.py` - Core logging framework
- `operations.py` - All operations migrated to logging
- `scaffold.py` - Main entry point and key functions migrated

### 🚧 In Progress
- `scaffold.py` - Remaining print statements in Scaffolder class methods
- `services.py` - Service management operations
- `backup.py` - Backup and restore operations

### ⏳ Pending
- Dashboard API endpoints
- Database scripts
- Migration scripts
- Utility scripts

## How to Use the Logging Framework

### Basic Setup

```python
from logging_config import get_logger, setup_logging

logger = get_logger(__name__)

# In main() function:
def main():
    setup_logging(level="INFO", enable_colors=True)
    # ... rest of code
```

### Log Levels

Choose the appropriate level for your message:

| Level | Use For | Example |
|-------|---------|---------|
| `DEBUG` | Detailed diagnostic info, skipped operations | Skipped existing file |
| `INFO` | Normal operations, confirmations | Created directory, Downloaded file |
| `WARNING` | Recoverable issues, deprecations | chown failed (expected in container) |
| `ERROR` | Operation failures that need attention | Failed to create directory |
| `CRITICAL` | System-level failures | Cannot connect to Docker daemon |

### Migration Patterns

#### Simple Messages

```python
# Before
print("Service enabled successfully")

# After
logger.info("Service enabled successfully")
```

#### Messages with Variables

```python
# Before
print(f"Created directory: {path}")

# After
logger.info("Created directory", extra={"path": str(path)})
```

#### Error Messages

```python
# Before
print(f"Error creating directory {path}: {e}")

# After
logger.error(f"Failed to create directory: {e}", 
             extra={"path": str(path)}, 
             exc_info=True)  # Includes traceback
```

#### Conditional Output (Verbose/Debug)

```python
# Before
if verbose:
    print(f"Processing file: {filename}")

# After
logger.debug("Processing file", extra={"filename": filename})
# Control with setup_logging(level="DEBUG")
```

### Structured Context

Use the `extra` parameter to add structured fields to log records:

```python
logger.info(
    "Scaffold operation completed",
    extra={
        "service": "adguard",
        "operation": "build",
        "files_created": 5,
        "duration_ms": 123,
    }
)
```

Output: `INFO: Scaffold operation completed service=adguard operation=build files_created=5 duration_ms=123`

### Context Managers

Use `LogContext` to add fields to all log messages in a block:

```python
from logging_config import LogContext

with LogContext(service="adguard", operation="scaffold"):
    logger.info("Starting operation")  # Includes service and operation
    logger.info("Created directory")   # Includes service and operation
```

## Command-Line Interface

### Log Levels

Users can control verbosity:

```bash
# Default (INFO and above)
make enable-service adguard

# Verbose (DEBUG and above)
make enable-service adguard LOGLEVEL=DEBUG

# Quiet (WARNING and above)
make enable-service adguard LOGLEVEL=WARNING
```

### Structured Output

For automation/parsing:

```bash
make backup STRUCTURED=true
```

Output:
```
timestamp=2026-05-12T10:30:00 level=INFO message="Backup started" operation=backup
timestamp=2026-05-12T10:30:05 level=INFO message="Backup completed" size_mb=150 duration_ms=5000
```

## Migration Checklist

When migrating a file:

1. **Add imports:**
   ```python
   from logging_config import get_logger
   logger = get_logger(__name__)
   ```

2. **Initialize logging in main():**
   ```python
   setup_logging(level="INFO", enable_colors=True)
   ```

3. **Replace print statements:**
   - Determine appropriate log level
   - Extract variables to `extra` dict
   - Add context fields where useful

4. **Update exception handling:**
   ```python
   except Exception as e:
       logger.error(f"Operation failed: {e}", exc_info=True)
   ```

5. **Test the output:**
   - Run the script and verify messages
   - Check log levels are appropriate
   - Ensure structured fields are useful

## Testing

### Unit Tests

Mock the logger in tests:

```python
from unittest.mock import patch

def test_operation(self):
    with patch('operations.logger') as mock_logger:
        result = op.execute()
        mock_logger.info.assert_called_once()
```

### Integration Tests

Check log output:

```python
import logging
from logging_config import setup_logging

def test_logging():
    setup_logging(level="DEBUG")
    logger = logging.getLogger("test")
    
    with self.assertLogs(logger, level="INFO") as cm:
        logger.info("Test message")
    
    assert "Test message" in cm.output[0]
```

## Performance Considerations

- **String formatting:** Use lazy formatting when possible
  ```python
  # Good - only formats if logged
  logger.debug("Processing %s", filename)
  
  # Avoid - always formats
  logger.debug(f"Processing {filename}")
  ```

- **Expensive context:** Use conditionals for heavy operations
  ```python
  if logger.isEnabledFor(logging.DEBUG):
      expensive_data = compute_expensive_debug_info()
      logger.debug("Debug data", extra={"data": expensive_data})
  ```

## Backwards Compatibility

During migration, both systems coexist:
- New code uses logging
- Old code uses print
- No breaking changes to external interfaces

Once migration is complete, we can:
- Add global print() override for debugging
- Redirect stdout to logger
- Remove legacy print statement checks

## Resources

- Python logging docs: https://docs.python.org/3/library/logging.html
- Structured logging best practices: https://www.structlog.org/en/stable/
- `logging_config.py` source code for API reference
