
# OnRamp Copilot Instructions

## Guardrails
- Do **not** create new files unless the user explicitly requests the file by name or clearly authorizes the creation.
- If the user asks for a new file but does not specify a name, use your best judgment to name the file appropriately.
- If a task appears to require a new file but no explicit approval is given, pause, summarize the need, and ask the user for confirmation.
- When file creation is declined or unclear, offer alternative approaches that reuse existing files whenever possible.
- When the user asks for a commit and push, ensure all modified files are committed and pushed so that `git status` reports a clean working tree when you finish.

## Project Context
OnRamp is a modular, self-hosted homelab infrastructure built on **Docker Compose**, **Traefik**, and **Cloudflare**.
- **Philosophy:** Disaster Recovery (DR) over High Availability (HA). The stack should be rebuildable in minutes from backups.
- **Core Architecture:**
  - **Traefik:** Acts as the central reverse proxy and handles SSL via Cloudflare DNS-01 challenge.
  - **Modular Services:** Services are defined in `services-available/` and activated via symlinks in `services-enabled/`.
  - **Dynamic Composition:** The `Makefile` dynamically constructs the `docker compose` command by aggregating `docker-compose.yml` + all enabled service and override files.
  - **Sietch Container:** Python-based tool container for scaffolding and environment migration (`sietch/`).
  - **Services Scaffold:** Convention-based templates in `services-scaffold/` for generating service configurations.

## Directory Structure

```
onramp/
├── docker-compose.yml
├── Makefile
├── make.d/
│
├── sietch/                       # Tool container
│   ├── Dockerfile
│   ├── .built                    # Build marker (gitignored)
│   └── scripts/
│       ├── scaffold.py           # Build/teardown service configs
│       └── migrate-env.py        # Legacy .env migration
│
├── services-scaffold/            # Templates for service configuration
│   ├── onramp/
│   │   ├── .env.template         → services-enabled/.env
│   │   ├── .env.nfs.template     → services-enabled/.env.nfs
│   │   └── .env.external.template → services-enabled/.env.external
│   ├── adguard/
│   │   ├── env.template          → services-enabled/adguard.env
│   │   └── AdGuardHome.yaml.template → etc/adguard/AdGuardHome.yaml
│   └── prometheus/
│       ├── env.template
│       └── targets/
│           └── docker_host.json.static
│
├── services-available/           # Service definitions
├── services-enabled/             # Symlinks + env files
│   ├── .env                      # Global config (DOMAINNAME, PUID, etc.)
│   ├── .env.nfs                  # NFS-specific globals
│   ├── .env.external             # External service globals
│   ├── adguard.yml               # Symlink
│   ├── adguard.env               # Service config
│   └── ...
│
├── overrides-available/
├── overrides-enabled/
├── etc/                          # Generated configs
│
└── backups/
    └── .env.legacy               # Migrated legacy file
```

## Critical Workflows
**ALWAYS use `make` commands instead of running `docker compose` directly.** The `Makefile` handles the complex file aggregation logic.

### Service Management
- **Enable a Service:** `make enable-service <name>` (Creates symlink in `services-enabled/`, runs scaffold if templates exist)
- **Disable a Service:** `make disable-service <name>` (Removes symlink and env file)
- **Nuke a Service:** `make nuke-service <name>` (Removes symlink, env file, and etc/ directory)
- **Apply Changes:** `make` (Equivalent to `up -d`) or `make restart` (full down/up cycle)
- **View Logs:** `make logs` or `make logs <service_name>`
- **Update Images:** `make update`

### Environment Management
- **Edit Global Config:** `make edit-env-onramp`
- **Edit Service Config:** `make edit-env <service>`
- **Edit NFS Config:** `make edit-env-nfs`
- **Edit External Config:** `make edit-env-external`
- **Edit Custom Vars:** `make edit-env-custom`

