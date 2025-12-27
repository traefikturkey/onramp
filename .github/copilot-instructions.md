# OnRamp

Docker Compose-based self-hosted homelab. Traefik reverse proxy + Cloudflare DNS-01 SSL.

**Philosophy:** Disaster Recovery over High Availability. Rebuildable in minutes from backups.

## Project Structure

```
services-available/              # Service definitions (*.yml)
services-enabled/                # Active symlinks + *.env files
services-scaffold/<service>/     # Templates → generates env + configs
etc/                             # Generated configs per service
media/                           # Service data volumes
backups/                         # Backup archives + migration backups
sietch/scripts/                  # Python tools
```

## Key Commands

| Task | Command |
|------|---------|
| Enable service | `make enable-service NAME` |
| Start service | `make start-service NAME` |
| View logs | `make logs NAME` |
| Edit global env | `make edit-env-onramp` |
| Edit service env | `make edit-env NAME` |
| Rebuild scaffold | `make scaffold-build NAME` |
| List services | `make list-services` |

## How Scaffolding Works

`make enable-service <name>`:
1. Creates symlink to `services-enabled/`
2. If `services-scaffold/<name>/env.template` exists → generates `services-enabled/<name>.env`
3. Copies templates to `etc/<name>/`

**No scaffold = no .env generated.** Service may fail if it needs config.

## Common Troubleshooting

### "cannot open your_server_name" Error
Global `.env` has placeholder values:
```bash
make edit-env-onramp
# Fix: HOST_NAME=<your_server_name> → HOST_NAME=myserver
```

### No .env Created
Missing scaffold - create `services-scaffold/<service>/env.template`

### Database Connection Failed
Service YAML missing env vars:
```yaml
environment:
  - HOST=db
  - USER=${SERVICE_POSTGRES_USER}
  - PASSWORD=${SERVICE_POSTGRES_DB_PW}
```

### Find Original .env After Migration
```bash
cat backups/environments-enabled.legacy/.env
```

## Copilot Resources

- **Path-scoped**: `.github/instructions/*.instructions.md`
- **Architecture docs**: `.github/shared/*.md`
- **Full context**: `.claude/CLAUDE.md`

## Guardrails

- Always use `make` commands, never raw `docker compose`
- Do not create files without explicit user request
