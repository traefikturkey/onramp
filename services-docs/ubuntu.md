# Ubuntu

> ubuntu base image

## Links
- [Docker Image](https://hub.docker.com/_/ubuntu)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/ubuntu.yml)

## Docker Images
- `ubuntu`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `UBUNTU_TEST_VOLUME` |  | Ubuntu test volume |

## Configuration

### Volumes
- `${UBUNTU_TEST_VOLUME:-.}` - Volume mount

## Quick Start

```bash
# Enable the service
make enable ubuntu

# Configure environment variables (if needed)
make scaffold ubuntu

# Start the service
make up
```
