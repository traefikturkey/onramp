# Sietch IoC/Dependency Injection Refactoring

## Branch

```
feature/sietch-ioc-refactor
```

Located in worktree: `../onramp-sietch-ioc`

## What We Did

Refactored 5 sietch scripts to use Inversion of Control (IoC) / Dependency Injection (DI) patterns, making them testable without requiring real external dependencies (HTTP APIs, Docker, subprocess calls).

### Scripts Refactored

| Script | Dependency Injected | Tests Added |
|--------|---------------------|-------------|
| `cloudflare.py` | `HttpClient` (HTTP requests) | 21 |
| `database.py` | `DockerExecutor` (docker exec) | 27 |
| `backup.py` | `CommandExecutor` (subprocess/sudo) | 32 |
| `operations.py` | `CommandExecutor` (openssl, wget, chmod, chown) | 14 |
| `scaffold.py` | `CommandExecutor` (envsubst) | 20 |

### New Infrastructure Created

```
scripts/
├── ports/                    # Protocol definitions (interfaces)
│   ├── __init__.py
│   ├── http.py              # HttpClient protocol
│   ├── command.py           # CommandExecutor protocol + CommandResult
│   └── docker.py            # DockerExecutor protocol
├── adapters/                 # Real implementations
│   ├── __init__.py
│   ├── urllib_http.py       # UrllibHttpClient
│   ├── subprocess_cmd.py    # SubprocessCommandExecutor
│   └── docker_subprocess.py # SubprocessDockerExecutor

tests/
├── mocks/                    # Mock implementations for testing
│   ├── __init__.py
│   ├── http.py              # MockHttpClient
│   ├── command.py           # MockCommandExecutor
│   └── docker.py            # MockDockerExecutor
```

## Why We Did It

### The Problem

Before this refactoring, several scripts had **0% test coverage** because they:
- Made direct HTTP calls to Cloudflare API (`urllib.request`)
- Executed `docker exec` commands via subprocess
- Ran system commands via `subprocess.run()` (tar, mount, openssl, etc.)

These couldn't be unit tested without:
- Live API credentials
- Running Docker containers
- Root/sudo access
- Actual filesystem operations

### The Solution

By injecting dependencies through constructor parameters, we can:
- Pass mock implementations during testing
- Pass real implementations in production
- Test business logic in isolation
- Achieve fast, reliable, repeatable tests

### Coverage Improvement

| Script | Before | After |
|--------|--------|-------|
| `cloudflare.py` | 0% | 55% |
| `database.py` | 0% | 66% |
| `backup.py` | 0% | 58% |
| `operations.py` | ~25% | 82% |
| `scaffold.py` | ~30% | 56% |
| **Overall** | ~25% | **54%** |

## How We Did It

### Pattern Used

Constructor injection with optional parameters (backward compatible):

```python
class CloudflareAPI:
    def __init__(
        self,
        api_token: str | None = None,
        domain: str | None = None,
        http_client: "HttpClient | None" = None,  # NEW: injectable
    ):
        # ... existing init code ...

        # Use injected client or create default
        if http_client is not None:
            self._http = http_client
        else:
            from adapters.urllib_http import UrllibHttpClient
            self._http = UrllibHttpClient()
```

### Protocol Definitions

Using Python's `typing.Protocol` for structural typing:

```python
class HttpClient(Protocol):
    def request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        data: bytes | None = None,
        timeout: float = 30,
    ) -> tuple[int, bytes]: ...
```

### Mock Implementations

Mocks that record calls and return preconfigured responses:

```python
class MockHttpClient:
    def __init__(self):
        self.responses: dict[str, tuple[int, bytes]] = {}
        self.calls: list[dict] = []

    def set_response(self, url_pattern: str, status: int, body: bytes):
        self.responses[url_pattern] = (status, body)

    def request(self, method, url, headers=None, data=None, timeout=30):
        self.calls.append({"method": method, "url": url, ...})
        # Return matching response
```

## Testing the Changes

### 1. Switch to the feature branch

```bash
cd /path/to/onramp
git fetch origin
git checkout feature/sietch-ioc-refactor

# Or use the worktree if available:
cd ../onramp-sietch-ioc
```

### 2. Run the test suite

```bash
cd sietch
uv run pytest
```

Expected: **232 passed, 2 skipped**

### 3. Run with coverage

```bash
uv run pytest --cov=scripts --cov-report=term-missing
```

Expected: **54% overall coverage**

### 4. Build Docker image

```bash
cd ..  # back to onramp root
docker build -t sietch-test:ioc sietch/
```

### 5. Verify imports work in container

```bash
docker run --rm sietch-test:ioc python -c "
import sys
sys.path.insert(0, '/scripts')
from cloudflare import CloudflareAPI
from database import DatabaseManager
from backup import BackupManager
from scaffold import Scaffolder
from operations import OperationContext
print('All imports OK')
"
```

### 6. Manual Smoke Tests

Test that the refactored scripts still work in the real environment:

#### Test scaffold build
```bash
# In the sietch container or with proper mounts
make scaffold-build <some-service>
```

#### Test backup creation
```bash
make create-backup
```

#### Test database operations (if MariaDB running)
```bash
docker exec -it sietch python /scripts/database.py list-databases
```

#### Test cloudflare (requires API token)
```bash
docker exec -it sietch python /scripts/cloudflare.py list-records
```

### 7. Verify backward compatibility

The refactored scripts should work exactly as before when called without injecting dependencies - they create their own real implementations automatically.

## Key Changes to Review

1. **Constructor signatures** - All modified classes now accept optional dependency parameters
2. **Import structure** - New `ports/` and `adapters/` directories
3. **Test infrastructure** - New `tests/mocks/` directory
4. **pytest.ini** - Updated to ignore incomplete `tests/core/` and `tests/api/` directories

## Files Modified

### Scripts (production code)
- `scripts/cloudflare.py`
- `scripts/database.py`
- `scripts/backup.py`
- `scripts/operations.py`
- `scripts/scaffold.py`

### New files
- `scripts/ports/*.py` (4 files)
- `scripts/adapters/*.py` (4 files)
- `tests/mocks/*.py` (4 files)
- `tests/test_cloudflare.py`
- `tests/test_database.py`
- `tests/test_backup.py`
- `tests/test_operations.py` (extended)
- `tests/test_scaffold.py` (extended)

### Config
- `pytest.ini` - Added `--ignore` for incomplete test directories
