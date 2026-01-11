# Troubleshooting

Common issues and solutions for OnRamp.

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

## Getting More Help

1. Check service-specific documentation in the yml file comments
2. Review the [README](../README.md)
3. Open an issue on GitHub with:
   - Error messages from logs
   - Your Docker version (`docker --version`)
   - Relevant parts of your configuration (redact secrets)
