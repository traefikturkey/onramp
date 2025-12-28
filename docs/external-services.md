# External Services

External services allow Traefik to proxy requests to services running outside of Docker (VMs, physical servers, other hosts).

## How It Works

External services are Traefik router configurations that forward traffic to non-Docker endpoints. Unlike regular services, they don't run containers - they just configure routing.

## Directory Structure

```
external-available/     # Available external service definitions
external-enabled/       # Active external services (copied, not symlinked)
```

## Commands

| Command | Description |
|---------|-------------|
| `make list-external` | List available external services |
| `make enable-external NAME` | Enable external service |
| `make disable-external NAME` | Disable external service |
| `make create-external NAME` | Create new external service from template |

## Configuration

External services require configuration in `services-enabled/.env.external`:

```bash
make edit-env-external
```

Example variables:
```bash
# TrueNAS
TRUENAS_HOST=192.168.1.100
TRUENAS_PORT=443

# Proxmox
PROXMOX_HOST=192.168.1.50
PROXMOX_PORT=8006

# Home Assistant
HOMEASSISTANT_HOST=192.168.1.75
HOMEASSISTANT_PORT=8123
```

## Available External Services

Common external services included:

| Service | Description |
|---------|-------------|
| `proxmox` | Proxmox VE hypervisor |
| `truenas` | TrueNAS storage |
| `homeassistant` | Home Assistant |
| `pfsense` | pfSense firewall |
| `opnsense` | OPNsense firewall |
| `synology` | Synology NAS |
| `unifi` | UniFi controller |
| `pihole` | Pi-hole DNS |
| `octoprint` | OctoPrint 3D printer |
| `idrac` | Dell iDRAC |

## Creating a New External Service

1. Create from template:
   ```bash
   make create-external myservice
   ```

2. Edit the generated file to set host/port:
   ```yaml
   # external-available/myservice.yml
   services:
     myservice-external:
       image: traefik/whoami  # Dummy, not used
       labels:
         - traefik.enable=true
         - traefik.http.routers.myservice.rule=Host(`myservice.${HOST_DOMAIN}`)
         - traefik.http.services.myservice.loadbalancer.server.url=http://${MYSERVICE_HOST}:${MYSERVICE_PORT}
   ```

3. Add variables to `.env.external`:
   ```bash
   MYSERVICE_HOST=192.168.1.x
   MYSERVICE_PORT=8080
   ```

4. Enable and restart:
   ```bash
   make enable-external myservice
   make restart
   ```

## Middleware

External services can use middleware for authentication:

- `authelia_middlewares.yml` - Authelia SSO
- `authentik_middleware.yml` - Authentik SSO
- `crowdsec-bouncer.yml` - CrowdSec protection

## Troubleshooting

### External service not accessible

1. Check the host is reachable:
   ```bash
   ping ${MYSERVICE_HOST}
   curl http://${MYSERVICE_HOST}:${MYSERVICE_PORT}
   ```

2. Verify variables are set in `.env.external`

3. Check Traefik logs:
   ```bash
   docker logs traefik 2>&1 | grep myservice
   ```

### SSL certificate issues

For HTTPS backends, you may need to configure `serversTransport`:
```yaml
labels:
  - traefik.http.services.myservice.loadbalancer.server.scheme=https
  - traefik.http.serversTransports.myservice.insecureSkipVerify=true
```
