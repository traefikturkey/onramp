# Scaffolding: Convention Over Configuration

OnRamp uses a convention-based scaffolding system to automatically generate service configurations. Instead of writing custom scripts for each service, you simply drop template files in the right place and the system handles the rest.

## How It Works

When you run `make enable-service <name>`, OnRamp:

1. Creates a symlink in `services-enabled/`
2. Looks for templates in `services-scaffold/<name>/`
3. Processes any `*.template` files and copies other files
4. Executes `scaffold.yml` manifest operations (if present)
5. Outputs the results to `services-enabled/` or `etc/<name>/`

## File Conventions

| File Pattern | Action | Output Location |
|--------------|--------|-----------------|
| `env.template` | Render with envsubst | `services-enabled/<service>.env` |
| `*.template` | Render with envsubst | `etc/<service>/*` (suffix stripped) |
| `scaffold.yml` | Execute operations | N/A (control file) |
| `MESSAGE.txt` | Display after build | N/A (post-enable instructions) |
| `*.md` | Ignored | N/A (documentation) |
| `.gitkeep` | Ignored | N/A (git placeholder) |
| Everything else | Copy as-is | `etc/<service>/*` |

Files are copied with no-clobber behavior — existing files are not overwritten.

## Global Config (onramp)

The `services-scaffold/onramp/` directory is special — it holds global environment templates:

```
services-scaffold/onramp/
├── .env.template           → services-enabled/.env
├── .env.nfs.template       → services-enabled/.env.nfs
└── .env.external.template  → services-enabled/.env.external
```

These use dotfile naming so they sort to the top of `services-enabled/` and are visually distinct from per-service configs.

## Examples

### Simple Service (env only)

```
services-scaffold/plex/
└── env.template
```

**env.template:**
```bash
PLEX_CLAIM=${PLEX_CLAIM}
PLEX_DOCKER_TAG=${PLEX_DOCKER_TAG:-latest}
```

**Result:** `services-enabled/plex.env`

### Service with Config File

```
services-scaffold/adguard/
├── env.template
└── conf/
    └── AdGuardHome.yaml.template
```

**Result:**
- `services-enabled/adguard.env`
- `etc/adguard/conf/AdGuardHome.yaml`

### Service with Static Files

```
services-scaffold/gatus/
├── env.template
└── config.yaml
```

Files without `.template` suffix are copied as-is (no variable substitution).

**Result:**
- `services-enabled/gatus.env`
- `etc/gatus/config.yaml`

### Service with Nested Structure

```
services-scaffold/prometheus/
├── env.template
├── conf/
│   ├── prometheus.yml
│   └── targets/
│       └── docker_host.json
```

Directory structure is preserved in the output.

**Result:**
- `services-enabled/prometheus.env`
- `etc/prometheus/conf/prometheus.yml`
- `etc/prometheus/conf/targets/docker_host.json`

## Template Syntax

Templates use standard `${VAR}` syntax, compatible with `envsubst`:

```yaml
# prometheus.yml.template
scrape_configs:
  - job_name: 'traefik'
    static_configs:
      - targets: ['${HOSTIP}:8080']
```

Default values use shell syntax:
```bash
DOCKER_TAG=${PLEX_DOCKER_TAG:-latest}
```

## Manifest Operations (scaffold.yml)

For complex operations beyond file copies (key generation, downloads, permissions), use a `scaffold.yml` manifest:

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

| Type | Description | Parameters |
|------|-------------|------------|
| `mkdir` | Create directory | `path`, `mode` |
| `generate_rsa_key` | Generate RSA keypair | `output`, `public_key`, `bits`, `skip_if_exists` |
| `generate_random` | Generate random bytes | `output`, `bytes`, `encoding`, `skip_if_exists` |
| `download` | Download file from URL | `url`, `output`, `mode`, `skip_if_exists` |
| `delete` | Delete file/directory | `path` |
| `chown` | Change ownership | `path`, `user`, `group`, `recursive` |
| `chmod` | Change permissions | `path`, `mode`, `recursive` |

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
- `file_exists` / `file_not_exists`
- `dir_empty` / `dir_not_empty`

### Example: Service with Complex Setup

```
services-scaffold/radarr/
├── extended.conf
└── scaffold.yml
```

**scaffold.yml:**
```yaml
version: "1"

operations:
  - type: mkdir
    path: custom-services.d/

  - type: mkdir
    path: custom-cont-init.d/

  - type: download
    url: https://raw.githubusercontent.com/.../scripts_init.bash
    output: custom-cont-init.d/scripts_init.bash
    condition:
      type: dir_empty
      path: custom-services.d/

  - type: chown
    path: ./
    user: "${PUID}"
    group: "${PGID}"
    recursive: true
```

## Commands

```bash
make scaffold-list              # List services with scaffolding
make scaffold-check <service>   # Check if service has scaffold files
make scaffold-build <service>   # Manually run scaffolding
make scaffold-teardown <service> # Remove generated files (keeps etc/)
```

