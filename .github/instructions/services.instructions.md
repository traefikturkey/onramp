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
