# Troubleshooting

Common issues and solutions for OnRamp.

## Backup & Restore

### What's Backed Up

| Directory | Contents |
|-----------|----------|
| `etc/` | Service configuration files |
| `services-enabled/` | Enabled service symlinks and env files |
| `overrides-enabled/` | Active override symlinks |
| `external-enabled/` | External service routing definitions |

### Create and restore backups

```bash
make create-backup     # Creates backup in backups/ directory
make restore-backup    # Restore from backup
make create-nfs-backup # Backup to NFS share
```

## Certificate Issues

### "Certificate not valid" or SSL errors

**Cause:** Let's Encrypt rate limits or DNS propagation delays.

**Solutions:**
1. Test with staging first: `make start-staging`
2. Wait for DNS propagation (can take 5-15 minutes)
3. Check Cloudflare API token has correct permissions
4. Verify `CF_API_EMAIL` and `CF_DNS_API_TOKEN` in `.env`

### Stuck on staging certificates

```bash
make down-staging
make clean-acme
make start
```

### Expired certificates (ERR_CERT_DATE_INVALID)

If your browser shows "Your connection is not private" or `NET::ERR_CERT_DATE_INVALID`:

1. **Check Cloudflare credentials are still valid:**
   ```bash
   make check-cf
   ```

2. **Verify Traefik is running and can reach Cloudflare:**
   ```bash
   docker logs traefik 2>&1 | grep -i "acme\|certificate\|error"
   ```

3. **Force certificate renewal by clearing the ACME store:**
   ```bash
   make down
   make clean-acme
   make start
   ```

