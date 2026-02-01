---
description: "Checklist for creating or updating service definitions"
applyTo: "services-available/**/*.yml"
---
# Authoring service files in `services-available`

## Required Elements

- Add comment header with `# description:` (single sentence) and upstream URL (`# https://...`)
- Parameterize with `${SERVICE_*}` variables: image tags, container names, hostnames
- Mount configs to `./etc/<service>/` or `./media/<service>/` (relative paths only)
- Include Traefik labels: `websecure` entrypoint, joyride host label, watchtower/autoheal flags
- Verify container port matches `loadbalancer.server.port` in Traefik labels

## Service Metadata (YAML Comments)

Services can declare optional and required dependencies using YAML comment headers:

### Optional Services

Offer related services during `make enable-service`:

```yaml
# optional-service: ollama
# optional-prompt: Enable Ollama for AI document processing?
services:
  paperless-ngx:
    # ...
```

### Optional Groups (Multiple Services)

```yaml
# optional-group: ai-features
# optional-group-prompt: Enable AI features (Ollama + OpenWebUI)?
# optional-group-services: ollama, openwebui
```

### Required Dependencies (depends_on)

Cross-service dependencies in `depends_on` are automatically enabled:

```yaml
services:
  paperless-ngx:
    depends_on:
      - ollama  # If defined in ollama.yml, auto-enabled first
```

## Database Connections

If service has a dedicated database container (e.g., `db` or `<service>-db`):

```yaml
environment:
  # PostgreSQL standard
  - HOST=db
  - USER=${SERVICE_POSTGRES_USER:-service}
  - PASSWORD=${SERVICE_POSTGRES_DB_PW}
```

The service's `env.template` must define these variables.

## Scaffold Requirements

Services needing configuration must have `services-scaffold/<service>/`:
- `env.template` → generates `services-enabled/<service>.env`
- `*.static` files → copied to `etc/<service>/`

Without scaffolding, `make enable-service` only creates the symlink.

## Service Linting

Lint single service with strict mode and auto-fix:
```bash
services.py lint SERVICE --strict --fix
```

Lint all services and show outdated ones:
```bash
services.py lint --all --outdated
```

What linting checks:
- Required labels (traefik.enable, watchtower.enable, autoheal)
- Network configuration (must be on traefik network)
- Volume mount patterns (./etc/ or ./media/ prefixes)
- Metadata comments (description, config_version)
- Port consistency (container port matches loadbalancer.server.port)

## Config Versioning

Services declare their configuration version with a YAML comment:
```yaml
# config_version: 2
services:
  myservice:
    # ...
```

Version meanings:
- v1 (legacy): Older services, may not follow current conventions
- v2 (current): Follows all current standards and conventions

The linter's `--outdated` flag identifies v1 services needing upgrade.

## Archive System

When services are disabled, their .env files are preserved in `services-enabled/archive/`. On re-enable, the scaffolder prompts to restore the archived config:

```
Found archived config for myservice.
Restore previous configuration? [Y/n]
```

This preserves customizations (passwords, settings) across disable/enable cycles.

## Validation

```bash
yamllint services-available/<service>.yml
make enable-service <service>
make start-service <service>
make logs <service>
```

## Common Issues

- **No .env created**: Missing `services-scaffold/<service>/env.template`
- **Can't connect to DB**: Missing HOST/USER/PASSWORD in service environment
- **Traefik not routing**: Wrong port or missing `traefik.enable=true`

## Reference

See [troubleshooting](../shared/troubleshooting.md) for detailed solutions and [scaffold templates](../shared/scaffold-templates.md) for scaffold.yml operations.
