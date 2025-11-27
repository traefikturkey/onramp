# Scaffolding: Convention Over Configuration

OnRamp uses a convention-based scaffolding system to automatically generate service configurations. Instead of writing custom scripts for each service, you simply drop template files in the right place and the system handles the rest.

## How It Works

When you run `make enable-service <name>`, OnRamp:

1. Creates a symlink in `services-enabled/`
2. Looks for templates in `services-scaffold/<name>/`
3. Processes any `*.template` or `*.static` files it finds
4. Outputs the results to `services-enabled/` or `etc/<name>/`

## File Conventions

| File Pattern | Action | Output Location |
|--------------|--------|-----------------|
| `env.template` | Render with envsubst | `services-enabled/<service>.env` |
| `*.yaml.template` | Render with envsubst | `etc/<service>/*.yaml` |
| `*.yml.template` | Render with envsubst | `etc/<service>/*.yml` |
| `*.conf.template` | Render with envsubst | `etc/<service>/*.conf` |
| `*.static` | Copy without modification | `etc/<service>/*` |
| `subdir/*.template` | Render, preserve structure | `etc/<service>/subdir/*` |

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
└── AdGuardHome.yaml.template
```

**Result:**
- `services-enabled/adguard.env`
- `etc/adguard/AdGuardHome.yaml`

### Service with Nested Structure

```
services-scaffold/prometheus/
├── env.template
├── prometheus.yml.template
└── targets/
    └── docker_host.json.static
```

**Result:**
- `services-enabled/prometheus.env`
- `etc/prometheus/prometheus.yml`
- `etc/prometheus/targets/docker_host.json`

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

3. Add config templates if needed:
   ```bash
   # services-scaffold/myservice/config.yaml.template
   server:
     port: ${MYSERVICE_PORT}
   ```

4. Test it:
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
