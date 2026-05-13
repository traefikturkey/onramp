# Speedtest Tracker

> Scheduled internet speed testing dashboard

## Links
- [Official Repository](https://github.com/alexjustesen/speedtest-tracker)
- [Official Documentation](https://docs.linuxserver.io/images/docker-speedtest-tracker/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/speedtest-tracker.yml)

## Docker Images
- `lscr.io/linuxserver/speedtest-tracker:${SPEEDTEST_TRACKER_DOCKER_TAG:-latest}`
- `postgres:${SPEEDTEST_TRACKER_POSTGRES_TAG:-16-alpine}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `POSTGRES_USER` |  | PostgreSQL database username |
| `PUID` |  | User ID for file permissions |
| `SPEEDTEST_TRACKER_APP_KEY` | ${SPEEDTEST_TRACKER_APP_KEY:-} | Speedtest tracker app key |
| `SPEEDTEST_TRACKER_AUTOHEAL_ENABLED` | true | Enable Autoheal container restart on unhealthy status |
| `SPEEDTEST_TRACKER_CONTAINER_NAME` | speedtest-tracker | Container name |
| `SPEEDTEST_TRACKER_DB_CONTAINER_NAME` |  | Container name |
| `SPEEDTEST_TRACKER_DB_HOST` | speedtest-tracker-db | Speedtest tracker db host |
| `SPEEDTEST_TRACKER_DB_NAME` | speedtest | Speedtest tracker db name |
| `SPEEDTEST_TRACKER_DB_PASSWORD` | speedtest | Service password |
| `SPEEDTEST_TRACKER_DB_PORT` | 5432 | Service port number |
| `SPEEDTEST_TRACKER_DB_USER` | speedtest | Service username |
| `SPEEDTEST_TRACKER_DOCKER_TAG` | latest | Docker image tag/version |
| `SPEEDTEST_TRACKER_HOST_NAME` | speedtest | Speedtest tracker host name |
| `SPEEDTEST_TRACKER_POSTGRES_TAG` | 16-alpine | Speedtest tracker postgres tag |
| `SPEEDTEST_TRACKER_PRUNE_DAYS` | 0 | Speedtest tracker prune days |
| `SPEEDTEST_TRACKER_RESTART` | unless-stopped | Container restart policy |
| `SPEEDTEST_TRACKER_SCHEDULE` | 0 */6 * * * | Speedtest tracker schedule |
| `SPEEDTEST_TRACKER_SERVERS` | ${SPEEDTEST_TRACKER_SERVERS:-} | Speedtest tracker servers |
| `SPEEDTEST_TRACKER_TRAEFIK_ENABLED` | true | Enable Traefik reverse proxy |
| `SPEEDTEST_TRACKER_WATCHTOWER_ENABLED` | true | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/speedtest-tracker/config:/config` - Configuration files
- `/etc/localtime:/etc/localtime` - Volume mount
- `./etc/speedtest-tracker/postgres:/var/lib/postgresql/data` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${SPEEDTEST_TRACKER_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.speedtest-tracker.entrypoints=websecure`
- `traefik.http.routers.speedtest-tracker.rule=Host(`${SPEEDTEST_TRACKER_HOST_NAME:-speedtest}.${HOST_DOMAIN}`)`
- `traefik.http.services.speedtest-tracker.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SPEEDTEST_TRACKER_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${SPEEDTEST_TRACKER_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${SPEEDTEST_TRACKER_HOST_NAME:-speedtest}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable speedtest-tracker

# Configure environment variables (if needed)
make scaffold speedtest-tracker

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
