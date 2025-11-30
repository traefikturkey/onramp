# Sietch Scripts: IoC/DI Pattern

OnRamp uses an Inversion of Control (IoC) / Dependency Injection (DI) pattern for its Python tools in `sietch/scripts/`, enabling testable, modular service scaffolding and lifecycle operations.

## Core Architecture

### OperationContext Dataclass

The `OperationContext` is the central context object injected into all operations:

```python
@dataclass
class OperationContext:
    service: str                           # Service name being operated on
    base_dir: Path                         # Repository root
    scaffold_dir: Path                     # services-scaffold/
    etc_dir: Path                          # etc/
    services_enabled: Path                 # services-enabled/
    command_executor: CommandExecutor = None  # Injected executor (subprocess or mock)
```

Operations call `ctx.resolve_path(path)` to resolve output paths relative to `etc/<service>/`.

### Operation Base Class

All operations inherit from the `Operation` abstract base class:

```python
class Operation(ABC):
    def __init__(self, config: dict, ctx: OperationContext):
        self.config = config
        self.ctx = ctx

    @abstractmethod
    def execute(self) -> bool:
        """Execute operation. Returns True on success."""
        pass

    def should_execute(self) -> bool:
        """Check condition before execution."""
        # Conditional logic here
```

Operations are registered in an `OPERATIONS` registry by type (mkdir, generate_rsa_key, etc.).

## Key Files

| File | Purpose |
|------|---------|
| `operations.py` | Base `Operation` ABC, `OperationContext` dataclass, operation implementations, registry |
| `scaffold.py` | `Scaffolder` class — processes templates, executes manifests, copies files |
| `migrate-env.py` | Legacy `.env` migration utilities |
| `adapters/subprocess_cmd.py` | Default `CommandExecutor` implementation (subprocess wrapper) |
| `ports/command.py` | `CommandExecutor` protocol — allows mock injection for testing |

## Conventions

### Type Hints (Python 3.12+)

All code uses explicit type hints:
- `def resolve_path(self, path: str) -> Path:`
- `config: dict[str, Any]`
- `Optional` types for nullable fields (e.g., `CommandExecutor | None`)

### Dataclasses for Configuration

Configuration is passed via dataclasses (`OperationContext`, operation config dicts) rather than global state or environment variables. This enables:
- Easy testing with injected mock contexts
- Clear parameter passing through call stacks
- IDE autocomplete support

### Context Injection Pattern

All operations receive `OperationContext` as a constructor parameter:

```python
op = MkdirOp(config, ctx)
result = op.execute()
```

The `CommandExecutor` is injected into context, allowing:
- **Production:** Real subprocess execution via `SubprocessCommandExecutor`
- **Testing:** Mock execution via test doubles

## Testing

### Running Tests

```bash
make test
```

Tests use `pytest` with:
- **Fixtures:** Mock `OperationContext` with test directories
- **Mocking:** `CommandExecutor` mocks for subprocess calls
- **No warnings:** Zero-warnings policy enforced

### Test Example

```python
def test_mkdir_creates_directory(temp_ctx):
    """mkdir creates directory with correct permissions."""
    config = {"type": "mkdir", "path": "config/", "mode": "0755"}
    op = MkdirOp(config, temp_ctx)

    assert op.execute() is True
    assert (temp_ctx.etc_dir / "myservice" / "config").exists()
```

## Service Lifecycle Operations

### Available Operation Types (operations.py)

| Type | Config | Behavior |
|------|--------|----------|
| `mkdir` | `path`, `mode` | Create directory with octal permissions |
| `generate_rsa_key` | `output`, `public_key`, `bits`, `skip_if_exists` | Generate RSA keypair via OpenSSL |
| `generate_random` | `output`, `bytes`, `encoding`, `skip_if_exists` | Generate random bytes (base64/hex) |
| `download` | `url`, `output`, `mode`, `skip_if_exists` | Download file from URL via wget |
| `delete` | `path` | Delete file or directory |
| `chown` | `path`, `user`, `group`, `recursive` | Change ownership (warns if fails in container) |
| `chmod` | `path`, `mode`, `recursive` | Change permissions |

All operations support conditional execution via `condition` block (file_exists, file_not_exists, dir_empty, dir_not_empty).

## Common Patterns

### Environment Variable Expansion

Operations call `self.expand_env(value)` to substitute `${VAR}` in config values:

```python
# config: {"user": "${PUID}", "group": "${PGID}"}
user = self.expand_env(self.config.get("user", ""))  # Returns actual UID from env
```

### Path Resolution

All output paths are resolved relative to `etc/<service>/`:

```python
path = ctx.resolve_path("config/app.yml")
# Resolves to: etc/<service>/config/app.yml
```

### Conditional Execution

Operations check conditions before execution:

```yaml
- type: download
  url: https://example.com/setup.sh
  output: scripts/init.sh
  condition:
    type: dir_empty
    path: custom-scripts/
```

Only downloads if `etc/<service>/custom-scripts/` is empty.
