# Odoo

> a suite of applications used in managing a business, including CRM, ERP, and more.

## Links
- [Official Repository](https://github.com/odoo/odoo)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/odoo.yml)

## Docker Images
- `odoo:${ODOO_DOCKER_TAG:-latest}`
- `postgres:15`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `ODOO_AUTOHEAL_ENABLED` | true | Enable Autoheal container restart on unhealthy status |
| `ODOO_CONTAINER_NAME` | odoo | Container name |
| `ODOO_DOCKER_TAG` | 18 | Docker image tag/version |
| `ODOO_HOST_NAME` | odoo | Odoo host name |
| `ODOO_POSTGRES_DB` | odoo | PostgreSQL database name |
| `ODOO_POSTGRES_DB_PW` | ${ODOO_POSTGRES_DB_PW:-} | PostgreSQL database name |
| `ODOO_POSTGRES_USER` | odoo | Service username |
| `ODOO_RESTART` | unless-stopped | Container restart policy |
| `ODOO_TRAEFIK_ENABLED` | true | Enable Traefik reverse proxy |
| `ODOO_WATCHTOWER_ENABLED` | true | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./media/odoo/web-data:/var/lib/odoo` - Data storage
- `./media/odoo/addons:/mnt/extra-addons` - Volume mount
- `./etc/odoo:/etc/odoo` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `./media/odoo/postgresql:/var/lib/postgresql/data` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${ODOO_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.odoo.entrypoints=websecure`
- `traefik.http.routers.odoo.rule=Host(`${ODOO_HOST_NAME:-odoo}.${HOST_DOMAIN}`)`
- `traefik.http.routers.odoo.service=odoo`
- `traefik.http.routers.odoo.tls.certresolver=letsencrypt`
- `traefik.http.services.odoo.loadbalancer.server.port=8069`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${ODOO_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${ODOO_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${ODOO_HOST_NAME:-odoo}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable odoo

# Configure environment variables (if needed)
make scaffold odoo

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
