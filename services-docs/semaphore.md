# Semaphore

> UI and API for Ansible,Terraform/OpenTofu/Terragrunt

## Links
- [Official Documentation](https://docs.ansible-semaphore.com/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/semaphore.yml)

## Docker Images
- `mysql:8.0`
- `semaphoreui/semaphore:${SEMAPHORE_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `SEMAPHORE_ACCESS_KEY_ENCRYPTION` |  | Semaphore access key encryption |
| `SEMAPHORE_ADMIN` |  | Semaphore admin |
| `SEMAPHORE_ADMIN_EMAIL` |  | Semaphore admin email |
| `SEMAPHORE_ADMIN_NAME` |  | Semaphore admin name |
| `SEMAPHORE_ADMIN_PASSWORD` |  | Service password |
| `SEMAPHORE_ANSIBLE_HOST_KEY_CHECKING` |  | Semaphore ansible host key checking |
| `SEMAPHORE_CONTAINER_NAME` |  | Container name |
| `SEMAPHORE_DB` |  | Semaphore db |
| `SEMAPHORE_DB_DIALECT` |  | Semaphore db dialect |
| `SEMAPHORE_DB_HOST` |  | Semaphore db host |
| `SEMAPHORE_DB_PASS` |  | Semaphore db pass |
| `SEMAPHORE_DB_PORT` |  | Service port number |
| `SEMAPHORE_DB_USER` |  | Service username |
| `SEMAPHORE_DOCKER_TAG` |  | Docker image tag/version |
| `SEMAPHORE_LDAP_ACTIVATED` |  | Semaphore ldap activated |
| `SEMAPHORE_LDAP_DN_BIND` |  | Semaphore ldap dn bind |
| `SEMAPHORE_LDAP_HOST` |  | Semaphore ldap host |
| `SEMAPHORE_LDAP_NEEDTLS` |  | Semaphore ldap needtls |
| `SEMAPHORE_LDAP_PASSWORD` |  | Service password |
| `SEMAPHORE_LDAP_PORT` |  | Service port number |
| `SEMAPHORE_LDAP_SEARCH` |  | Semaphore ldap search |
| `SEMAPHORE_LDAP_SEARCH_FILTER` |  | Semaphore ldap search filter |
| `SEMAPHORE_PLAYBOOK_PATH` |  | Semaphore playbook path |
| `SEMAPHORE_RESTART` |  | Container restart policy |
| `SEMAPHORE_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/semaphore/db:/var/lib/mysql` - Volume mount
- `./etc/semaphore/inventory.txt:/inventory` - Volume mount
- `./etc/semaphore/authorized_keys.txt:/authorized_keys` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.semaphore.entrypoints=websecure`
- `traefik.http.routers.semaphore.rule=Host(`${SEMAPHORE_CONTAINER_NAME:-semaphore}.${HOST_DOMAIN}`)`
- `traefik.http.services.semaphore.loadbalancer.server.port=3000`
- `traefik.http.services.semaphore.loadbalancer.server.scheme=http`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SEMAPHORE_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${SEMAPHORE_CONTAINER_NAME:-semaphore}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `semaphore-db`

## Quick Start

```bash
# Enable the service
make enable semaphore

# Configure environment variables (if needed)
make scaffold semaphore

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
- Requires semaphore-db to be running
