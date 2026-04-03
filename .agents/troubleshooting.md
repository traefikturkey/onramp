# OnRamp Troubleshooting

## "cannot open your_server_name" Error

Global `.env` has placeholder values. Fix with:
```bash
make edit-env-onramp
# Change: HOST_NAME=<your_server_name> → HOST_NAME=myserver
# Change: HOST_DOMAIN=<your_domain.com> → HOST_DOMAIN=example.com
```

## No .env Created for Service

The scaffolder should auto-generate a `.env` file even without a template. If missing:
1. Re-run scaffolding: `make scaffold-build <service>`
2. Check services-enabled directory exists
3. For custom variables, create `services-scaffold/<service>/env.template`

## Service Can't Connect to Database

Check service YAML has database connection environment variables:
```yaml
environment:
  - HOST=db
  - USER=${SERVICE_POSTGRES_USER:-service}
  - PASSWORD=${SERVICE_POSTGRES_DB_PW}
```
These must reference variables from the service's `.env` file.

## Finding Original .env Values After Migration

```bash
cat backups/environments-enabled.legacy/.env
```

## Resources

User documentation (`docs/`):
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

Architecture docs (`.github/shared/`):
- **Scaffold Templates**: `.github/shared/scaffold-templates.md`
- **Makefile Modules**: `.github/shared/makefile-modules.md`
- **Sietch Scripts**: `.github/shared/sietch-scripts.md`
- **Troubleshooting (extended)**: `.github/shared/troubleshooting.md`
- **NFS Architecture**: `.github/shared/nfs-architecture.md`
