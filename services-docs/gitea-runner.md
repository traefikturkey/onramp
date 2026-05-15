# Gitea Runner

> Gitea Actions runner for CI/CD workflows (similar to GitHub Actions)

## Links
- [Official Repository](https://github.com/vegardit/docker-gitea-act-runner)
- [Official Documentation](https://docs.gitea.com/usage/actions/act-runner)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/gitea-runner.yml)

## Docker Images
- `ghcr.io/vegardit/gitea-act-runner:${GITEA_RUNNER_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GITEA_RUNNER_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `GITEA_RUNNER_CONTAINER_NAME` |  | Container name |
| `GITEA_RUNNER_DOCKER_TAG` |  | Docker image tag/version |
| `GITEA_RUNNER_INSTANCE_URL` |  | Gitea runner instance url |
| `GITEA_RUNNER_LABELS` | ubuntu-latest:docker://node:20-bookworm,ubuntu-22.04:docker://node:20-bookworm,ubuntu-20.04:docker://node:20-bookworm | Gitea runner labels |
| `GITEA_RUNNER_NAME` |  | Gitea runner name |
| `GITEA_RUNNER_REGISTRATION_TOKEN` | <token here> | Gitea runner registration token |
| `GITEA_RUNNER_RESTART` |  | Container restart policy |
| `GITEA_RUNNER_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/gitea-runner/config.yaml:/config.yaml` - Configuration files
- `./etc/gitea-runner/data:/data` - Data storage
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${GITEA_RUNNER_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${GITEA_RUNNER_AUTOHEAL_ENABLED:-true}`

## Quick Start

```bash
# Enable the service
make enable gitea-runner

# Configure environment variables (if needed)
make scaffold gitea-runner

# Start the service
make up
```
