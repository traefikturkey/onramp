# Authentik

> identity and access management solution

## Links
- [Official Repository](https://github.com/goauthentik/authentik)
- [Official Documentation](https://www.postgresql.org/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/authentik.yml)

## Docker Images
- `postgres`
- `redis:alpine`
- `${AUTHENTIK_IMAGE:-ghcr.io/goauthentik/server}:${AUTHENTIK_DOCKER_TAG:-2023.5.2}`
- `${AUTHENTIK_IMAGE:-ghcr.io/goauthentik/server}:${AUTHENTIK_DOCKER_TAG:-2022.8.2}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTHENTIK_AUTH_DOMAIN` |  | Authentik auth domain |
| `AUTHENTIK_BOOTSTRAP_PASSWORD` |  | Service password |
| `AUTHENTIK_DOCKER_TAG` |  | Docker image tag/version |
| `AUTHENTIK_IMAGE` |  | Authentik image |
| `AUTHENTIK_SECRET_KEY` |  | Authentik secret key |
| `AUTHENTIK_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `GEOIP_ACCOUNT` |  | Geoip account |
| `GEOIP_KEY` |  | Geoip key |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PG_DB` |  | Pg db |
| `PG_PASS_AUTHENTIK` |  | Pg pass authentik |
| `PG_USER` |  | Service username |
| `POSTGRES_DB` |  | PostgreSQL database name |
| `POSTGRES_USER` |  | PostgreSQL database username |
| `PUID` |  | User ID for file permissions |

## Configuration

### Volumes
- `./etc/authentik/postgresql:/var/lib/postgresql/data` - Volume mount
- `./etc/authentik/redis:/data` - Volume mount
- `./etc/authentik/media:/media` - Volume mount
- `./etc/authentik/certs:/certs` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount
- `./etc/authentik/custom-templates:/templates` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=false`
- `traefik.http.middlewares.authentik.forwardauth.address=http://authentik-server:9000/outpost.goauthentik.io/auth/traefik`
- `traefik.http.middlewares.authentik.forwardauth.authResponseHeaders=X-authentik-username,X-authentik-groups,X-authentik-email,X-authentik-name,X-authentik-uid,X-authentik-jwt,X-authentik-meta-jwks,X-authentik-meta-outpost,X-authentik-meta-provider,X-authentik-meta-app,X-authentik-meta-version`
- `traefik.http.middlewares.authentik.forwardauth.trustForwardHeader=true`
- `traefik.http.routers.authentik.entrypoints=websecure`
- `traefik.http.routers.authentik.rule=Host(`${AUTHENTIK_AUTH_DOMAIN}`) || HostRegexp(`{subdomain:[a-z]+}.${HOST_DOMAIN}`) && PathPrefix(`/outpost.goauthentik.io/`)`
- `traefik.http.services.authentik.loadbalancer.server.port=9000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${AUTHENTIK_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${AUTHENTIK_AUTH_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable authentik

# Configure environment variables (if needed)
make scaffold authentik

# Start the service
make up
```

## Notes
- This service consists of 4 containers working together
