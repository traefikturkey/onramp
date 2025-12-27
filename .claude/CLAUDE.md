# OnRamp

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

etc/                             # Generated configs per service (persisted)
media/                           # Service data volumes
backups/                         # Backup archives
  └── environments-enabled.legacy/  # Pre-migration .env backup
overrides-available/             # Optional service extensions
overrides-enabled/               # Active overrides
sietch/scripts/                  # Python tools (scaffold.py, backup.py, etc.)
make.d/                          # Makefile modules
.github/shared/                  # Detailed architecture docs
```

## Commands

### Services
```bash
make enable-service NAME      # Enable + scaffold
make disable-service NAME     # Disable (keeps etc/ data)
make start-service NAME       # Start container
make stop-service NAME        # Stop container
make restart-service NAME     # Restart container
make logs NAME                # View logs
make nuke-service NAME        # Remove service AND all data
```

### Environment
```bash
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
```

## How Scaffolding Works

When you run `make enable-service <name>`:

1. Creates symlink: `services-available/<name>.yml` → `services-enabled/`
2. Looks for `services-scaffold/<name>/` directory
3. If `env.template` exists → generates `services-enabled/<name>.env`
4. Copies `*.template` files to `etc/<name>/` with variable substitution
5. Copies `*.static` files to `etc/<name>/` as-is
6. Executes `scaffold.yml` operations if present

**If no scaffold exists**, only the symlink is created. The service may fail if it requires environment variables.

## Troubleshooting

### "cannot open your_server_name" Error
Global `.env` has placeholder values. Fix with:
```bash
make edit-env-onramp
# Change: HOST_NAME=<your_server_name> → HOST_NAME=myserver
# Change: HOST_DOMAIN=<your_domain.com> → HOST_DOMAIN=example.com
```

### No .env Created for Service
Service missing scaffold templates:
1. Check if `services-scaffold/<service>/` exists
2. If not, create `services-scaffold/<service>/env.template`
3. Run `make scaffold-build <service>`

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

## Adding Services

1. Create `services-available/<name>.yml`
2. Create `services-scaffold/<name>/env.template` (required if service needs config)
3. `make enable-service <name>`

## Conventions

- Templates: `*.template` (variable substitution) or `*.static` (copy as-is)
- Env vars: `${VAR:-default}` pattern
- Services with databases: Use dedicated containers (e.g., `db` or `<service>-db`)

## Guardrails

- Always use `make` commands, never raw `docker compose`
- Do not create files without explicit user request
- Commit all changes when asked (clean `git status`)
