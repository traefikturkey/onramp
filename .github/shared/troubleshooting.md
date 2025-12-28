# Troubleshooting Guide

Common issues and solutions for OnRamp services.

## Service Enable/Start Failures

### Error: "cannot open your_server_name: No such file"

**Cause:** The global `.env` file contains placeholder values with `<` and `>` characters, which the shell interprets as redirection operators.

**Solution:**
```bash
make edit-env-onramp
```

Find and replace placeholder values:
```bash
# Wrong (causes shell errors):
HOST_NAME=<your_server_name_without_domain>
HOST_DOMAIN=<your_domain.com>

# Correct:
HOST_NAME=myserver
HOST_DOMAIN=example.com
```

**Location:** `services-enabled/.env`

---

### Error: No .env file created for service

**Cause:** The service lacks scaffold templates. When `make enable-service` runs, it only creates a symlink if no `services-scaffold/<service>/` directory exists.

**Diagnosis:**
```bash
ls services-scaffold/<service>/
# If "No such file or directory" → scaffold is missing
```

**Solution:** Create the scaffold directory with at minimum an `env.template`:

```bash
mkdir -p services-scaffold/<service>
```

Create `services-scaffold/<service>/env.template` with required variables:
```bash
###############################################
# <Service> Configuration
###############################################

<SERVICE>_DOCKER_TAG=${<SERVICE>_DOCKER_TAG:-latest}
<SERVICE>_HOST_NAME=${<SERVICE>_HOST_NAME:-<service>}
# Add other required variables...
```

Then rebuild:
```bash
make scaffold-build <service>
```

---

### Error: Service can't connect to database

**Cause:** The service YAML is missing environment variables to connect to its database container.

**Diagnosis:** Check the service's environment section in `services-available/<service>.yml`:
```yaml
environment:
  - HOST=db              # Missing?
  - USER=${..._USER}     # Missing?
  - PASSWORD=${..._PW}   # Missing?
```

**Common patterns by database type:**

PostgreSQL (official Odoo-style):
```yaml
environment:
  - HOST=db
  - USER=${SERVICE_POSTGRES_USER:-service}
  - PASSWORD=${SERVICE_POSTGRES_DB_PW}
```

PostgreSQL (standard):
```yaml
environment:
  - POSTGRES_HOST=db
  - POSTGRES_USER=${SERVICE_DB_USER}
  - POSTGRES_PASSWORD=${SERVICE_DB_PASSWORD}
```

MariaDB:
```yaml
environment:
  - MYSQL_HOST=mariadb
  - MYSQL_USER=${SERVICE_DB_USER}
  - MYSQL_PASSWORD=${SERVICE_DB_PASSWORD}
```

---

### Error: Container starts but service unreachable

**Diagnosis checklist:**

1. **Check Traefik labels in service YAML:**
   ```yaml
   labels:
     - traefik.enable=true
     - traefik.http.routers.<service>.rule=Host(`${HOST_NAME}.${HOST_DOMAIN}`)
     - traefik.http.services.<service>.loadbalancer.server.port=<PORT>
   ```

2. **Verify the port matches what the container exposes:**
   ```bash
   docker logs <container_name>
   # Look for "listening on port XXXX"
   ```

3. **Check container is on traefik network:**
   ```yaml
   networks:
     - traefik
   ```

---

## Configuration Issues

### Finding original .env values after migration

Legacy environment files are backed up during migration:
```bash
ls backups/environments-enabled.legacy/
cat backups/environments-enabled.legacy/.env
```

---

### Which .env file to edit?

| File | Purpose | Command |
|------|---------|---------|
| `services-enabled/.env` | Global: HOST_NAME, HOST_DOMAIN, TZ, PUID/PGID | `make edit-env-onramp` |
| `services-enabled/.env.nfs` | NFS mount paths | `make edit-env-nfs` |
| `services-enabled/.env.external` | External service URLs | `make edit-env-external` |
| `services-enabled/<service>.env` | Service-specific config | `make edit-env <service>` |

---

### Environment variable not taking effect

**Cause:** The `.env` file exists but the variable has wrong syntax or the service needs restart.

**Check syntax:**
```bash
# Correct:
MY_VAR=value
MY_VAR=${OTHER_VAR:-default}

# Wrong (spaces around =):
MY_VAR = value

# Wrong (quotes often unnecessary):
MY_VAR="value"
```

**Restart service:**
```bash
make restart-service <service>
```

---

## Scaffold Issues

### Template variables not substituted

**Cause:** Variable syntax error or variable not exported.

**Check template syntax:**
```bash
# Correct:
${VAR_NAME}
${VAR_NAME:-default}

# Wrong (missing braces):
$VAR_NAME
```

**Variables available during scaffolding:**
- All variables from `services-enabled/.env*` files
- `PUID`, `PGID`, `HOSTIP`, `HOST_NAME`, `HOST_DOMAIN`, `TZ`
- Host environment variables

---

### scaffold.yml operations failing

**Check permissions:** Operations run as PUID:PGID (usually 1000:1000).

**Check paths:** All paths in scaffold.yml are relative to `etc/<service>/`:
```yaml
# This creates: etc/<service>/keys/
- type: mkdir
  path: keys/
```

---

## Database Issues

### MariaDB database not created

Databases are auto-created during scaffold if service YAML has metadata:
```yaml
# database: mariadb
# database_name: myservice
```

Manual creation:
```bash
make mariadb-create-db <database_name>
```

---

### PostgreSQL container unhealthy

**Check logs:**
```bash
docker logs <service>_postgres
```

**Common causes:**
- Volume permissions (data dir not writable)
- Missing environment variables (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`)

---

## Health Check Issues

### Container keeps restarting (unhealthy)

**Diagnosis:**
```bash
docker inspect <container> | grep -A 20 '"Health"'
docker logs <container> --tail 50
```

**Common causes:**
- Health check command references wrong port
- Service takes longer to start than health check timeout
- Missing dependencies (database not ready)

**Fix in service YAML:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 30s
  timeout: 10s
  retries: 5
  start_period: 60s  # Increase for slow-starting services
```

---

## Certificate Issues

### Stuck on staging certificates

**Solution:**
```bash
make down-staging
make clean-acme
make start
```

### Testing with staging certs first

Always test with staging to avoid rate limits:
```bash
make start-staging
# Check logs, verify routing works
make down-staging
make start  # Production certs
```

---

## Environment Precedence

When the same variable is defined in multiple files:

**Order (later wins):**
1. `services-enabled/.env` (global)
2. `services-enabled/.env.nfs` (NFS mounts)
3. `services-enabled/.env.external` (external services)
4. `services-enabled/<service>.env` (service-specific) ← **Highest priority**

**Debugging:**
```bash
# Check which file defines a variable
grep -r "MY_VAR" services-enabled/

# Check final resolved value
docker compose config | grep MY_VAR
```

---

## Quick Diagnostic Commands

```bash
# Check what's enabled
make list-enabled

# Check if scaffold exists
make scaffold-check <service>

# View service logs
make logs <service>

# Check container status
docker ps -a | grep <service>

# Inspect environment being passed
docker inspect <container> | grep -A 50 '"Env"'

# Validate all YAML files
make check-yaml

# View Traefik routing
docker logs traefik 2>&1 | grep <service>
```
