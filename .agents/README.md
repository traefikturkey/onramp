# OnRamp Agent Guide

Docker Compose-based self-hosted homelab. Traefik reverse proxy + Cloudflare DNS-01 SSL.

**Philosophy:** Disaster Recovery over High Availability. Rebuildable in minutes from backups.

## Project Structure

```
services-available/              # Docker Compose service definitions (*.yml)
services-enabled/                # Active symlinks + environment files
  ├── .env                       # Global (HOST_NAME, HOST_DOMAIN, TZ, PUID/PGID)
  ├── .env.nfs                   # NFS mount configuration
  ├── .env.external              # External service URLs
  └── <service>.env              # Per-service environment variables

services-scaffold/               # Templates that generate configs on enable
  ├── onramp/                    # Global .env templates
  └── <service>/                 # Per-service templates
      ├── env.template           # → services-enabled/<service>.env
      ├── *.template             # → etc/<service>/* (variable substitution)
      ├── *.static               # → etc/<service>/* (copied as-is)
      └── scaffold.yml           # Complex operations (keys, downloads)

services-docs/                   # Service documentation (287 services)
  ├── README.md                  # Documentation index
  └── <service>.md               # Per-service docs (config, env vars, overrides)

etc/                             # Generated configs per service (persisted)
media/                           # Service data volumes
backups/                         # Backup archives
  └── environments-enabled.legacy/  # Pre-migration .env backup
overrides-available/             # Optional service extensions (109 overrides)
overrides-enabled/               # Active overrides
sietch/scripts/                  # Python tools (scaffold.py, backup.py, etc.)
make.d/                          # Makefile modules
docs/                            # User documentation
docs/internal/                   # Internal/developer documentation
.github/shared/                  # Detailed architecture docs
```

## Commands

### Services

**Important:** Service name is a positional argument, NOT a `NAME=` variable.
Use `make restart-service onramp-dashboard`, not `make restart-service NAME=onramp-dashboard`.
The Makefile extracts the second word from `MAKECMDGOALS` to build `SERVICE_FLAGS` (compose `-f` flags).
Using `NAME=` silently results in an empty service name and wrong compose behavior.

```bash
make enable-service <name>      # Enable + scaffold
make disable-service <name>     # Disable (keeps etc/ data)
make start-service <name>       # Start container
make stop-service <name>        # Stop container
make restart-service <name>     # Restart container
make logs <name>                # View logs
make nuke-service <name>        # Remove service AND all data
```

### Environment
```bash
make env-wizard               # Interactive setup wizard for required vars
make env-wizard-check         # Check if configuration is complete
make edit-env-onramp          # Edit global .env (HOST_NAME, HOST_DOMAIN)
make edit-env-nfs             # Edit NFS mounts
make edit-env-external        # Edit external service URLs
make edit-env NAME            # Edit service-specific .env
```

### Scaffolding
```bash
make scaffold-build NAME      # Re-run scaffold templates
make scaffold-list            # List services with scaffolds
make scaffold-check NAME      # Validate scaffold exists
```

### Listing
```bash
make list-services            # All available services
make list-enabled             # Currently enabled services
make list-overrides           # Available overrides
make list-external            # External service proxies
make list-games               # Game servers
```

### Additional Operations
```bash
make attach-service NAME      # Exec bash into container
make update-service NAME      # Pull + restart single service
make pull-service NAME        # Pull image only
make check-yaml               # Validate all YAML files
make start-staging            # Use ACME staging certs
make test                     # Run pytest suite
```

## How Scaffolding Works

When you run `make enable-service <name>`:

1. Creates symlink: `services-available/<name>.yml` → `services-enabled/`
2. Looks for `services-scaffold/<name>/` directory
3. Generates `services-enabled/<name>.env`:
   - From `env.template` if present (with variable substitution)
   - Auto-generated minimal file if no template exists
4. Copies `*.template` files to `etc/<name>/` with variable substitution
5. Copies `*.static` files to `etc/<name>/` as-is
6. Executes `scaffold.yml` operations if present

**Every service gets a `.env` file** - this ensures the YAML `env_file:` directive works.

## How Environment Variables Work

OnRamp uses two mechanisms for environment variables:

1. **Makefile `--env-file` flags**: Loads ALL env files for YAML variable substitution
   - Enables `${VAR}` in container_name, labels, volumes, etc.
   - Runs at docker-compose parse time

2. **YAML `env_file:` directive**: Each service declares its env file
   - Provides variables inside the running container
   - Self-documenting (shows which file the service uses)

### Environment File Precedence

1. Service-specific: `services-enabled/<service>.env`
2. Global overrides: `services-enabled/.env.nfs`, `.env.external`
3. Main config: `services-enabled/.env`

## Adding Services

1. Create `services-available/<name>.yml` with `env_file:` directive:
   ```yaml
   # description: Brief service description
   # https://github.com/project/repo
   
   services:
     myservice:
       image: myservice:${MYSERVICE_TAG:-latest}
       env_file:
         - ./services-enabled/myservice.env
       container_name: ${MYSERVICE_CONTAINER_NAME:-myservice}
       restart: ${MYSERVICE_RESTART:-unless-stopped}
       # ... other configuration
   ```

2. (Optional) Create `services-scaffold/<name>/env.template` for custom variables:
   ```bash
   # Service configuration
   MYSERVICE_TAG=latest
   MYSERVICE_CONTAINER_NAME=myservice
   MYSERVICE_RESTART=unless-stopped
   ```

