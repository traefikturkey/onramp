# OnRamp Architecture

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

## Environment File Precedence

1. Service-specific: `services-enabled/<service>.env`
2. Global overrides: `services-enabled/.env.nfs`, `.env.external`
3. Main config: `services-enabled/.env`
