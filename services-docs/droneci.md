# Droneci

> Continuous integration and delivery platform

## Links
- [Official Repository](https://github.com/harness/drone)
- [Official Documentation](https://docs.drone.io/server/metrics/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/droneci.yml)

## Docker Images
- `drone/drone:${DRONE_DOCKER_TAG:-latest}`
- `drone/drone-runner-docker`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DRONE_ADMIN_USER_CREATE` |  | Service username |
| `DRONE_CONTAINER_NAME` |  | Container name |
| `DRONE_DOCKER_TAG` |  | Docker image tag/version |
| `DRONE_GITEA_CLIENT_ID` |  | Drone gitea client id |
| `DRONE_GITEA_CLIENT_SECRET` |  | Drone gitea client secret |
| `DRONE_RPC_SECRET` |  | Drone rpc secret |
| `DRONE_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `GITEA_CONTAINER_NAME` |  | Container name |
| `HOST_DOMAIN` |  | Host domain for service access |

## Configuration

### Ports
- `4003:3000`

### Volumes
- `./etc/droneci:/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

### Networks
- `traefik`
- `default`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.drone.entrypoints=websecure`
- `traefik.http.routers.drone.rule=Host(`${DRONE_CONTAINER_NAME:-drone}.${HOST_DOMAIN}`)`
- `traefik.http.services.drone.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${DRONE_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${DRONE_CONTAINER_NAME:-drone}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `drone`

## Quick Start

```bash
# Enable the service
make enable droneci

# Configure environment variables (if needed)
make scaffold droneci

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
- Requires drone to be running