3. Enable and scaffold:
   ```bash
   make enable-service <name>
   ```

4. Service documentation will be automatically generated:
   ```bash
   cd sietch
   uv run python scripts/generate_service_docs.py
   uv run python scripts/update_services_md.py
   ```

## Service Documentation

All 287 services have comprehensive documentation in `services-docs/`:
- Configuration details (Docker images, ports, volumes, networks)
- Environment variables with defaults and descriptions
- Available overrides (NFS storage, GPU acceleration, dedicated databases)
- Quick start guides

**View service documentation:**
```bash
cat services-docs/plex.md          # View Plex documentation
cat services-docs/README.md        # View documentation index
```

**Browse all services:**
- [SERVICES.md](../SERVICES.md) - Quick service list with links
- [services-docs/README.md](../services-docs/README.md) - Documentation index

## Conventions

- **Templates**: `*.template` (variable substitution) or `*.static` (copy as-is)
- **Env vars**: `${VAR:-default}` pattern
- **Service YAMLs**: Include `env_file:` directive pointing to `./services-enabled/<service>.env`
- **Services with databases**: Use dedicated containers (e.g., `db` or `<service>-db`)
- **NFS overrides**: `overrides-available/<service>-nfs.yml` pattern, fall back to shared global paths (`NFS_MEDIA_PATH`, `NFS_DOWNLOADS_PATH`), never add service-specific paths to the global `.env.nfs.template`
- **Logging**: All scripts use structured logging via `logging_config.py` (not print statements)

## Generated Files (Do Not Edit Directly)

- **SERVICES.md** - Generated by `.githooks/generate-services-markdown.sh`
  - To fix: Edit the generator script or service YAML `# description:` comments
  - Regenerate: Run the script or commit (pre-commit hook)

- **services-docs/*.md** - Generated by `sietch/scripts/generate_service_docs.py`
  - Automatically extracts config from service YAMLs, scaffolds, and overrides
  - Regenerate: `cd sietch && uv run python scripts/generate_service_docs.py`

## Guardrails

- Always use `make` commands, never raw `docker compose`
- Do not create files without explicit user request
- Commit all changes when asked (clean `git status`)
- Never mention AI, Claude, or "generated with" in commit messages

### File Move/Rename Checklist
When moving or renaming files, review for:
- Relative paths (volume mounts, imports, includes) that depend on file location
- References in other files (Makefiles, scripts, documentation)
- Glob patterns that may include/exclude differently after the move

### Testing Requirements
After making changes:
- Identify all commands/features affected by the change
- Test each affected command before committing
- For new features: test the new functionality
- For modifications: test both the modified feature AND existing features that share code paths
- Run `make test` to verify unit tests pass

## Troubleshooting

### "cannot open your_server_name" Error

Global `.env` has placeholder values. Fix with:
```bash
make edit-env-onramp
# Change: HOST_NAME=<your_server_name> → HOST_NAME=myserver
# Change: HOST_DOMAIN=<your_domain.com> → HOST_DOMAIN=example.com
```

### No .env Created for Service

The scaffolder should auto-generate a `.env` file even without a template. If missing:
1. Re-run scaffolding: `make scaffold-build <service>`
2. Check services-enabled directory exists
3. For custom variables, create `services-scaffold/<service>/env.template`

### Service Can't Connect to Database

Check service YAML has database connection environment variables:
```yaml
environment:
  - HOST=db
  - USER=${SERVICE_POSTGRES_USER:-service}
  - PASSWORD=${SERVICE_POSTGRES_DB_PW}
```
These must reference variables from the service's `.env` file.

### Finding Original .env Values After Migration

```bash
cat backups/environments-enabled.legacy/.env
```

## Resources

### User Documentation (`docs/`)
- **Getting Started**: `docs/getting-started.md`
- **Commands**: `docs/commands.md`
- **Environment Variables**: `docs/env-vars.md`
- **Scaffolding**: `docs/scaffolding.md`
- **Service Creation**: `docs/service-creation.md`
- **Overrides**: `docs/overrides.md`
- **External Services**: `docs/external-services.md`
- **Troubleshooting**: `docs/troubleshooting.md`
- **Dashboard**: `docs/dashboard.md`
- **Fix Env Deletion**: `docs/fix-env-deletion.md`
- **Migration (legacy env)**: `docs/migration-from-legacy-env.md`
- **Migration (feature branch)**: `docs/migration-from-feature-branch.md`

### Architecture Documentation (`.github/shared/`)
- **Scaffold Templates**: `.github/shared/scaffold-templates.md`
- **Makefile Modules**: `.github/shared/makefile-modules.md`
- **Sietch Scripts**: `.github/shared/sietch-scripts.md`
- **Troubleshooting (extended)**: `.github/shared/troubleshooting.md`
- **NFS Architecture**: `.github/shared/nfs-architecture.md`
- **Database Architecture**: `.github/shared/database-architecture.md`
- **Network Architecture**: `.github/shared/network-architecture.md`
- **Backup Strategy**: `.github/shared/backup-strategy.md`
- **Health Check Patterns**: `.github/shared/healthcheck-patterns.md`

### Internal Documentation (`docs/internal/`)
- **Logging Migration**: `docs/internal/logging-migration-complete.md`
- **Service Documentation**: `docs/internal/service-documentation-complete.md`
- **Database Migrations**: Various database consolidation and migration guides
