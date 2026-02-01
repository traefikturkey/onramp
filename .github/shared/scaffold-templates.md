# Scaffold Templates: Convention-Based Configuration

OnRamp uses a convention-based templating system in `services-scaffold/` to automatically generate service configurations. File names and locations determine how they are processed.

## File Conventions

| File Pattern | Processing | Output Location | Notes |
|--------------|-----------|------------------|-------|
| `env.template` | Render with variable substitution | `services-enabled/<service>.env` | Environment variables per service |
| (no template) | Auto-generate minimal .env | `services-enabled/<service>.env` | Ensures YAML `env_file:` works |
| `*.template` | Render with variable substitution | `etc/<service>/*` (suffix stripped) | Config files with variable substitution |
| `scaffold.yml` | Execute operations | N/A | Control file (not copied) |
| `*.static` | Copy as-is | `etc/<service>/*` (suffix stripped) | No variable substitution |
| `*.md` | Ignored | N/A | Documentation (not copied) |
| `.gitkeep` | Ignored | N/A | Git placeholder (not copied) |
| `MESSAGE.txt` | Display after build | N/A | Post-enable instructions (not copied) |
| Other files | Copy as-is | `etc/<service>/*` | Preserve directory structure |

## Service Metadata (YAML Comments)

Services can declare optional dependencies and required dependencies using metadata in YAML comment headers. This enables intelligent enablement workflows.

### Optional Service Metadata

Declare related services that should be offered as optional when enabling this service:

**Individual Optional Service:**
```yaml
# optional-service: ollama
# optional-prompt: Enable Ollama for AI document processing?
services:
  paperless-ngx:
    image: paperless-ngx:latest
```

**Grouped Optional Services (Multiple Services with One Prompt):**
```yaml
# optional-group: ai-features
# optional-group-prompt: Enable AI features (Ollama + OpenWebUI)?
# optional-group-services: ollama, openwebui
services:
  paperless-ngx:
    image: paperless-ngx:latest
```

Metadata syntax:
- `# optional-service: <service-name>` — Declare a single optional service
- `# optional-prompt: <text>` — Custom prompt text (defaults to "Enable {service}?")
- `# optional-group: <group-name>` — Declare a named group of optional services
- `# optional-group-prompt: <text>` — Custom prompt text for the group
- `# optional-group-services: service1, service2` — Comma-separated service names

### Required Dependencies (depends_on)

Services can declare dependencies on other services using Docker Compose `depends_on`. Cross-service dependencies are automatically resolved:

```yaml
services:
  paperless-ngx:
    image: paperless-ngx:latest
    depends_on:
      - ollama          # Dependency from another service file
      - postgresql-db   # Same-file dependency (already enabled together)
```