### Scaffold Commands
- **Build Service Scaffold:** `make scaffold-build <service>`
- **Build All Scaffolds:** `make scaffold-build-all`
- **List Available Scaffolds:** `make scaffold-list`
- **Check if Service Has Scaffold:** `make scaffold-check <service>`
- **Teardown (preserve etc/):** `make scaffold-teardown <service>`
- **Nuke (remove etc/):** `make scaffold-nuke <service>`

### Sietch Container
- **Build Container:** `make sietch-build` (auto-builds on changes)
- **Force Rebuild:** `make sietch-rebuild`
- **Open Shell:** `make sietch-shell`

### Legacy Migration
- **Dry Run:** `make migrate-env-dry-run`
- **Force Migration:** `make migrate-env-force`

### Overrides (Extensions)
- **Purpose:** Add functionality (e.g., NFS mounts, GPU support) without modifying the base service file.
- **Enable Override:** `make enable-override <name>` (e.g., `make enable-override plex-nfs`)
- **Disable Override:** `make disable-override <name>`

### Backup & Restore
- **Create Backup:** `make create-backup` (Archives config and enabled states)
- **Restore:** `make restore-backup`

## Sietch Container

### Purpose
The Sietch container provides Python-based tooling for:
- **scaffold.py:** Convention-based scaffolding for generating service configurations
- **migrate-env.py:** Migration from legacy monolithic `.env` to modular environment system

### Auto-Build Behavior
- Automatically builds if the image is missing
- Automatically rebuilds if any file in `sietch/` changes
- Build marker: `sietch/.built` (gitignored)

### Scaffold Conventions
| File in `services-scaffold/<service>/` | Action |
|----------------------------------------|--------|
| `*.template` | Render with envsubst → output location |
| `*.static` | Copy without modification |
| Subdirectories mirrored | `conf/*.template` → `etc/<service>/conf/*` |

### Output Mapping
| Template | Output |
|----------|--------|
| `services-scaffold/onramp/.env.template` | `services-enabled/.env` |
| `services-scaffold/onramp/.env.<stub>.template` | `services-enabled/.env.<stub>` |
| `services-scaffold/<service>/env.template` | `services-enabled/<service>.env` |
| `services-scaffold/<service>/<file>.template` | `etc/<service>/<file>` |
| `services-scaffold/<service>/<file>.static` | `etc/<service>/<file>` |

## Codebase Conventions
- **Service Definitions (`services-available/*.yml`):**
  - Use standard Docker Compose YAML syntax.
  - Rely on environment variables for configuration (from `services-enabled/*.env`)
  - Define default values for variables: `${VARIABLE:-default_value}`.
  - **Labels:** Use Traefik labels for routing. Follow the patterns in existing files for `traefik.http.routers.*`.
- **Overrides (`overrides-available/*.yml`):**
  - Should only contain the *changes* (deltas) to the base service.
  - Naming convention: `<service>-<feature>.yml`.
- **Environment Variables:**
  - Global config: `services-enabled/.env`
  - Service-specific: `services-enabled/<service>.env`
  - `PUID`/`PGID` are critical for permission management.
  - `HOSTIP` is dynamically injected by the Makefile.

## Development Guidelines
- **Adding a New Service:**
  1. Create `<service-name>.yml` in `services-available/`.
  2. (Optional) Create scaffold in `services-scaffold/<service-name>/`:
     - `env.template` for service environment variables
     - Additional `*.template` or `*.static` files for configs
  3. Use existing services (e.g., `whoami.yml`, `uptime-kuma.yml`) as templates.
  4. Test by enabling: `make enable-service <service-name>` -> `make up` (foreground logs).
- **Adding Service Scaffolds:**
  1. Create directory: `services-scaffold/<service>/`
  2. Add `env.template` for environment variables
  3. Add other `*.template` files for config files that need variable substitution
  4. Add `*.static` files for configs that should be copied as-is
- **Debugging:**
  - If a service fails, check `make logs <service>`.
  - Verify the generated composition logic by inspecting `DOCKER_COMPOSE_FLAGS` in `Makefile` if needed.

