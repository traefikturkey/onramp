#!/usr/bin/env python
"""
services_linter.py - Service configuration linter for OnRamp

Validates service YAML files against OnRamp standards and best practices.
"""

import re
import sys
from pathlib import Path
from typing import Optional

# Try to import yaml, but don't fail at import time
yaml = None
try:
    import yaml
except ImportError:
    pass


class ServiceLinter:
    """Lints service configurations against OnRamp standards."""
    
    CURRENT_VERSION = 2
    
    # Required labels for web services (those with traefik.enable=true)
    REQUIRED_LABELS_WEB = [
        "joyride.host.name",
        "traefik.enable",
        "traefik.http.routers",
        "traefik.http.services",
        "com.centurylinklabs.watchtower.enable",
        "autoheal",
    ]
    
    # Required labels for all services
    REQUIRED_LABELS_ALL = [
        "com.centurylinklabs.watchtower.enable",
        "autoheal",
    ]
    
    # Standard environment variables expected in most services
    STANDARD_ENV_VARS = ["PUID", "PGID", "TZ"]
    
    # Infrastructure services that don't need PUID/PGID
    INFRASTRUCTURE_SERVICES = [
        "postgres", "mariadb", "redis", "valkey", "surrealdb",
        "traefik", "autoheal", "watchtower", "dozzle",
        "prometheus", "grafana", "loki"
    ]
    
    def __init__(self, base_dir: str = "/app"):
        self.base_dir = Path(base_dir)
        self.services_available = self.base_dir / "services-available"
    
    def lint(self, service: str, strict: bool = False, auto_fix: bool = False) -> tuple[bool, list[str], list[str]]:
        """
        Lint a service configuration.
        
        Returns (is_valid, errors, warnings)
        """
        if yaml is None:
            return False, ["pyyaml not installed. Install with: pip install pyyaml"], []
        
        errors = []
        warnings = []
        
        service_file = self.services_available / f"{service}.yml"
        if not service_file.exists():
            return False, [f"Service file not found: {service_file}"], []
        
        # Read file content
        with open(service_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse YAML
        try:
            config = yaml.safe_load(content)
        except yaml.YAMLError as e:
            return False, [f"Invalid YAML: {e}"], []
        
        if not config or 'services' not in config:
            return False, ["Invalid service configuration: missing 'services' section"], []
        
        # Check config version
        version = self._get_config_version(content)
        if version < self.CURRENT_VERSION:
            errors.append(f"Outdated config version: v{version} (current standard: v{self.CURRENT_VERSION})")
        
        # Check documentation
        if not self._has_description(content):
            errors.append("Missing '# description:' comment")
        
        if not self._has_url(content):
            warnings.append("No URL references found (recommend adding GitHub or Docker Hub links)")
        
        # Check network configuration
        if not self._has_traefik_network(config):
            # Some services may use network_mode: host
            if not self._uses_host_network(config):
                warnings.append("Missing 'traefik' network definition (unless using network_mode: host)")
        
        # Check each service definition
        for svc_name, svc_config in config.get('services', {}).items():
            # Check environment variables
            env_issues = self._check_env_vars(svc_name, svc_config, service)
            errors.extend(env_issues.get("errors", []))
            warnings.extend(env_issues.get("warnings", []))
            
            # Check labels
            label_issues = self._check_labels(svc_name, svc_config, service)
            errors.extend(label_issues.get("errors", []))
            warnings.extend(label_issues.get("warnings", []))
            
            # Check volumes
            volume_issues = self._check_volumes(svc_name, svc_config)
            warnings.extend(volume_issues)
        
        # Check for hardcoded values
        hardcoded = self._find_hardcoded_values(content)
        if hardcoded:
            warnings.extend([f"Hardcoded value detected: {h}" for h in hardcoded])
        
        is_valid = len(errors) == 0
        if strict:
            is_valid = is_valid and len(warnings) == 0
        
        return is_valid, errors, warnings
    
    def _get_config_version(self, content: str) -> int:
        """Extract config version from YAML comments."""
        for line in content.split('\n'):
            if line.strip().startswith('# config_version:'):
                try:
                    return int(line.split(':', 1)[1].strip())
                except (ValueError, IndexError):
                    return 1
        return 1  # Default to v1 if not specified
    
    def _has_description(self, content: str) -> bool:
        """Check if service has description comment."""
        return '# description:' in content
    
    def _has_url(self, content: str) -> bool:
        """Check if service has URL references."""
        return '# http' in content.lower()
    
    def _has_traefik_network(self, config: dict) -> bool:
        """Check if traefik network is defined."""
        networks = config.get('networks', {})
        return 'traefik' in networks and networks['traefik'].get('external') == True
    
    def _uses_host_network(self, config: dict) -> bool:
        """Check if any service uses network_mode: host."""
        for svc_config in config.get('services', {}).values():
            if svc_config.get('network_mode') == 'host':
                return True
        return False
    
    def _check_env_vars(self, svc_name: str, svc_config: dict, service: str) -> dict:
        """Check environment variable patterns."""
        errors = []
        warnings = []
        
        env = svc_config.get('environment', [])
        env_dict = {}
        
        # Convert env list/dict to dict for easier checking
        if isinstance(env, list):
            for item in env:
                if isinstance(item, str) and '=' in item:
                    key, val = item.split('=', 1)
                    env_dict[key] = val
                elif isinstance(item, str):
                    # Format like "- KEY" without value
                    env_dict[item.strip('- ')] = None
        elif isinstance(env, dict):
            env_dict = env
        
        # Check for PUID/PGID (skip for infrastructure services)
        if service not in self.INFRASTRUCTURE_SERVICES:
            has_puid = any('PUID' in k for k in env_dict.keys())
            has_pgid = any('PGID' in k for k in env_dict.keys())
            has_uid = any(k in ['UID', 'USER_ID'] for k in env_dict.keys())
            has_gid = any(k in ['GID', 'GROUP_ID'] for k in env_dict.keys())
            
            # Check if using user: directive instead
            has_user_directive = 'user' in svc_config
            
            if has_uid or has_gid:
                warnings.append(f"{svc_name}: Uses UID/GID instead of PUID/PGID (recommend standardizing)")
            elif not has_puid and not has_pgid and not has_user_directive:
                warnings.append(f"{svc_name}: Missing PUID/PGID environment variables")
        
        # Check for TZ
        if not any('TZ' in k for k in env_dict.keys()):
            warnings.append(f"{svc_name}: Missing TZ environment variable")
        
        return {"errors": errors, "warnings": warnings}
    
    def _check_labels(self, svc_name: str, svc_config: dict, service: str) -> dict:
        """Check service labels."""
        errors = []
        warnings = []
        
        labels = svc_config.get('labels', [])
        label_dict = {}
        
        # Convert labels to dict
        if isinstance(labels, list):
            for label in labels:
                if isinstance(label, str):
                    # Handle both "key=value" and "key: value" formats
                    if '=' in label:
                        k, v = label.split('=', 1)
                        label_dict[k.strip('- ')] = v
                    elif ':' in label and not label.startswith('-'):
                        parts = label.split(':', 1)
                        if len(parts) == 2:
                            label_dict[parts[0].strip('- ')] = parts[1].strip()
        elif isinstance(labels, dict):
            label_dict = labels
        
        # Check if this is a web service
        traefik_enable = label_dict.get('traefik.enable', '').strip()
        is_web_service = traefik_enable and 'true' in traefik_enable.lower()
        
        if is_web_service:
            # Check required web service labels
            if not any('joyride.host.name' in k for k in label_dict.keys()):
                errors.append(f"{svc_name}: Web service missing joyride.host.name label")
            
            if not any('traefik.http.routers' in k for k in label_dict.keys()):
                errors.append(f"{svc_name}: Missing Traefik router configuration")
            
            if not any('traefik.http.services' in k or 'loadbalancer.server.port' in str(label_dict) for k in label_dict.keys()):
                errors.append(f"{svc_name}: Missing Traefik loadbalancer port configuration")
        
        # Check autoheal (required for all services)
        if not any('autoheal' in k for k in label_dict.keys()):
            warnings.append(f"{svc_name}: Missing autoheal label")
        
        # Check watchtower
        if not any('watchtower.enable' in k for k in label_dict.keys()):
            warnings.append(f"{svc_name}: Missing watchtower.enable label")
        
        return {"errors": errors, "warnings": warnings}
    
    def _check_volumes(self, svc_name: str, svc_config: dict) -> list[str]:
        """Check volume mounts."""
        warnings = []
        
        volumes = svc_config.get('volumes', [])
        environment = svc_config.get('environment', [])
        
        # Check if TZ is set
        has_tz = False
        if isinstance(environment, list):
            has_tz = any('TZ' in str(item) for item in environment)
        elif isinstance(environment, dict):
            has_tz = 'TZ' in environment
        
        # Check if /etc/localtime is mounted
        has_localtime = any('/etc/localtime' in str(v) for v in volumes)
        
        if has_tz and not has_localtime:
            warnings.append(f"{svc_name}: Has TZ env var but missing /etc/localtime:/etc/localtime:ro volume mount")
        
        return warnings
    
    def _find_hardcoded_values(self, content: str) -> list[str]:
        """Find hardcoded hostnames and values that should be variables."""
        hardcoded = []
        
        # Look for patterns like "service.${HOST_DOMAIN}" where service is hardcoded
        # This should be "${SERVICE_CONTAINER_NAME:-service}.${HOST_DOMAIN}"
        pattern = r'([a-z][a-z0-9-]+)\.\$\{HOST_DOMAIN\}'
        matches = re.findall(pattern, content)
        
        for match in matches:
            # Check if it appears to be a hardcoded service name (not a variable)
            if match and not match.startswith('${'):
                hardcoded.append(f"Hardcoded hostname: {match}.${{HOST_DOMAIN}} (should use variable)")
        
        return list(set(hardcoded))  # Remove duplicates
