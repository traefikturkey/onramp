"""Configuration settings for OnRamp Dashboard."""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Dashboard configuration via environment variables."""

    # Application
    app_title: str = "OnRamp Dashboard"
    debug: bool = False

    # Paths (container mounts)
    base_dir: Path = Path("/app")

    @property
    def services_available(self) -> Path:
        return self.base_dir / "services-available"

    @property
    def services_enabled(self) -> Path:
        return self.base_dir / "services-enabled"

    @property
    def services_scaffold(self) -> Path:
        return self.base_dir / "services-scaffold"

    @property
    def etc_dir(self) -> Path:
        return self.base_dir / "etc"

    # Docker
    docker_host: str = "unix:///var/run/docker.sock"

    # Prometheus/Traefik metrics (optional)
    prometheus_url: str = "http://traefik:8082"

    # Cache settings
    status_cache_ttl: int = 5  # seconds

    class Config:
        env_prefix = "DASHBOARD_"


settings = Settings()
