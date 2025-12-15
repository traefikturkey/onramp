# Database Architecture

OnRamp uses **dedicated database containers** for each service that requires a database. This document explains the architecture and provides guidance for service configuration.

## Design Decision: Dedicated vs Shared Databases

### Current Architecture: Dedicated Containers

Each service that requires a database runs its own dedicated container:

```
plex-db          # PostgreSQL for Plex
nextcloud-db     # PostgreSQL for Nextcloud
firefly3-db      # PostgreSQL for Firefly III
gitea-db         # PostgreSQL for Gitea
```

**Benefits:**
- **Isolation**: Database issues don't cascade across services
- **Independent upgrades**: Upgrade one service's database without affecting others
- **Resource control**: Can tune memory/CPU per-service
- **Simpler backups**: Each service's data is self-contained
- **Disaster recovery**: Restore individual services independently

### Legacy: Shared Database Containers

Historically, OnRamp had shared database containers:
- `postgres` - Shared PostgreSQL instance
- `mariadb` - Shared MariaDB instance
- `valkey` - Shared Redis-compatible cache

**These are deprecated.** New services should use dedicated containers.

## Service Configuration Patterns

### PostgreSQL (Dedicated)

```yaml
services:
  myservice:
    image: myservice/image
    depends_on:
      - myservice-db
    environment:
      DATABASE_URL: postgres://myservice:${MYSERVICE_DB_PASS}@myservice-db:5432/myservice

  myservice-db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: myservice
      POSTGRES_PASSWORD: ${MYSERVICE_DB_PASS}
      POSTGRES_DB: myservice
    volumes:
      - myservice-db-data:/var/lib/postgresql/data
    networks:
      - traefik

volumes:
  myservice-db-data:
```

### MariaDB (Dedicated)

```yaml
services:
  myservice:
    image: myservice/image
    depends_on:
      - myservice-db
    environment:
      MYSQL_HOST: myservice-db
      MYSQL_USER: myservice
      MYSQL_PASSWORD: ${MYSERVICE_DB_PASS}
      MYSQL_DATABASE: myservice

  myservice-db:
    image: mariadb:11
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSERVICE_DB_ROOT_PASS}
      MYSQL_USER: myservice
      MYSQL_PASSWORD: ${MYSERVICE_DB_PASS}
      MYSQL_DATABASE: myservice
    volumes:
      - myservice-db-data:/var/lib/mysql
    networks:
      - traefik

volumes:
  myservice-db-data:
```

### Redis/Valkey (Dedicated)

```yaml
services:
  myservice:
    image: myservice/image
    depends_on:
      - myservice-cache
    environment:
      REDIS_URL: redis://myservice-cache:6379

  myservice-cache:
    image: valkey/valkey:8-alpine
    volumes:
      - myservice-cache-data:/data
    networks:
      - traefik

volumes:
  myservice-cache-data:
```

## Database Management

### Interactive Console

For dedicated containers, use docker exec directly:

```bash
# PostgreSQL
docker exec -it myservice-db psql -U myservice

# MariaDB
docker exec -it myservice-db mysql -u myservice -p

# Valkey/Redis
docker exec -it myservice-cache valkey-cli
```

### Database Helpers (Legacy)

The `database.py` script in sietch is designed for shared databases. For dedicated containers, use the `--container` flag:

```bash
# Connect to a specific container
make sietch-run CMD="python /scripts/database.py console --container myservice-db"
```

## Migration Guide: Shared to Dedicated

If migrating an existing service from shared to dedicated database:

1. **Export data** from shared database:
   ```bash
   docker exec postgres pg_dump -U username dbname > backup.sql
   ```

2. **Update service YAML** to use dedicated container pattern (see above)

3. **Enable service** to create new container:
   ```bash
   make restart-service myservice
   ```

4. **Import data** to dedicated container:
   ```bash
   docker exec -i myservice-db psql -U myservice < backup.sql
   ```

5. **Verify** application works correctly

6. **Clean up** old database from shared container (optional)

## Health Checks

Database containers should include health checks:

```yaml
myservice-db:
  image: postgres:16-alpine
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U myservice"]
    interval: 10s
    timeout: 5s
    retries: 5
    start_period: 30s
```

This allows dependent services to wait for database readiness:

```yaml
myservice:
  depends_on:
    myservice-db:
      condition: service_healthy
```

## Backup Strategy

Dedicated containers simplify backups:

```bash
# Backup specific service database
docker exec myservice-db pg_dump -U myservice myservice > myservice-$(date +%Y%m%d).sql

# Backup all PostgreSQL containers
for db in $(docker ps --filter "name=-db" --format "{{.Names}}"); do
  docker exec $db pg_dumpall -U postgres > ${db}-$(date +%Y%m%d).sql
done
```

## Services with Dedicated Databases

Current services using dedicated PostgreSQL:
- authentik, docmost, firefly3, gitea, immich, keycloak, linkwarden
- memos, netbox, nextcloud, nocodb, outline, paperless-ngx-postgres
- semaphore, tandoor, vikunja, wikijs

Current services using dedicated MariaDB:
- bookstack, espocrm, freescout, itflow, joomla, kimai
- matomo, monica, prestashop, snipe-it, wallabag

Current services using dedicated Valkey/Redis:
- authentik, docmost, immich, nextcloud, outline, paperless-ngx