4. **If the Cloudflare API token expired**, generate a new one at [dash.cloudflare.com/profile/api-tokens](https://dash.cloudflare.com/profile/api-tokens) and update:
   ```bash
   make edit-env-onramp
   # Update CF_DNS_API_TOKEN=your-new-token
   make restart
   ```

## Service Won't Start

### Check service logs

```bash
make logs servicename
# or
docker logs servicename
```

### Service configuration missing

If a service needs configuration files in `etc/`:

```bash
make scaffold-build servicename
```

### Port conflicts

Check if another service is using the same port:
```bash
docker ps
netstat -tlnp | grep :PORT
```

## Traefik Issues

### Dashboard not accessible

1. Verify Traefik is running: `docker ps | grep traefik`
2. Check Traefik logs: `docker logs traefik`
3. Ensure `TRAEFIK_HOST_NAME` is set in `.env`

### Services not routing

1. Check service has correct labels in yml file
2. Verify service is on the `traefik` network
3. Check Traefik dashboard for router/service status

## Docker Issues

### Permission denied errors

```bash
sudo chown -R $USER:$USER ./etc
sudo chown -R $USER:$USER ./services-enabled
```

### Out of disk space

```bash
docker system prune -a
docker volume prune
```

### Container keeps restarting

Check logs for the specific error:
```bash
docker logs --tail 100 containername
```

## Sietch Container Issues

### "Unable to find image 'sietch:latest' locally"

**Cause:** The sietch container is a local-only image that must be built before use. It's commonly lost after running `docker system prune` or `docker image prune -a`.

**Solution:**
```bash
make sietch-build
```

If that still fails (stale marker file):
```bash
rm -f sietch/.built
make sietch-build
```

## Environment Issues

### Variables not loading

1. Ensure `services-enabled/.env` exists
2. Check for syntax errors (no spaces around `=`)
3. Verify service-specific `.env` files exist

### Missing service environment file

```bash
make scaffold-build servicename
```

## Network Issues

### Services can't communicate

Ensure services are on the same Docker network:
```yaml
networks:
  - traefik
```

### DNS resolution inside containers

Check if the container can resolve DNS:
```bash
docker exec containername nslookup google.com
```

## Database Issues

### Database restore: missing data or broken logins

If you restored a `pg_dumpall` dump and the application is missing data or you can't log in:

**Cause:** The application started before the restore and ran its migrations, creating default
rows that collided with your dump data. Rows with conflicting IDs are silently skipped.

**Solution:** Stop the app, drop the database, restore, then start the app. See the full
procedure in [`.github/shared/backup-strategy.md`](../.github/shared/backup-strategy.md#3-restore-databases).

**Password auth failures after cross-version restore:** Re-set the database password:
```bash
docker exec <db-container> psql -U <user> -c "ALTER USER <user> WITH PASSWORD '<password>';"
```

### MariaDB connection refused

```bash
make mariadb-console
```

### Create database for service

Databases are auto-created by scaffolding when you enable a service:
```bash
make enable-service servicename
```

For manual database creation:
```bash
make mariadb-create-db servicename
```

## Root-Owned Files in etc/

Files created by containers running as root can't be modified by the user.

**Solution:**
```bash
# Fix ownership for single service
make fix-etc-ownership SERVICE

# Fix all etc/ directories
make fix-etc-ownership-all
```

This runs `chown -R $PUID:$PGID` on the affected directories.

## Service Migration Issues

When service env variable names change between versions:

```bash
# List available migrations
make migrate-service-list

# Preview what would change
make migrate-service-dry-run SERVICE

# Run migration for specific service
make migrate-service SERVICE

# Run all pending migrations
make migrate-service-all
```

Migrations handle variable renames (e.g., `SAMBA_SHARES` → `SAMBA_SHARES_CONFIG`).

## PHP Container Security Updates

CVE-2026-109618 and CVE-2026-109619 affect the PHP runtime, not just application
code. Upstream fixes were released on October 21, 2026 in PHP 8.2.35, 8.3.36,
8.4.27 and 8.5.12. See the [PHP security advisories](https://github.com/php/php-src/security/advisories).
Pulling an image does not update a running container; recreate the service after
pulling a patched image. Check any `*_DOCKER_TAG` overrides against the patched
runtime, and follow the application's supported upgrade path.

### ITFlow

The default image changed from `lued/itflow` (PHP 8.1.2, built in 2023) to
`itfloworg/itflow`. The replacement's Apache PHP packages were verified at
8.4.27-r0 on October 26, 2026. Its Docker packaging is community-maintained;
see the [upstream Docker repository](https://github.com/itflow-org/itflow-docker).

For an existing installation:

- The host application directory stays `./etc/itflow/www`. It is now mounted at
  `/var/www/localhost/htdocs` instead of `/var/www/html` inside the container.
  Existing application files and `config.php` stay in place. Custom mounts must
  use the new container path too.
- Remove custom `user: "33"` overrides. The image's entrypoint starts as root to
  set ownership for Alpine's `apache` user, then Apache serves the application.
  The image does not use `PUID` or `PGID`.
- Keep your existing database, credentials and `ITFLOW_DB_PASS`. This change does
  not upgrade MariaDB or update application code stored in the bind mount.
  Follow ITFlow's application upgrade instructions if that code is too old for
  PHP 8.4. For a new installation, set `ITFLOW_DB_PASS` explicitly and enter the
  configured database name and username during setup.
- Port 8080, the health check and Traefik routing remain unchanged.

After adjusting custom overrides and checking application compatibility:

```bash
make update-service itflow
make logs itflow
```

### PrestaShop ARM64

The official `prestashop/prestashop` image now publishes ARM64 builds with patched
PHP. The old `prestashop-arm` override selected
`yobasystems/alpine-prestashop`, whose ARM64 image still contained PHP 8.4.15-r0
on October 26, 2026. Disable that override on existing hosts:

```bash
make disable-override prestashop-arm
```

The base service mounts `./etc/prestashop` at `/var/www/html`. The old override
also mounted it at `/usr/html`; use the official image's `/var/www/html` path
for any custom mounts. Review existing store configuration and select a compatible
PrestaShop release with patched PHP rather than blindly upgrading an older store
to the current `latest` release. Then update the service:

```bash
make update-service prestashop
```

### Full-Text RSS (deprecated)

`heussd/fivefilters-full-text-rss:latest` still contains PHP 5.6.40, even in its
October 25, 2026 build. Upstream deliberately retains PHP 5 because newer PHP
versions reportedly cause crashes. Updating application code or pulling `latest`
does not fix these runtime vulnerabilities, and PHP 5.6 has no upstream fix.

The service definition is retained for existing installations but marked as
deprecated. Do not enable it for new deployments or expose it to untrusted
clients. No replacement image is configured. If it is running, stop it until you
can replace it with a maintained solution:

```bash
make stop-service fulltext-rss
make disable-service fulltext-rss
```

These commands do not delete its data. The repository change does not stop or
disable existing installations automatically.

## Cloudflare Configuration

Validate Cloudflare API credentials:
```bash
make check-cf
```

This verifies:
- `CF_API_EMAIL` is set
- `CF_DNS_API_TOKEN` is valid
- Token has correct zone permissions

## Restore Archived Env

When re-enabling a service, you may want the previous configuration:

```bash
# List archived configs
ls services-enabled/archive/

# Restore using Python script
services.py restore-env SERVICE

# Or manually
cp services-enabled/archive/SERVICE.env services-enabled/SERVICE.env
```

The scaffolder automatically prompts to restore archived configs during `make enable-service`.

## Getting More Help

1. Check service-specific documentation in the yml file comments
2. Review the [README](../README.md)
3. Open an issue on GitHub with:
   - Error messages from logs
   - Your Docker version (`docker --version`)
   - Relevant parts of your configuration (redact secrets)
