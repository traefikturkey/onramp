# Dozzle Agent

## Links
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/dozzle-agent.yml)

## Docker Images
- `amir20/dozzle:latest`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DOZZLE_RESTART` |  | Container restart policy |
| `HOST_NAME` |  | Host name |

## Configuration

### Ports
- `7007:7007`

### Volumes
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

## Quick Start

```bash
# Enable the service
make enable dozzle-agent

# Configure environment variables (if needed)
make scaffold dozzle-agent

# Start the service
make up
```
