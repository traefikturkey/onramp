"""Docker client wrapper for OnRamp Dashboard.

Provides container management via Docker API.
"""

from typing import Any

import docker
from docker.errors import NotFound, APIError


class DockerClient:
    """Wrapper around docker-py SDK for container operations."""

    def __init__(self, host: str = "tcp://docker-proxy:2375"):
        self.host = host
        self._client = None

    @property
    def client(self) -> docker.DockerClient:
        """Lazy initialization of Docker client."""
        if self._client is None:
            self._client = docker.DockerClient(base_url=self.host)
        return self._client

    def list_containers(self, all: bool = True) -> list[dict]:
        """List all containers with status info."""
        try:
            containers = self.client.containers.list(all=all)
            return [self._container_to_dict(c) for c in containers]
        except APIError as e:
            return []

    def get_container(self, name: str) -> dict | None:
        """Get a specific container by name."""
        try:
            container = self.client.containers.get(name)
            return self._container_to_dict(container)
        except NotFound:
            return None
        except APIError:
            return None

    def start(self, name: str) -> tuple[bool, str]:
        """Start a container."""
        try:
            container = self.client.containers.get(name)
            container.start()
            return True, f"Container {name} started"
        except NotFound:
            return False, f"Container {name} not found"
        except APIError as e:
            return False, str(e)

    def stop(self, name: str) -> tuple[bool, str]:
        """Stop a container."""
        try:
            container = self.client.containers.get(name)
            container.stop()
            return True, f"Container {name} stopped"
        except NotFound:
            return False, f"Container {name} not found"
        except APIError as e:
            return False, str(e)

    def restart(self, name: str) -> tuple[bool, str]:
        """Restart a container."""
        try:
            container = self.client.containers.get(name)
            container.restart()
            return True, f"Container {name} restarted"
        except NotFound:
            return False, f"Container {name} not found"
        except APIError as e:
            return False, str(e)

    def get_logs(self, name: str, tail: int = 100, timestamps: bool = True) -> str:
        """Get container logs."""
        try:
            container = self.client.containers.get(name)
            logs = container.logs(tail=tail, timestamps=timestamps)
            return logs.decode("utf-8", errors="replace")
        except NotFound:
            return f"Container {name} not found"
        except APIError as e:
            return str(e)

    def get_stats(self, name: str) -> dict | None:
        """Get container resource stats."""
        try:
            container = self.client.containers.get(name)
            stats = container.stats(stream=False)
            return self._parse_stats(stats)
        except (NotFound, APIError):
            return None

    def _container_to_dict(self, container: Any) -> dict:
        """Convert container object to dictionary."""
        image_tags = container.image.tags if container.image else []

        return {
            "id": container.short_id,
            "name": container.name,
            "status": container.status,
            "image": image_tags[0] if image_tags else "unknown",
            "created": container.attrs.get("Created", ""),
            "ports": container.ports or {},
            "labels": container.labels or {},
            "health": self._get_health_status(container),
            "started_at": container.attrs.get("State", {}).get("StartedAt", ""),
        }

    def _get_health_status(self, container: Any) -> str:
        """Extract health status from container."""
        state = container.attrs.get("State", {})
        health = state.get("Health", {})
        return health.get("Status", "none")

    def _parse_stats(self, stats: dict) -> dict:
        """Parse Docker stats into readable format."""
        cpu_delta = stats.get("cpu_stats", {}).get("cpu_usage", {}).get("total_usage", 0) - \
                   stats.get("precpu_stats", {}).get("cpu_usage", {}).get("total_usage", 0)
        system_delta = stats.get("cpu_stats", {}).get("system_cpu_usage", 0) - \
                      stats.get("precpu_stats", {}).get("system_cpu_usage", 0)
        num_cpus = len(stats.get("cpu_stats", {}).get("cpu_usage", {}).get("percpu_usage", [1]))

        cpu_percent = 0.0
        if system_delta > 0 and cpu_delta > 0:
            cpu_percent = (cpu_delta / system_delta) * num_cpus * 100.0

        memory_usage = stats.get("memory_stats", {}).get("usage", 0)
        memory_limit = stats.get("memory_stats", {}).get("limit", 1)
        memory_percent = (memory_usage / memory_limit) * 100.0 if memory_limit > 0 else 0.0

        return {
            "cpu_percent": round(cpu_percent, 2),
            "memory_usage": memory_usage,
            "memory_limit": memory_limit,
            "memory_percent": round(memory_percent, 2),
        }

    def ping(self) -> bool:
        """Check if Docker daemon is reachable."""
        try:
            self.client.ping()
            return True
        except Exception:
            return False