Behavior:
- Dependencies listed in `depends_on` are resolved during `make enable-service`
- If a dependency is defined in another service file (e.g., `ollama.yml`), it is automatically enabled
- Cross-file dependencies print status: "Enabling required dependency: {service}"
- Same-file dependencies are not re-enabled (they're part of the same enable operation)

### Auto-Generation of .env Files

Services without an `env.template` still get a `.env` file auto-generated. This ensures:
1. The service YAML's `env_file: ./services-enabled/<service>.env` directive always finds its file
2. Users can add variables later without modifying scaffolding
3. Consistent structure across all services

### Global Config (onramp service)

The special `services-scaffold/onramp/` directory holds global environment templates:

```
services-scaffold/onramp/
├── .env.template           → services-enabled/.env
├── .env.nfs.template       → services-enabled/.env.nfs
└── .env.external.template  → services-enabled/.env.external
```

These use dotfile naming (sort to top) and are visually distinct from per-service configs.

## Template Syntax

Templates use POSIX `${VAR}` syntax, compatible with `envsubst`:

```yaml
# config.yml.template
server:
  port: ${SERVICE_PORT}
  host: ${SERVICE_HOST}
  secret: ${SERVICE_SECRET}
```

### Default Values

Default values use shell parameter expansion syntax:

```bash
# .env.template
DOCKER_TAG=${SERVICE_TAG:-latest}
DEBUG=${DEBUG:-false}
TIMEOUT=${TIMEOUT:-30}
```

If `SERVICE_TAG` is unset, uses `latest`. If set, uses the value.

### Password Auto-Generation

Variables containing password-like patterns are automatically generated with secure 32-character random values when:
- The variable is **unset** in the environment
- The variable has **no default value** (uses `${VAR}` not `${VAR:-default}`)

**Detected patterns:**
- `_PASS`, `_PASSWORD`, `_SECRET`, `_KEY`, `_TOKEN`
- `PASS_`, `PASSWORD_`, `SECRET_`, `KEY_`, `TOKEN_`

**Example:**
```bash
# env.template
DB_PASSWORD=${MYSERVICE_DB_PASSWORD}
SECRET_KEY=${MYSERVICE_SECRET_KEY}
API_TOKEN=${MYSERVICE_API_TOKEN}
```

When scaffolded with these variables unset, each gets a unique 32-character alphanumeric password:
```
Generated secure value for MYSERVICE_DB_PASSWORD
Generated secure value for MYSERVICE_SECRET_KEY
Generated secure value for MYSERVICE_API_TOKEN
```

**What doesn't trigger auto-generation:**
- Variables with defaults: `${VAR:-somedefault}` uses the default
- Variables already set in environment
- Non-password variable names (returns empty string)

### Environment Variables

Template variables come from:
1. Host environment (e.g., `${USER}`, `${HOME}`)
2. Makefile-exported variables (e.g., `${PUID}`, `${PGID}`, `${HOSTIP}`)
3. Sourced `.env` files in `services-enabled/`

## scaffold.yml Operations

The `scaffold.yml` manifest file defines complex operations beyond file copies (key generation, downloads, permissions). Operations execute in order.

### Operation Structure

```yaml
version: "1"

operations:
  - type: mkdir
    path: keys/

  - type: generate_rsa_key
    output: keys/jwt-private-key.pem
    public_key: keys/jwt-public-key.pem
    bits: 2048
    skip_if_exists: true
```

### Available Operations

| Operation | Parameters | Behavior |
|-----------|-----------|----------|
| `mkdir` | `path`, `mode` | Create directory (default mode 0755) |
| `touch` | `path`, `skip_if_exists` | Create empty file (default skip_if_exists: true) |
| `generate_rsa_key` | `output`, `public_key`, `bits`, `skip_if_exists` | Generate RSA keypair via OpenSSL |
| `generate_random` | `output`, `bytes`, `encoding`, `skip_if_exists` | Generate random bytes (base64/hex encoding) |
| `download` | `url`, `output`, `mode`, `skip_if_exists` | Download file from URL via wget |
| `delete` | `path` | Delete file or directory |
| `chown` | `path`, `user`, `group`, `recursive` | Change ownership (warns if fails) |
| `chmod` | `path`, `mode`, `recursive` | Change file permissions |

### Conditional Execution

Operations can be conditional:

```yaml
- type: download
  url: https://example.com/script.sh
  output: scripts/init.sh
  condition:
    type: dir_empty
    path: custom-scripts/
```

Condition types:
- `file_exists` — File exists
- `file_not_exists` — File does not exist
- `dir_empty` — Directory is empty (or doesn't exist)
- `dir_not_empty` — Directory contains files

### Path Resolution

All operation paths are resolved relative to `etc/<service>/`:

```yaml
- type: mkdir
  path: config/          # Resolves to: etc/<service>/config/

- type: generate_rsa_key
  output: keys/id_rsa    # Resolves to: etc/<service>/keys/id_rsa
```

### Environment Variable Expansion

Operations expand `${VAR}` in config values:

```yaml
- type: chown
  path: ./
  user: "${PUID}"
  group: "${PGID}"
  recursive: true
```

`${PUID}` and `${PGID}` are substituted from environment.

## Examples

### Simple Service (env only)

```
services-scaffold/myapp/
└── env.template
```

**env.template:**
```bash
MYAPP_PORT=${MYAPP_PORT:-8080}
MYAPP_DEBUG=${DEBUG:-false}
```

**Result:** `services-enabled/myapp.env`

### Service with Config Files

```
services-scaffold/adguard/
├── env.template
└── conf/
    └── AdGuardHome.yaml.template
```

**Result:**
- `services-enabled/adguard.env`
- `etc/adguard/conf/AdGuardHome.yaml`

### Service with Manifest Operations

```
services-scaffold/geopulse/
├── env.template
└── scaffold.yml
```

**scaffold.yml:**
```yaml
version: "1"
operations:
  - type: mkdir
    path: keys/
  - type: generate_rsa_key
    output: keys/jwt-private-key.pem
    public_key: keys/jwt-public-key.pem
    skip_if_exists: true
  - type: generate_random
    output: keys/encryption-key.txt
    bytes: 32
    encoding: base64
    skip_if_exists: true
```

**Result:**
- `services-enabled/geopulse.env`
- `etc/geopulse/keys/jwt-private-key.pem`
- `etc/geopulse/keys/jwt-public-key.pem`
- `etc/geopulse/keys/encryption-key.txt`

## Build and Management

### Commands

```bash
make scaffold-list                  # List services with scaffolding
make scaffold-check <service>       # Check if service has scaffold files
make scaffold-build <service>       # Manually run scaffolding
make scaffold-teardown <service>   # Remove generated files (keeps etc/)
make enable-service <service>       # Enable + scaffold
make disable-service <service>      # Disable (removes .env, keeps etc/)
make nuke-service <service>         # Disable + remove etc/
```

### File Copy Behavior

Files are copied with **no-clobber** — existing files in `etc/<service>/` are not overwritten during re-scaffolding. This allows:
- Manual edits to survive `make scaffold-build`
- Incremental updates without losing customizations

Operations in `scaffold.yml` respect `skip_if_exists` flags for the same reason.

## Full Documentation

For detailed scaffolding documentation, see `docs/scaffolding.md` in the repository.
