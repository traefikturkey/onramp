# Semaphore UI - Ansible/Terraform UI

Web-based UI for Ansible and Terraform/OpenTofu/Terragrunt.

## Quick Start

1. Enable the service:
   ```bash
   make enable-service semaphore
   ```

2. **IMPORTANT:** Due to MariaDB migration issues, enable the dedicated MySQL override:
   ```bash
   make enable-override semaphore-dedicated-mysql
   make restart-service semaphore
   ```

3. Access at `https://semaphore.${HOST_DOMAIN}` with default credentials:
   - Username: `admin@localhost`
   - Password: `changeme` (change immediately!)

## Known Issues

### MariaDB Migration Error (v2.7.8)

Semaphore has a known upstream bug with MariaDB migrations. The migration v2.7.8 attempts to drop a foreign key named `project__inventory_ibfk_2`, but MariaDB creates foreign keys with different names (e.g., `1`, `2`, `3`).

**Error:**
```
Error 1091 (42000): Can't DROP FOREIGN KEY `project__inventory_ibfk_2`; check that it exists
```

This issue persists across all tested versions (v2.10.32, v2.10.43, and latest).

### Current Solution

The service is pre-configured with the dedicated MySQL override which avoids these compatibility issues entirely. The dedicated MySQL 8.0 container has better compatibility with Semaphore's migration system.

#### Option 2: Manual Migration Fix

If you prefer to use shared MariaDB, manually mark problematic migrations as complete:

```bash
# Connect to MariaDB
docker exec -it mariadb bash -c "MYSQL_PWD=\$MYSQL_ROOT_PASSWORD mariadb -u root semaphore"

# Insert migration records to skip problematic migrations
INSERT INTO migrations (version, upgraded_date) VALUES ('2.7.8', NOW());
INSERT INTO migrations (version, upgraded_date) VALUES ('2.10.24', NOW());  # May also fail
exit

# Restart semaphore
make restart-service semaphore
```

#### Option 3: Use PostgreSQL

Use the PostgreSQL override instead:

```bash
make enable-override semaphore-pg
make restart-service semaphore
```

Note: This creates a dedicated PostgreSQL container for semaphore.

## Version Pinning

The service is pinned to `v2.10.43` to avoid unstable `latest` tag. You can override this in `services-enabled/semaphore.env`:

```bash
SEMAPHORE_DOCKER_TAG=v2.10.43
```

## References

- [Semaphore Issue #857 - Migration Error From 2.8.33 to 2.8.45](https://github.com/semaphoreui/semaphore/issues/857)
- [Semaphore Issue #215 - Database migration failed](https://github.com/ansible-semaphore/semaphore/issues/215)
- [Semaphore Issue #116 - Setup fails during migrations](https://github.com/ansible-semaphore/semaphore/issues/116)
