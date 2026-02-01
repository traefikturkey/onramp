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
| `enable_service.py` | `EnableServiceWizard` class — dependency resolution, optional service prompts, env archive restoration |
| `extract_env.py` | `EnvExtractor` class — scans compose YAML for variables, generates env.template files |
| `healthcheck_audit.py` | Health check auditing — identifies services with autoheal but missing healthcheck |
| `migrate_service_env.py` | Service-specific env migrations — versioned migrations with dry-run support |
| `traefik_hosts.py` | Host extraction from external-enabled YAML, syncs to Joyride DNS hosts |
| `services.py` | Service management CLI — lint, archive/restore env, config versioning |
| `database.py` | PostgreSQL database setup — user/db/grant creation with password generation |
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

## Script Documentation

### enable_service.py

The `EnableServiceWizard` class provides intelligent service enablement with automatic dependency resolution and optional service discovery.

**Key Features:**

- **Automatic Dependency Resolution**: Reads `depends_on` keys from service YAML files and automatically enables required dependencies from other service files
- **Optional Service Prompts**: Parses YAML metadata comments to discover and prompt for optional services:
  - `# optional-service: <name>` — individual optional service
  - `# optional-prompt: <text>` — custom prompt text (defaults to "Enable {service}?")
  - `# optional-group: <group-name>` — grouped optional services
  - `# optional-group-prompt: <text>` — custom group prompt
  - `# optional-group-services: <service1>, <service2>, ...` — comma-separated service list
- **Env File Archive Restoration**: Prompts to restore archived env files from `services-enabled/archive/` when enabling a service
- **Session Tracking**: Uses `enabled_this_session` set to prevent circular dependencies during recursive enablement

**Behavior:**

When enabling a service, the wizard:
1. Checks for required dependencies (cross-file `depends_on` entries)
2. Recursively enables dependencies first (prints "Enabling required dependency: <name>")
3. Prompts for optional services/groups if YAML metadata is present
4. Checks for archived env files and offers restoration
5. Creates service symlink and runs scaffolding

**Usage:**

```python
wizard = EnableServiceWizard(base_dir=Path("/apps/onramp"))
wizard.enable_service("paperless-ngx")
```

### extract_env.py

The `EnvExtractor` class scans Docker Compose YAML files for environment variable usage and generates structured `env.template` files.

**Key Features:**

- **Variable Pattern Matching**: Identifies `${VAR}` and `${VAR:-default}` patterns in YAML
- **Categorization**: Groups variables by type:
  - Docker tags (`_TAG`, `_VERSION`)
  - Hostnames (`_HOST`, `_HOSTNAME`)
  - Passwords/secrets (`_PASSWORD`, `_SECRET`, `_KEY`, `_TOKEN`)
  - General configuration (everything else)
- **Template Generation**: Outputs formatted env.template with:
  - Section headers for each category
  - Default values preserved from `${VAR:-default}` syntax
  - Alphabetical sorting within sections

**Usage:**

```bash
python sietch/scripts/extract_env.py services-available/paperless-ngx.yml
```

Outputs to `services-scaffold/<service>/env.template`.

### healthcheck_audit.py

Audits Docker Compose services for health check configuration mismatches.

**Key Features:**

- **Autoheal Detection**: Identifies services with `autoheal=true` label but no healthcheck defined
- **Coverage Statistics**: Calculates percentage of services with proper health check configuration
- **Multiple Output Formats**: Supports text (human-readable) and JSON (machine-parseable) output

**Usage:**

```bash
# Text output
python sietch/scripts/healthcheck_audit.py services-enabled/

# JSON output
python sietch/scripts/healthcheck_audit.py services-enabled/ --format json
```

**Output:**

```
Services with autoheal but no healthcheck:
  - paperless-ngx (services-enabled/paperless-ngx.yml)
  - immich (services-enabled/immich.yml)

Coverage: 45/50 services (90.0%)
```

### migrate_service_env.py

Service-specific environment variable migration system for evolving configurations.

**Key Features:**

- **Configured Migrations**: Pre-defined migrations in `MIGRATIONS` dict:
  - `samba`: Migrates password variables (v1 → v2)
  - `cloudflare-ddns`: Updates API token format (v1 → v2)
- **Migration Versioning**: Tracks migration state in env file comments
- **Dry-Run Mode**: Preview changes without modifying files (`--dry-run` flag)
- **Idempotent**: Safe to re-run; skips already-migrated files

**Migration Structure:**

```python
MIGRATIONS = {
    "service_name": {
        "description": "What changed",
        "from_version": "v1",
        "to_version": "v2",
        "transform": lambda env: {...}  # Transformation function
    }
}
```

**Usage:**

```bash
# Dry-run (preview only)
python sietch/scripts/migrate_service_env.py samba --dry-run

# Apply migration
python sietch/scripts/migrate_service_env.py samba
```

### traefik_hosts.py

Extracts Traefik `Host()` rules from external service definitions and synchronizes them to Joyride DNS.

**Key Features:**

- **Host Rule Extraction**: Parses Traefik router labels for `Host()` rules
- **DNS Synchronization**: Writes extracted hostnames to Joyride DNS hosts file
- **External Service Support**: Scans `external-enabled/` directory for proxy configurations

**Usage:**

```bash
python sietch/scripts/traefik_hosts.py
```

Reads from `external-enabled/*.yml`, writes to Joyride DNS hosts configuration.

### services.py (Expanded)

Service management CLI with linting, archival, and versioning commands.

**Additional Commands:**

- **`lint`**: Validate service YAML files with optional auto-fix
  - `--fix`: Automatically fix linting issues
  - `--strict`: Treat warnings as errors
  - `--outdated`: Check for outdated image tags
- **`archive-env NAME`**: Archive service env file to `services-enabled/archive/`
- **`restore-env NAME`**: Restore service env file from archive
- **`check-archive NAME`**: Verify if archived env file exists
- **`get-version NAME`**: Get current config version for service
- **`check-version NAME`**: Check if service uses latest config version

**Config Versioning System:**

- **v1 (legacy)**: Variables directly in service YAML or `environments-enabled/<service>/.env`
- **v2 (current)**: Variables in `services-enabled/<service>.env` with `env_file:` directive

**Usage:**

```bash
# Lint all services with auto-fix
python sietch/scripts/services.py lint --fix

# Archive env file before major changes
python sietch/scripts/services.py archive-env paperless-ngx

# Restore after testing
python sietch/scripts/services.py restore-env paperless-ngx

# Check config version
python sietch/scripts/services.py get-version paperless-ngx
```

### database.py (Expanded)

PostgreSQL database setup and management with automatic password generation.

**Key Commands:**

- **`setup NAME`**: Full PostgreSQL user/database/grant creation
  - Generates secure random password if not provided
  - Stores password in `.generated_passwords/<service>.env`
  - Creates database and grants all privileges
  - **Idempotent**: Safe to re-run; skips existing users/databases

**Password Generation:**

- Uses `secrets.token_urlsafe(32)` for cryptographically secure passwords
- Stores in `.generated_passwords/<service>.env` for retrieval
- Format: `SERVICE_POSTGRES_DB_PW=<password>`

**Usage:**

```bash
# Setup database with auto-generated password
python sietch/scripts/database.py setup paperless

# Manual password (not recommended)
python sietch/scripts/database.py setup paperless --password mysecret
```

**Safety Features:**

- Checks for existing users/databases before creation
- Prints clear status messages ("User already exists", "Database created")
- All operations idempotent (safe to re-run)
