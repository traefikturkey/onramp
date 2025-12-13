# PostgreSQL Shared Database

This is the shared PostgreSQL instance used by multiple OnRamp services.

## Setup

1. Enable the service:
   ```bash
   make enable-service postgres
   ```

2. Set the password in `services-enabled/.env`:
   ```bash
   PG_PASS=your_secure_password_here
   ```

3. Start the service:
   ```bash
   make restart
   ```

## Database Management

Use the `postgres_manager.py` script for database operations:

```bash
# List all databases
cd sietch/scripts && ./postgres_manager.py list-databases

# Create a new database
cd sietch/scripts && ./postgres_manager.py create-db myservice

# Connect to postgres console
cd sietch/scripts && ./postgres_manager.py console

# Drop a database
cd sietch/scripts && ./postgres_manager.py drop-db myservice
```

## Automatic Database Creation

When you enable a service with postgres metadata:

```yaml
# database: postgres
# database_name: mydb
```

The database will be automatically created during `make enable-service <name>`.

## Services Using This Database

The following services connect to this shared postgres instance:
- authentik
- dockerizalo
- healthchecks
- kaizoku
- kaneo
- mediamanager
- n8n (when using n8n-postgres override)
- nocodb
- tandoor

## Credentials

All services use the shared credentials from the global `.env`:
- **User**: `${PG_USER}` (default: admin)
- **Password**: `${PG_PASS}` (must be set)
- **Host**: `postgres` (container name on traefik network)
- **Port**: `5432`

Services can override these with service-specific variables if needed.

## Backups

Database files are stored in:
```
./media/databases/postgres/data
```

Use the backup scripts to backup all databases:
```bash
./backup.sh
```

## Port Exposure

Port 5432 is exposed for local development/debugging. In production, services connect via the internal traefik network without needing the exposed port.
