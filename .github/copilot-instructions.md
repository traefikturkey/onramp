# OnRamp

Docker Compose-based self-hosted homelab with Traefik reverse proxy and Cloudflare DNS-01 SSL.

**Philosophy:** Disaster Recovery over High Availability. Rebuildable in minutes from backups.

## Project Structure

```
services-available/           # Docker Compose service definitions (*.yml)
services-enabled/             # Symlinks to active services + environment files
  ├── .env                    # Global environment (HOST_NAME, HOST_DOMAIN, etc.)
  ├── .env.nfs                # NFS mount configuration
  ├── .env.external           # External service URLs
  └── <service>.env           # Per-service environment variables

services-scaffold/            # Templates that generate configs on enable
  ├── onramp/                 # Global .env templates
  ├── <service>/              # Per-service templates
  │   ├── env.template        # → services-enabled/<service>.env
  │   ├── *.template          # → etc/<service>/* (variable substitution)
  │   ├── *.static            # → etc/<service>/* (copied as-is)
  │   └── scaffold.yml        # Complex operations (keys, downloads)

etc/                          # Generated configs per service (persisted)
media/                        # Service data volumes
overrides-available/          # Optional service extensions
overrides-enabled/            # Active overrides
backups/                      # Backup archives and migration backups
  └── environments-enabled.legacy/  # Pre-migration .env backup

sietch/scripts/               # Python tools (scaffold.py, backup.py, etc.)
make.d/                       # Makefile modules
.github/shared/               # Detailed documentation for AI assistants
```

## Essential Commands

### Service Management
```bash
make enable-service NAME      # Enable service + run scaffolding
make disable-service NAME     # Disable (keeps etc/ data)
make start-service NAME       # Start container
make stop-service NAME        # Stop container
make restart-service NAME     # Restart container
make logs NAME                # View logs
make nuke-service NAME        # Remove service AND all data
```

### Environment Configuration
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

1. Creates symlink: `services-available/<name>.yml` → `services-enabled/<name>.yml`
2. Looks for `services-scaffold/<name>/` directory
3. If `env.template` exists → generates `services-enabled/<name>.env`
4. Copies `*.template` files to `etc/<name>/` with variable substitution
5. Copies `*.static` files to `etc/<name>/` as-is
6. Executes `scaffold.yml` operations if present

**If no scaffold exists**, only the symlink is created. The service may fail to start if it requires environment variables that weren't generated.

## Common Troubleshooting

### "cannot open your_server_name" Error
The global `.env` has placeholder values. Fix with:
```bash
make edit-env-onramp
# Change: HOST_NAME=<your_server_name> → HOST_NAME=myserver
# Change: HOST_DOMAIN=<your_domain.com> → HOST_DOMAIN=example.com
```

### Service Enable Fails / No .env Created
The service is missing scaffold templates:
1. Check if `services-scaffold/<service>/` exists
2. If not, create `services-scaffold/<service>/env.template`
3. Re-run `make scaffold-build <service>`

### Finding Original .env Values After Migration
```bash
cat backups/environments-enabled.legacy/.env
```

### Service Can't Connect to Database
Check if the service YAML has database connection environment variables:
- PostgreSQL: `HOST`, `USER`, `PASSWORD` (or service-specific like `DB_HOST`)
- These must reference variables from the service's `.env` file

## Service YAML Requirements

Every service in `services-available/*.yml` should:
- Use `${SERVICE_*}` environment variables for configurability
- Have a corresponding `services-scaffold/<service>/env.template` if it needs config
- Include Traefik labels for reverse proxy routing
- Mount configs to `./etc/<service>/` not absolute paths

## Guardrails

- Always use `make` commands, never raw `docker compose`
- Do not create files without explicit user request
- Check `git status` before committing
- Reference `.github/shared/*.md` for detailed architecture docs
