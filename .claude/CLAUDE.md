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

## Adding Services

1. Create `services-available/<name>.yml` with `env_file:` directive:
   ```yaml
   services:
     myservice:
       image: myservice:${MYSERVICE_TAG:-latest}
       env_file:
         - ./services-enabled/myservice.env
   ```
2. (Optional) Create `services-scaffold/<name>/env.template` for custom variables
3. `make enable-service <name>`

## Conventions

- Templates: `*.template` (variable substitution) or `*.static` (copy as-is)
- Env vars: `${VAR:-default}` pattern
- Service YAMLs: Include `env_file:` directive pointing to `./services-enabled/<service>.env`
- Services with databases: Use dedicated containers (e.g., `db` or `<service>-db`)
- NFS overrides: `overrides-available/<service>-nfs.yml` pattern, fall back to shared global paths (`NFS_MEDIA_PATH`, `NFS_DOWNLOADS_PATH`), never add service-specific paths to the global `.env.nfs.template`

## How Environment Variables Work

OnRamp uses two mechanisms for environment variables:

1. **Makefile `--env-file` flags**: Loads ALL env files for YAML variable substitution
   - Enables `${VAR}` in container_name, labels, volumes, etc.
   - Runs at docker-compose parse time

2. **YAML `env_file:` directive**: Each service declares its env file
   - Provides variables inside the running container
   - Self-documenting (shows which file the service uses)

## Generated Files (Do Not Edit Directly)

- `SERVICES.md` - Generated by `.githooks/generate-services-markdown.sh`
  - To fix: Edit the generator script or service YAML `# description:` comments
  - Regenerate: Run the script or commit (pre-commit hook)

## Environment File Precedence

1. Service-specific: `services-enabled/<service>.env`
2. Global overrides: `services-enabled/.env.nfs`, `.env.external`
3. Main config: `services-enabled/.env`

## Resources

For detailed documentation:
- **Scaffolding**: `.github/shared/scaffold-templates.md`
- **Makefiles**: `.github/shared/makefile-modules.md`
- **Sietch Scripts**: `.github/shared/sietch-scripts.md`
- **Troubleshooting**: `.github/shared/troubleshooting.md`
- **NFS Architecture**: `.github/shared/nfs-architecture.md`
- **User Docs**: `docs/` directory

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