## Adding Scaffolding to a Service

1. Create the directory:
   ```bash
   mkdir -p services-scaffold/myservice
   ```

2. Add an `env.template` for environment variables:
   ```bash
   # services-scaffold/myservice/env.template
   MYSERVICE_PORT=${MYSERVICE_PORT:-8080}
   MYSERVICE_SECRET=${MYSERVICE_SECRET}
   ```

3. Add config files if needed (with or without `.template` suffix):
   ```yaml
   # services-scaffold/myservice/config.yaml.template
   server:
     port: ${MYSERVICE_PORT}
   ```

4. Add a `scaffold.yml` for complex operations (optional):
   ```yaml
   version: "1"
   operations:
     - type: mkdir
       path: data/
   ```

5. Test it:
   ```bash
   make enable-service myservice
   ```

## Teardown vs Nuke

| Command | Removes symlink | Removes .env | Removes etc/ |
|---------|-----------------|--------------|--------------|
| `make disable-service` | ✅ | ✅ | ❌ |
| `make nuke-service` | ✅ | ✅ | ✅ |

Use `disable-service` when you might re-enable later (preserves config customizations).
Use `nuke-service` for a clean slate.

## Service Metadata (Auto-Dependencies)

Services can declare metadata in YAML comments to automatically enable dependencies during scaffolding. This eliminates the need for manual `depends_on` entries that cross compose files.

### Metadata Format

Add metadata comments at the top of your service YAML (after networks/volumes declarations):

```yaml
networks:
  traefik:
    external: true

# description: My awesome service
# https://github.com/user/service
# database: postgres
# database_name: myservice
# cache: valkey
# cache_db: 5
# requires: gitea, crowdsec

services:
  myservice:
    # ...
```

### Supported Metadata

| Key | Values | Effect |
|-----|--------|--------|
| `database` | `postgres`, `mariadb` | Auto-enables database service, creates database |
| `database_name` | string | Name of database to create (required with `database`) |
| `cache` | `valkey` | Auto-enables Valkey, assigns database number |
| `cache_db` | `0-15` | Preferred Valkey database number (optional) |
| `requires` | comma-separated | Services to auto-enable and start first |

### Database Auto-Creation

When a service declares `# database: postgres` and `# database_name: mydb`:

1. Scaffolding auto-enables postgres if not already enabled
2. Starts postgres container and waits for healthy state
3. Creates the database if it doesn't exist
4. Proceeds with normal scaffolding

Example (docmost.yml):
```yaml
# database: postgres
# database_name: docmost
# cache: valkey
# cache_db: 5
```

### Service Requirements

For services that depend on other OnRamp services (not just databases), use `# requires:`:

```yaml
# description: Data importer for Firefly III
# requires: firefly3
```

When scaffolding this service:
1. Checks if `firefly3` is enabled, enables it if not
2. Runs scaffold for `firefly3` if it has templates
3. Starts `firefly3` and waits for healthy state
4. Proceeds with normal scaffolding

Multiple requirements are comma-separated:
```yaml
# requires: gitea, postgres
```

### Why Not depends_on?

Docker Compose `depends_on` only works within a single compose file. Since OnRamp uses separate compose files per service, cross-service dependencies cause errors like:

```
service "myservice" depends on undefined service "postgres"
```

The metadata system solves this by handling dependencies at scaffold time instead of compose time.

## Post-Enable Messages (MESSAGE.txt)

Some services require manual steps after enabling (API key setup, host configuration, etc.). Add a `MESSAGE.txt` file to display instructions after successful scaffolding:

```
services-scaffold/myservice/
├── env.template
└── MESSAGE.txt
```

**MESSAGE.txt:**
```
After first start, configure authentication:

1. Access the web UI at https://myservice.${HOST_DOMAIN}
2. Create an admin user
3. Generate API keys for integrations
```

The message is displayed after `make enable-service myservice` completes successfully.

## External Services (Traefik Routing)

External services are non-Docker services (like Proxmox, TrueNAS, Home Assistant) that you want to route through Traefik for SSL termination and unified access.

### Directory Structure

```
external-available/      # Templates for external routing (tracked in git)
├── proxmox.yml
├── homeassistant.yml
└── ...

external-enabled/        # Active configs - creates a copy in external-enabled (gitignored)
└── .keep
```

### Commands

```bash
make enable-external proxmox    # Enable routing for external service
make disable-external proxmox   # Disable routing
make create-external myservice  # Create new external service from template
make list-external              # List available external services
```

### How It Works

When you run `make enable-external <name>`:
1. Creates a copy: `external-available/<name>.yml` → `external-enabled/<name>.yml`
2. Traefik's file provider picks up the config automatically

### Creating a New External Service

```bash
make create-external myrouter
```

This creates `external-available/myrouter.yml` from a template and opens it for editing. Configure the hostname and target URL for your external service.
