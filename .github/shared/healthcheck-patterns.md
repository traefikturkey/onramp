# Health Check Patterns

Standard health check configurations for different service types in OnRamp.

## Why Health Checks Matter

Health checks enable:
- **Autoheal**: Automatically restart unhealthy containers
- **Dependency readiness**: Services wait for dependencies with `condition: service_healthy`
- **Monitoring**: Track container health in dashboards

## Standard Patterns

### HTTP/HTTPS Web Services

For services with a web interface or REST API:

```yaml
healthcheck:
  test: ["CMD", "wget", "--spider", "-q", "http://localhost:8080/"]
  interval: 30s
  timeout: 5s
  retries: 3
  start_period: 30s
```

Alternative with curl:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 30s
  timeout: 5s
  retries: 3
  start_period: 30s
```

**Note:** Many minimal images don't include curl. wget is more common.

### PostgreSQL

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

### MariaDB/MySQL

```yaml
healthcheck:
  test: ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 60s
```

Alternative (older images):
```yaml
healthcheck:
  test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

### Redis/Valkey

```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 10s
```

For Valkey:
```yaml
healthcheck:
  test: ["CMD", "valkey-cli", "ping"]
  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 10s
```

### MongoDB

```yaml
healthcheck:
  test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

### Elasticsearch

```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -s http://localhost:9200/_cluster/health | grep -q '\"status\":\"green\"\\|\"status\":\"yellow\"'"]
  interval: 30s
  timeout: 10s
  retries: 5
  start_period: 60s
```

### TCP Port Check

For services without built-in health endpoints:

```yaml
healthcheck:
  test: ["CMD-SHELL", "nc -z localhost 8080 || exit 1"]
  interval: 30s
  timeout: 5s
  retries: 3
  start_period: 30s
```

### Custom Script

For complex health requirements:

```yaml
healthcheck:
  test: ["CMD", "/healthcheck.sh"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```

## Timing Guidelines

| Parameter | Purpose | Typical Values |
|-----------|---------|----------------|
| `interval` | Time between checks | 10s-60s |
| `timeout` | Max time for check to complete | 5s-30s |
| `retries` | Failures before unhealthy | 3-5 |
| `start_period` | Grace period after start | 10s-120s |

### Service Type Recommendations

| Service Type | interval | timeout | start_period |
|--------------|----------|---------|--------------|
| Fast APIs | 10s | 5s | 10s |
| Web apps | 30s | 5s | 30s |
| Databases | 10s | 5s | 30-60s |
| Heavy apps | 60s | 10s | 120s |

## Using Health Checks with Dependencies

### Service Waits for Database

```yaml
services:
  app:
    depends_on:
      app-db:
        condition: service_healthy

  app-db:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
```

### Chain of Dependencies

```yaml
services:
  app:
    depends_on:
      app-db:
        condition: service_healthy
      app-cache:
        condition: service_healthy

  app-db:
    healthcheck: ...

  app-cache:
    healthcheck: ...
```

## Integration with Autoheal

For autoheal to work, containers need health checks:

```yaml
services:
  myservice:
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:8080/"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 30s
    labels:
      - autoheal=true
```

Without a healthcheck, `autoheal=true` has no effect.

## Audit Tool

Use the healthcheck audit tool to find services without health checks:

```bash
# Audit all services
docker run --rm -v $(pwd):/app sietch python /scripts/healthcheck_audit.py

# Audit enabled services only
docker run --rm -v $(pwd):/app sietch python /scripts/healthcheck_audit.py --enabled-only

# JSON output for scripts
docker run --rm -v $(pwd):/app sietch python /scripts/healthcheck_audit.py --format=json
```

## Common Issues

### Health Check Fails Immediately

**Problem:** Container marked unhealthy right after start.

**Solution:** Increase `start_period`:
```yaml
healthcheck:
  start_period: 60s  # Give more time to initialize
```

### Health Check Times Out

**Problem:** Check takes too long, times out.

**Solution:** Increase `timeout` or use simpler check:
```yaml
healthcheck:
  test: ["CMD", "true"]  # Minimal check
  timeout: 30s
```

### No Health Check Tool Available

**Problem:** Container doesn't have wget, curl, or nc.

**Solutions:**
1. Use the application's native health endpoint
2. Check for a PID file or socket
3. Add health check tool in a custom Dockerfile

```yaml
# Check if process is running
healthcheck:
  test: ["CMD-SHELL", "pgrep myprocess || exit 1"]
```

### Health Check Not Detecting Issues

**Problem:** Service unhealthy but check passes.

**Solution:** Make check more thorough:
```yaml
# Instead of just checking port
healthcheck:
  test: ["CMD", "wget", "-O", "-", "http://localhost:8080/api/health"]
  # Actually validates response, not just connectivity
```
