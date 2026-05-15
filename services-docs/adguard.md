# Adguard

> Network-wide ad blocker and privacy tool

## Links
- [Official Repository](https://github.com/AdguardTeam/AdGuardHome)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/adguard.yml)

## Docker Images
- `adguard/adguardhome:${ADGUARD_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ADGUARD_CONTAINER_NAME` | adguard | Container name |
| `ADGUARD_DOCKER_TAG` | latest | Docker image tag/version |
| `ADGUARD_PASSWORD` | ${ADGUARD_PASSWORD} | Service password |
| `ADGUARD_RESTART` | unless-stopped | Container restart policy |
| `ADGUARD_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `ADGUARD_USER` | admin | Service username |
| `ADGUARD_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `53:53`
- `67:67/udp`
- `68:68/udp`
- `853:853`
- `784:784/udp`
- `853:853/tcp`
- `3001:3000/tcp`
- `5443:5443`
- `8853:8853/udp`

### Volumes
- `./etc/adguard/conf:/opt/adguardhome/conf` - Volume mount
- `./etc/adguard/work:/opt/adguardhome/work` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${ADGUARD_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.adguard.entrypoints=websecure`
- `traefik.http.routers.adguard.rule=Host(`${ADGUARD_CONTAINER_NAME:-adguard}.${HOST_DOMAIN}`)`
- `traefik.http.services.adguard.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${ADGUARD_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${ADGUARD_CONTAINER_NAME:-adguard}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable adguard

# Configure environment variables (if needed)
make scaffold adguard

# Start the service
make up
```
