# Crowdsec Traefik Bouncer

> Traefik Bouncer for CrowdSec

## Links
- [Official Documentation](https://plugins.traefik.io/plugins/6335346ca4caa9ddeffda116/crowdsec-bouncer-traefik-plugin)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/crowdsec-traefik-bouncer.yml)

## Docker Images
- `docker.io/fbonalair/traefik-crowdsec-bouncer:${TRAEFIK_BOUNCER_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CROWDSEC_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TRAEFIK_BOUNCER_API_KEY` |  | Traefik bouncer api key |
| `TRAEFIK_BOUNCER_DOCKER_TAG` |  | Docker image tag/version |

## Configuration

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${CROWDSEC_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`

## Quick Start

```bash
# Enable the service
make enable crowdsec-traefik-bouncer

# Configure environment variables (if needed)
make scaffold crowdsec-traefik-bouncer

# Start the service
make up
```
