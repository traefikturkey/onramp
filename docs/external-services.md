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
# TrueNAS (default HTTPS port, no _PORT needed in YAML)
TRUENAS_HOST_NAME=truenas
TRUENAS_ADDRESS=192.168.1.100

# Proxmox (custom port, hardcoded in YAML)
PROXMOX_HOST_NAME=proxmox
PROXMOX_ADDRESS=192.168.1.50

# Home Assistant (custom port, hardcoded in YAML)
HOMEASSISTANT_HOST_NAME=homeassistant
HOMEASSISTANT_ADDRESS=192.168.1.75
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

2. The generated file opens in your editor. Set the protocol and port for your service:
   ```yaml
   # external-available/myservice.yml
   http:
     routers:
       myservice:
         entryPoints:
           - websecure
         rule: "Host(`{{env "MYSERVICE_HOST_NAME"}}.{{env "HOST_DOMAIN"}}`)"
         middlewares:
           - default-headers
         tls: {}
         service: myservice

     services:
       myservice:
         loadBalancer:
           servers:
             - url: "https://{{env "MYSERVICE_ADDRESS"}}:{{env "MYSERVICE_PORT"}}/"
           passHostHeader: true
   ```

3. Add variables to `.env.external`:
   ```bash
   MYSERVICE_HOST_NAME=myservice
   MYSERVICE_ADDRESS=192.168.1.x
   MYSERVICE_PORT=8080
   ```

4. Enable and restart Traefik:
   ```bash
   make enable-external myservice
   make restart-service traefik
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
   ping ${MYSERVICE_ADDRESS}
   curl https://${MYSERVICE_ADDRESS}:${MYSERVICE_PORT}
   ```

2. Verify variables are set in `.env.external`

3. Check Traefik logs:
   ```bash
   make logs traefik
   ```

### SSL certificate issues

Traefik is configured with `--serverstransport.insecureskipverify=true` so self-signed backend certificates are accepted by default. If you still have issues, check that the protocol in the YAML (`http://` vs `https://`) matches what the backend service expects.
