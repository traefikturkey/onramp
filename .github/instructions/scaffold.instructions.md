---
applyTo: "services-scaffold/**/*"
---
# Scaffold Templates

Templates in `services-scaffold/<service>/` generate configuration when services are enabled.

## File Types and Output

| File Pattern | Output Location | Processing |
|--------------|-----------------|------------|
| `env.template` | `services-enabled/<service>.env` | Variable substitution |
| `*.template` | `etc/<service>/*` | Variable substitution (suffix stripped) |
| `*.static` | `etc/<service>/*` | Copied as-is (suffix stripped) |
| `scaffold.yml` | N/A | Executes operations (mkdir, keygen, etc.) |

## Creating a New Scaffold

Minimum required for a service that needs environment variables:

```
services-scaffold/<service>/
└── env.template
```

**env.template example:**
```bash
###############################################
# <Service> Configuration
# To regenerate: make scaffold-build <service>
###############################################

<SERVICE>_DOCKER_TAG=${<SERVICE>_DOCKER_TAG:-latest}
<SERVICE>_CONTAINER_NAME=${<SERVICE>_CONTAINER_NAME:-<service>}
<SERVICE>_HOST_NAME=${<SERVICE>_HOST_NAME:-<service>}

# Database (if service has dedicated db container)
<SERVICE>_POSTGRES_DB=${<SERVICE>_POSTGRES_DB:-<service>}
<SERVICE>_POSTGRES_USER=${<SERVICE>_POSTGRES_USER:-<service>}
<SERVICE>_POSTGRES_DB_PW=${<SERVICE>_POSTGRES_DB_PW:-}

# Service toggles
<SERVICE>_TRAEFIK_ENABLED=${<SERVICE>_TRAEFIK_ENABLED:-true}
<SERVICE>_WATCHTOWER_ENABLED=${<SERVICE>_WATCHTOWER_ENABLED:-true}
```

## Variable Syntax

```bash
${VAR}              # Required variable
${VAR:-default}     # Use default if unset
${VAR:?error msg}   # Error if unset
```

**Password auto-generation:** Variables containing `_PASS`, `_PASSWORD`, `_SECRET`, `_KEY`, or `_TOKEN` **without defaults** get auto-generated 32-character random values. Example:

```bash
# Auto-generates if MYSERVICE_DB_PASSWORD is unset:
DB_PASSWORD=${MYSERVICE_DB_PASSWORD}

# Does NOT auto-generate (has default):
DB_PASSWORD=${MYSERVICE_DB_PASSWORD:-changeme}
```

## Troubleshooting

### No .env file created
- Check `services-scaffold/<service>/` exists
- Check `env.template` file exists inside it
- Run `make scaffold-build <service>` to regenerate

### Variables not substituted
- Use `${VAR}` syntax, not `$VAR`
- Check variable is defined in one of:
  - `services-enabled/.env`
  - `services-enabled/.env.nfs`
  - `services-enabled/.env.external`
  - Host environment

### Template not copied to etc/
- Files are no-clobber: existing files in `etc/<service>/` are NOT overwritten
- Delete existing file first if you need to regenerate

## Commands

```bash
make scaffold-list            # List services with scaffolds
make scaffold-check <service> # Verify scaffold exists
make scaffold-build <service> # Run scaffolding manually
```

## Advanced Behaviors

**Force Override**: Use `make scaffold-build-force SERVICE` to bypass etc/ protection and regenerate all scaffold content even if etc/<service>/ already has content.

**Rollback on Failure**: If scaffolding fails, all created files/directories are removed in reverse order. Directories are only removed if empty.

**Auto-Volume Creation**: Scaffolder parses service YAML for `./etc/<service>/*` mounts and pre-creates the targets. Paths ending with `/` or without extensions become directories; paths with extensions become empty files.

**No-Clobber Default**: Existing files in etc/<service>/ are never overwritten during normal scaffolding. This preserves manual edits and container-generated configs.

## Reference

See [shared context](../shared/scaffold-templates.md) for complete scaffold.yml operations and advanced patterns.
