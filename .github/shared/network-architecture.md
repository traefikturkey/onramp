# Network Architecture

OnRamp uses Traefik as a reverse proxy with standardized network patterns for service exposure.

## Core Concepts

### The Traefik Network

All services join a single external Docker network named `traefik`:

```yaml
networks:
  traefik:
    external: true
```

This network is created by the traefik service and allows:
- Service-to-service communication by container name
- Traefik to route HTTP/HTTPS traffic to services
- Single point of SSL termination

## Network Patterns

### Pattern 1: Traefik Only (Most Common)

For web applications that only need HTTPS access:

```yaml
networks:
  traefik:
    external: true

services:
  myservice:
    image: myservice/image
    networks:
      - traefik
    labels:
      - traefik.enable=true
      - traefik.http.routers.myservice.entrypoints=websecure
      - traefik.http.routers.myservice.rule=Host(`myservice.${HOST_DOMAIN}`)
      - traefik.http.services.myservice.loadbalancer.server.port=8080
```

**Use when:**
- Service only needs web access
- No special protocol requirements

### Pattern 2: Traefik + Direct Ports

For services requiring both web access and direct protocol access:

```yaml
services:
  adguard:
    networks:
      - traefik
    ports:
      - "53:53/tcp"      # DNS
      - "53:53/udp"      # DNS
      - "67:67/udp"      # DHCP
    labels:
      - traefik.enable=true
      # ... traefik labels for web UI
```

**Use when:**
- Service needs non-HTTP protocols (DNS, SMTP, etc.)
- Clients connect directly (not through reverse proxy)
- Protocol doesn't support proxying (UDP, raw TCP)

### Pattern 3: Internal Networks

For services with multiple components that shouldn't be exposed:

```yaml
networks:
  traefik:
    external: true
  myservice-internal:
    internal: true

services:
  myservice:
    networks:
      - traefik
      - myservice-internal
    labels:
      - traefik.enable=true

  myservice-db:
    networks:
      - myservice-internal  # Only internal, not traefik
```

**Use when:**
- Database containers that shouldn't be web-accessible
- Worker processes that only communicate with main service
- Security-sensitive components

### Pattern 4: Host Network Mode

For services requiring direct host network access:

```yaml
services:
  myservice:
    network_mode: host
    # No networks: section
    # No traefik labels (must use direct port access)
```

**Use when:**
- Service needs to see all network interfaces
- Performance-critical networking (minimal overhead)
- mDNS/Bonjour discovery required
- DHCP server functionality

**Limitations:**
- Cannot use Traefik routing (no container DNS)
- Port conflicts with host
- Less isolation

### Pattern 5: macvlan (Separate IP)

For services needing their own IP address on the LAN:

```yaml
networks:
  macvlan:
    driver: macvlan
    driver_opts:
      parent: eth0
    ipam:
      config:
        - subnet: 192.168.1.0/24
          gateway: 192.168.1.1
          ip_range: 192.168.1.128/25

services:
  pihole:
    networks:
      macvlan:
        ipv4_address: 192.168.1.53
```

**Use when:**
- Service needs dedicated LAN IP
- Running network infrastructure (DNS, DHCP)
- Avoiding port conflicts

## Service-to-Service Communication

### Within Traefik Network

Services can reach each other by container name:

```yaml
services:
  app:
    environment:
      DATABASE_URL: postgres://app-db:5432/app
      REDIS_URL: redis://app-cache:6379

  app-db:
    # ...

  app-cache:
    # ...
```

### Cross-Service Communication

Services in the same traefik network can communicate:

```yaml
# In service A
environment:
  API_URL: http://serviceb:8080  # Direct container access

# For external access, use the public URL
environment:
  CALLBACK_URL: https://servicea.example.com
```

## Traefik Labels Reference

### Basic HTTP Routing

```yaml
labels:
  - traefik.enable=true
  - traefik.http.routers.myservice.entrypoints=websecure
  - traefik.http.routers.myservice.rule=Host(`myservice.${HOST_DOMAIN}`)
  - traefik.http.services.myservice.loadbalancer.server.port=8080
```

### With Security Headers Middleware

```yaml
labels:
  - traefik.http.routers.myservice.middlewares=default-headers@file
```

### Path-Based Routing

```yaml
labels:
  - traefik.http.routers.myservice.rule=Host(`example.com`) && PathPrefix(`/api`)
```

### Multiple Routers (HTTP + WebSocket)

```yaml
labels:
  # Web interface
  - traefik.http.routers.myservice.rule=Host(`myservice.${HOST_DOMAIN}`)
  - traefik.http.routers.myservice.service=myservice-web
  - traefik.http.services.myservice-web.loadbalancer.server.port=8080

  # WebSocket endpoint
  - traefik.http.routers.myservice-ws.rule=Host(`myservice.${HOST_DOMAIN}`) && PathPrefix(`/ws`)
  - traefik.http.routers.myservice-ws.service=myservice-ws
  - traefik.http.services.myservice-ws.loadbalancer.server.port=8081
```

## Port Exposure Guidelines

### When to Expose Ports

| Scenario | Expose Port? | Example |
|----------|--------------|---------|
| Web UI only | No | Gitea web |
| SSH access | Yes | Gitea SSH (22) |
| DNS server | Yes | AdGuard (53) |
| Database | No | PostgreSQL |
| Cache | No | Redis/Valkey |
| SMTP | Yes | Postfix (25, 587) |

### Port Security

```yaml
# Expose to localhost only (for dev/admin)
ports:
  - "127.0.0.1:8080:8080"

# Expose to all interfaces (for network services)
ports:
  - "53:53/udp"

# Bind to specific interface
ports:
  - "192.168.1.10:80:80"
```

## Common Configurations

### Web Application with Database

```yaml
networks:
  traefik:
    external: true

services:
  app:
    networks:
      - traefik
    environment:
      DATABASE_URL: postgres://app-db:5432/app
    labels:
      - traefik.enable=true
      # ...

  app-db:
    networks:
      - traefik  # Same network for container DNS
    # No traefik labels - not web accessible
```

### Multi-Protocol Service

```yaml
services:
  gitea:
    networks:
      - traefik
    ports:
      - "2222:22"  # SSH
    labels:
      - traefik.enable=true
      # Web UI routing
```

## Troubleshooting

### Service Can't Reach Database

1. Check both are on same network
2. Verify container name matches connection string
3. Check database is healthy: `docker ps`

### Traefik Not Routing

1. Verify service has `traefik.enable=true`
2. Check router rule matches expected hostname
3. Verify service port matches container's exposed port
4. Check Traefik logs: `make logs traefik`

### Port Already in Use

```bash
# Find what's using a port
sudo lsof -i :80
sudo netstat -tlnp | grep :80
```
