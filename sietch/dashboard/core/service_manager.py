"""Service manager wrapper for OnRamp Dashboard.

Wraps the existing sietch services.py ServiceManager for dashboard use.
"""

import sys
from pathlib import Path

# Add scripts directory to path to import existing ServiceManager
sys.path.insert(0, "/scripts")

from services import ServiceManager as SietchServiceManager


class ServiceManager:
    """Async-friendly wrapper around sietch ServiceManager."""

    def __init__(self, base_dir: str = "/app"):
        self._manager = SietchServiceManager(base_dir)
        self.base_dir = Path(base_dir)

    def list_available(self) -> list[dict]:
        """List all available services with metadata."""
        services = []
        for name in self._manager.list_available():
            info = self._manager.get_service_info(name)
            if info:
                services.append(info)
        return services

    def list_enabled(self) -> list[dict]:
        """List all enabled services with metadata."""
        services = []
        for name in self._manager.list_enabled():
            info = self._manager.get_service_info(name)
            if info:
                services.append(info)
        return services

    def list_games(self) -> list[dict]:
        """List all available games with metadata."""
        services = []
        for name in self._manager.list_games():
            info = self._manager.get_service_info(name)
            if info:
                services.append(info)
        return services

    def get_service_info(self, name: str) -> dict | None:
        """Get detailed info for a specific service."""
        return self._manager.get_service_info(name)

    def get_enabled_names(self) -> list[str]:
        """Get just the names of enabled services."""
        return self._manager.list_enabled()

    def get_available_names(self) -> list[str]:
        """Get just the names of available services."""
        return self._manager.list_available()

    def get_categories(self) -> list[str]:
        """Get unique categories from all services."""
        categories = set()
        for name in self._manager.list_available():
            info = self._manager.get_service_info(name)
            if info and info.get("category"):
                categories.add(info["category"])
        return sorted(categories)

    def search(self, query: str) -> list[dict]:
        """Search services by name or description."""
        query = query.lower()
        results = []
        for name in self._manager.list_available():
            info = self._manager.get_service_info(name)
            if info:
                if query in name.lower():
                    results.append(info)
                elif info.get("description") and query in info["description"].lower():
                    results.append(info)
        return results

    def filter_by_category(self, category: str) -> list[dict]:
        """Filter services by category."""
        results = []
        for name in self._manager.list_available():
            info = self._manager.get_service_info(name)
            if info and info.get("category") == category:
                results.append(info)
        return results
