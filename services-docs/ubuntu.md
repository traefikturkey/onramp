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

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### ubuntu-nfs

**Purpose**: Configures NFS volume mounts for remote storage

**Changes**:
- **Adds/modifies volumes**: `ubuntu-test-nfs-volume`
- **Adds/modifies services**: `ubuntu-test`

**Usage**:
```bash
make enable-override ubuntu-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/ubuntu-nfs.yml)

### ubuntu-smb

**Purpose**: Alternative configuration for this service

**Changes**:
- **Adds/modifies volumes**: `ubuntu-test-smb-volume`
- **Adds/modifies services**: `ubuntu-test`

**Usage**:
```bash
make enable-override ubuntu-smb
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/ubuntu-smb.yml)

## Quick Start

```bash
# Enable the service
make enable ubuntu

# Configure environment variables (if needed)
make scaffold ubuntu

# Start the service
make up
```
