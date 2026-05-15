#!/usr/bin/env python3
"""
Generate comprehensive markdown documentation for all OnRamp services.

This script:
1. Reads all .yml files from services-available/
2. Extracts metadata (description, URL, etc.)
3. Parses environment variables from service yml and env.template files
4. Scans overrides-available/ for service-specific override configurations
5. Analyzes override files to document alternative configurations
6. Generates detailed markdown documentation for each service
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml


class ServiceDocGenerator:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.services_available_dir = root_dir / "services-available"
        self.services_scaffold_dir = root_dir / "services-scaffold"
        self.services_docs_dir = root_dir / "services-docs"
        self.overrides_available_dir = root_dir / "overrides-available"

        # Create docs directory if it doesn't exist
        self.services_docs_dir.mkdir(exist_ok=True)

    def extract_yml_metadata(self, yml_path: Path) -> Dict[str, str]:
        """Extract metadata from YAML file comments."""
        metadata = {
            'description': '',
            'url': '',
            'github': '',
            'docker_hub': ''
        }

        try:
            with open(yml_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

                for line in lines[:20]:  # Check first 20 lines for metadata
                    line = line.strip()

                    # Extract description
                    if line.startswith('# description:'):
                        metadata['description'] = line.replace('# description:', '').strip()

                    # Extract URL
                    elif line.startswith('# https://'):
                        url = line.replace('# ', '').strip()
                        metadata['url'] = url

                        # Categorize URL
                        if 'github.com' in url:
                            metadata['github'] = url
                        elif 'hub.docker.com' in url or 'docker.io' in url:
                            metadata['docker_hub'] = url

        except Exception as e:
            print(f"Warning: Could not extract metadata from {yml_path}: {e}")

        return metadata

    def parse_yaml_content(self, yml_path: Path) -> Optional[Dict]:
        """Parse YAML content to extract service configuration."""
        try:
            with open(yml_path, 'r', encoding='utf-8') as f:
                # Remove comment lines starting with #
                content = []
                for line in f:
                    if not line.strip().startswith('#'):
                        content.append(line)

                yaml_content = ''.join(content)
                return yaml.safe_load(yaml_content)

        except Exception as e:
            print(f"Warning: Could not parse YAML from {yml_path}: {e}")
            return None

    def extract_env_vars_from_yml(self, yml_path: Path) -> List[str]:
        """Extract environment variable references from YAML file."""
        env_vars = set()

        try:
            with open(yml_path, 'r', encoding='utf-8') as f:
                content = f.read()

                # Find all ${VAR_NAME} or ${VAR_NAME:-default} patterns
                pattern = r'\$\{([A-Z_][A-Z0-9_]*)(:-[^}]*)?\}'
                matches = re.findall(pattern, content)

                for match in matches:
                    env_vars.add(match[0])

        except Exception as e:
            print(f"Warning: Could not extract env vars from {yml_path}: {e}")

        return sorted(list(env_vars))

    def parse_env_template(self, service_name: str) -> Dict[str, Dict[str, str]]:
        """Parse env.template file to extract variable definitions."""
        env_template_path = self.services_scaffold_dir / service_name / "env.template"
        env_vars = {}

        if not env_template_path.exists():
            return env_vars

        try:
            with open(env_template_path, 'r', encoding='utf-8') as f:
                current_section = None

                for line in f:
                    line = line.strip()

                    # Skip empty lines
                    if not line:
                        continue

                    # Section headers (comments that are all caps or describe a section)
                    if line.startswith('#') and not line.startswith('##'):
                        current_section = line.lstrip('#').strip()
                        continue

                    # Variable definitions
                    if '=' in line and not line.startswith('#'):
                        parts = line.split('=', 1)
                        var_name = parts[0].strip()
                        var_value = parts[1].strip() if len(parts) > 1 else ''

                        # Extract default value from ${VAR:-default} pattern
                        default_match = re.search(r'\$\{[^:}]+:-([^}]+)\}', var_value)
                        if default_match:
                            var_value = default_match.group(1)

                        env_vars[var_name] = {
                            'default': var_value,
                            'section': current_section or 'General',
                            'description': self.infer_description(var_name)
                        }

        except Exception as e:
            print(f"Warning: Could not parse env template for {service_name}: {e}")

        return env_vars

    def infer_description(self, var_name: str) -> str:
        """Infer description from variable name."""
        # Common patterns
        descriptions = {
            'CONTAINER_NAME': 'Container name',
            'DOCKER_TAG': 'Docker image tag/version',
            'RESTART': 'Container restart policy',
            'WATCHTOWER_ENABLE': 'Enable Watchtower auto-updates',
            'TRAEFIK_ENABLE': 'Enable Traefik reverse proxy',
            'AUTOHEAL': 'Enable Autoheal container restart on unhealthy status',
            'PUID': 'User ID for file permissions',
            'PGID': 'Group ID for file permissions',
            'TZ': 'Timezone setting',
            'PORT': 'Service port number',
            'PASSWORD': 'Service password',
            'USER': 'Service username',
            'POSTGRES_PASSWORD': 'PostgreSQL database password',
            'POSTGRES_USER': 'PostgreSQL database username',
            'POSTGRES_DB': 'PostgreSQL database name',
            'DB_HOSTNAME': 'Database host address',
            'DB_PASSWORD': 'Database password',
            'DB_USERNAME': 'Database username',
            'DB_DATABASE_NAME': 'Database name',
            'REDIS_HOSTNAME': 'Redis cache hostname',
            'HOST_DOMAIN': 'Host domain for service access',
            'UPLOAD_LOCATION': 'Directory for uploaded files',
            'DATA_DIR': 'Data directory path',
            'CONFIG_DIR': 'Configuration directory path',
            'BACKUP_DIR': 'Backup directory path',
        }

        # Check for exact matches
        if var_name in descriptions:
            return descriptions[var_name]

        # Check for partial matches
        for key, desc in descriptions.items():
            if key in var_name:
                return desc

        # Generate from variable name
        name = var_name.replace('_', ' ').lower().capitalize()
        return name

    def extract_service_info(self, yaml_data: Dict) -> Dict:
        """Extract service information from parsed YAML."""
        info = {
            'images': [],
            'ports': [],
            'volumes': [],
            'networks': [],
            'labels': {},
            'environment': [],
            'depends_on': []
        }

        if not yaml_data or 'services' not in yaml_data:
            return info

        # Process all services in the file
        for service_name, service_config in yaml_data.get('services', {}).items():
            if not isinstance(service_config, dict):
                continue

            # Extract image
            if 'image' in service_config:
                info['images'].append(service_config['image'])

            # Extract ports
            if 'ports' in service_config:
                for port in service_config['ports']:
                    info['ports'].append(str(port))

            # Extract expose ports
            if 'expose' in service_config:
                for port in service_config['expose']:
                    info['ports'].append(f"{port} (internal)")

            # Extract volumes
            if 'volumes' in service_config:
                for volume in service_config['volumes']:
                    info['volumes'].append(str(volume))

            # Extract networks
            if 'networks' in service_config:
                networks = service_config['networks']
                if isinstance(networks, list):
                    info['networks'].extend(networks)
                elif isinstance(networks, dict):
                    info['networks'].extend(networks.keys())

            # Extract labels
            if 'labels' in service_config:
                for label in service_config['labels']:
                    if isinstance(label, str) and '=' in label:
                        key, value = label.split('=', 1)
                        info['labels'][key] = value

            # Extract environment variables
            if 'environment' in service_config:
                env = service_config['environment']
                if isinstance(env, list):
                    info['environment'].extend(env)
                elif isinstance(env, dict):
                    info['environment'].extend([f"{k}={v}" for k, v in env.items()])

            # Extract dependencies
            if 'depends_on' in service_config:
                deps = service_config['depends_on']
                if isinstance(deps, list):
                    info['depends_on'].extend(deps)

        # Remove duplicates
        info['images'] = list(dict.fromkeys(info['images']))
        info['ports'] = list(dict.fromkeys(info['ports']))
        info['volumes'] = list(dict.fromkeys(info['volumes']))
        info['networks'] = list(dict.fromkeys(info['networks']))

        return info

    def find_service_overrides(self, service_name: str) -> List[Path]:
        """Find all override files for a given service."""
        if not self.overrides_available_dir.exists():
            return []

        # Strip games- prefix if present
        base_service_name = service_name.replace('games-', '')

        # Find all overrides matching the pattern {service}*.yml
        pattern = f"{base_service_name}*.yml"
        overrides = sorted(self.overrides_available_dir.glob(pattern))

        return overrides

    def analyze_override(self, override_path: Path) -> Dict:
        """Analyze an override file to determine what it modifies."""
        analysis = {
            'filename': override_path.name,
            'override_name': override_path.stem,
            'purpose': '',
            'volumes': [],
            'services': [],
            'environment_vars': [],
            'comments': []
        }

        try:
            # Read file for comments
            with open(override_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

                # Extract comments from first 10 lines
                for line in lines[:10]:
                    line = line.strip()
                    if line.startswith('#') and line != '#':
                        comment = line.lstrip('#').strip()
                        if comment:
                            analysis['comments'].append(comment)

            # Parse YAML content
            yaml_data = self.parse_yaml_content(override_path)

            if yaml_data:
                # Extract volumes
                if 'volumes' in yaml_data:
                    for vol_name in yaml_data['volumes'].keys():
                        analysis['volumes'].append(vol_name)

                # Extract services
                if 'services' in yaml_data:
                    for svc_name, svc_config in yaml_data['services'].items():
                        analysis['services'].append(svc_name)

                        # Extract environment variables
                        if isinstance(svc_config, dict) and 'environment' in svc_config:
                            env = svc_config['environment']
                            if isinstance(env, list):
                                for env_var in env:
                                    if isinstance(env_var, str) and '=' in env_var:
                                        var_name = env_var.split('=')[0].strip()
                                        if var_name not in analysis['environment_vars']:
                                            analysis['environment_vars'].append(var_name)

            # Infer purpose from filename and content
            analysis['purpose'] = self.infer_override_purpose(analysis)

        except Exception as e:
            print(f"Warning: Could not analyze override {override_path}: {e}")

        return analysis

    def infer_override_purpose(self, analysis: Dict) -> str:
        """Infer the purpose of an override from its filename and content."""
        filename = analysis['override_name'].lower()

        # Check comments for purpose - use first meaningful comment
        for comment in analysis['comments']:
            comment_lower = comment.lower()
            # Skip usage lines
            if 'usage:' in comment_lower or 'make enable-override' in comment_lower:
                continue
            # Use descriptive comments
            if any(word in comment_lower for word in ['override', 'backward', 'compatibility', 'configuration']):
                return comment

        # Check filename patterns (order matters - check most specific first)

        # NFS patterns
        if 'nfs' in filename:
            if 'cpu' in filename:
                return "Configures NFS volume mounts for CPU-based setup"
            elif 'nvidia' in filename or 'gpu' in filename:
                return "Configures NFS volume mounts for NVIDIA GPU setup"
            else:
                return "Configures NFS volume mounts for remote storage"

        # Dedicated database patterns
        if 'dedicated-redis' in filename:
            return "Adds a dedicated Redis container for this service"
        if 'dedicated-postgres' in filename or 'dedicated-postgresql' in filename:
            return "Adds a dedicated PostgreSQL database container for this service"
        if 'dedicated-mariadb' in filename or 'dedicated-mysql' in filename:
            return "Adds a dedicated MariaDB database container for this service"
        if 'dedicated-valkey' in filename:
            return "Adds a dedicated Valkey container for this service"

        # Standalone database patterns (without "dedicated" prefix)
        if filename.endswith('-postgres') or filename.endswith('-postgresql'):
            return "Configures PostgreSQL database for this service"
        if filename.endswith('-mariadb') or filename.endswith('-mysql'):
            return "Configures MariaDB database for this service"
        if filename.endswith('-redis'):
            return "Configures Redis for this service"

        # Hardware acceleration patterns
        if 'nvidia' in filename or 'gpu' in filename:
            return "Enables NVIDIA GPU hardware acceleration"
        if 'quicksync' in filename:
            return "Enables Intel QuickSync hardware acceleration"
        if 'amd' in filename:
            return "Enables AMD GPU hardware acceleration"
        if 'cpu' in filename:
            return "Configuration optimized for CPU-based processing"

        # Integration patterns
        if 'adguard' in filename:
            return "Integrates with AdGuard Home"
        if 'dynmap' in filename:
            return "Enables Dynmap web map for Minecraft"

        # Other patterns
        if 'extra' in filename:
            return "Provides additional configuration options"

        # Default
        return "Alternative configuration for this service"

    def format_override_section(self, overrides: List[Dict]) -> str:
        """Format the override section for markdown."""
        if not overrides:
            return ""

        md = []
        md.append("## Available Overrides")
        md.append("")
        md.append("OnRamp supports configuration overrides to customize this service. The following overrides are available:")
        md.append("")

        for override in overrides:
            override_name = override['override_name']

            # Override header
            md.append(f"### {override_name}")
            md.append("")

            # Purpose
            if override['purpose']:
                md.append(f"**Purpose**: {override['purpose']}")
                md.append("")

            # Changes
            changes = []
            if override['volumes']:
                changes.append(f"- **Adds/modifies volumes**: {', '.join([f'`{v}`' for v in override['volumes']])}")
            if override['services']:
                changes.append(f"- **Adds/modifies services**: {', '.join([f'`{s}`' for s in override['services']])}")
            if override['environment_vars']:
                changes.append(f"- **Adds/modifies environment variables**: {', '.join([f'`{e}`' for e in override['environment_vars']])}")

            if changes:
                md.append("**Changes**:")
                md.extend(changes)
                md.append("")

            # Usage
            md.append("**Usage**:")
            md.append("```bash")
            md.append(f"make enable-override {override_name}")
            md.append("make up")
            md.append("```")
            md.append("")

            # Configuration link
            github_override_url = f"https://github.com/traefikturkey/onramp/tree/main/overrides-available/{override['filename']}"
            md.append(f"**Configuration**: [View override file]({github_override_url})")
            md.append("")

        return '\n'.join(md)

    def generate_markdown(self, service_name: str, yml_path: Path) -> str:
        """Generate markdown documentation for a service."""
        metadata = self.extract_yml_metadata(yml_path)
        yaml_data = self.parse_yaml_content(yml_path)
        env_vars_yml = self.extract_env_vars_from_yml(yml_path)
        env_template = self.parse_env_template(service_name)
        service_info = self.extract_service_info(yaml_data)

        # Find and analyze overrides
        override_paths = self.find_service_overrides(service_name)
        overrides = [self.analyze_override(p) for p in override_paths]

        # Build markdown content
        md = []

        # Title
        md.append(f"# {service_name.replace('-', ' ').title()}")
        md.append("")

        # Description
        if metadata['description']:
            md.append(f"> {metadata['description']}")
            md.append("")

        # Links section
        md.append("## Links")
        if metadata['github']:
            md.append(f"- [Official Repository]({metadata['github']})")
        if metadata['docker_hub']:
            md.append(f"- [Docker Image]({metadata['docker_hub']})")
        if metadata['url'] and metadata['url'] not in [metadata['github'], metadata['docker_hub']]:
            md.append(f"- [Official Documentation]({metadata['url']})")

        github_yml_url = f"https://github.com/traefikturkey/onramp/tree/main/services-available/{yml_path.name}"
        md.append(f"- [Service Configuration]({github_yml_url})")
        md.append("")

        # Docker Images
        if service_info['images']:
            md.append("## Docker Images")
            for image in service_info['images']:
                md.append(f"- `{image}`")
            md.append("")

        # Environment Variables
        if env_vars_yml or env_template:
            md.append("## Environment Variables")
            md.append("")
            md.append("| Variable | Default | Description |")
            md.append("|----------|---------|-------------|")

            # Combine variables from both sources
            all_vars = set(env_vars_yml)
            all_vars.update(env_template.keys())

            for var in sorted(all_vars):
                if var in env_template:
                    default = env_template[var]['default']
                    description = env_template[var]['description']
                else:
                    default = ""
                    description = self.infer_description(var)

                # Escape pipe characters in values
                default = default.replace('|', '\\|')
                description = description.replace('|', '\\|')

                md.append(f"| `{var}` | {default} | {description} |")

            md.append("")

        # Configuration section
        md.append("## Configuration")
        md.append("")

        # Ports
        if service_info['ports']:
            md.append("### Ports")
            for port in service_info['ports']:
                md.append(f"- `{port}`")
            md.append("")

        # Volumes
        if service_info['volumes']:
            md.append("### Volumes")
            for volume in service_info['volumes']:
                if ':' in str(volume):
                    parts = str(volume).split(':')
                    host_path = parts[0]
                    container_path = parts[1] if len(parts) > 1 else ''
                    flags = parts[2] if len(parts) > 2 else ''

                    desc = "Configuration files" if 'config' in host_path.lower() else \
                           "Data storage" if 'data' in host_path.lower() else \
                           "Uploaded files" if 'upload' in host_path.lower() else \
                           "Volume mount"

                    md.append(f"- `{host_path}:{container_path}` - {desc}")
                else:
                    md.append(f"- `{volume}`")
            md.append("")

        # Networks
        if service_info['networks']:
            md.append("### Networks")
            for network in service_info['networks']:
                md.append(f"- `{network}`")
            md.append("")

        # Labels
        if service_info['labels']:
            md.append("### Labels")

            # Group labels by type
            traefik_labels = {k: v for k, v in service_info['labels'].items() if k.startswith('traefik.')}
            watchtower_labels = {k: v for k, v in service_info['labels'].items() if 'watchtower' in k}
            other_labels = {k: v for k, v in service_info['labels'].items()
                          if not k.startswith('traefik.') and 'watchtower' not in k}

            if traefik_labels:
                md.append("**Traefik Configuration:**")
                for key, value in sorted(traefik_labels.items()):
                    md.append(f"- `{key}={value}`")
                md.append("")

            if watchtower_labels:
                md.append("**Watchtower Configuration:**")
                for key, value in sorted(watchtower_labels.items()):
                    md.append(f"- `{key}={value}`")
                md.append("")

            if other_labels:
                md.append("**Other Labels:**")
                for key, value in sorted(other_labels.items()):
                    md.append(f"- `{key}={value}`")
                md.append("")

        # Dependencies
        if service_info['depends_on']:
            md.append("### Dependencies")
            md.append("This service depends on:")
            for dep in service_info['depends_on']:
                md.append(f"- `{dep}`")
            md.append("")

        # Available Overrides
        if overrides:
            override_section = self.format_override_section(overrides)
            if override_section:
                md.append(override_section)

        # Quick Start
        md.append("## Quick Start")
        md.append("")
        md.append("```bash")
        md.append(f"# Enable the service")
        md.append(f"make enable {service_name}")
        md.append("")
        md.append(f"# Configure environment variables (if needed)")
        md.append(f"make scaffold {service_name}")
        md.append("")
        md.append(f"# Start the service")
        md.append(f"make up")
        md.append("```")
        md.append("")

        # Additional Notes
        if service_info['depends_on'] or len(service_info['images']) > 1:
            md.append("## Notes")

            if len(service_info['images']) > 1:
                md.append(f"- This service consists of {len(service_info['images'])} containers working together")

            if service_info['depends_on']:
                md.append(f"- Requires {', '.join(service_info['depends_on'])} to be running")

            md.append("")

        return '\n'.join(md)

    def generate_all_docs(self):
        """Generate documentation for all services."""
        # Get main services
        yml_files = sorted(self.services_available_dir.glob("*.yml"))

        # Get game services from subdirectory
        games_dir = self.services_available_dir / "games"
        if games_dir.exists():
            game_files = sorted(games_dir.glob("*.yml"))
            yml_files.extend(game_files)

        print(f"Found {len(yml_files)} service files")
        print(f"Generating documentation in: {self.services_docs_dir}")
        print("")

        success_count = 0
        error_count = 0

        for yml_path in yml_files:
            # Handle subdirectory services (e.g., games/minecraft.yml -> games-minecraft)
            if yml_path.parent.name == "games":
                service_name = f"games-{yml_path.stem}"
            else:
                service_name = yml_path.stem

            try:
                print(f"Processing: {service_name}...", end=' ')

                # Generate markdown
                markdown = self.generate_markdown(service_name, yml_path)

                # Write to file
                output_path = self.services_docs_dir / f"{service_name}.md"
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown)

                print("OK")
                success_count += 1

            except Exception as e:
                print(f"ERROR: {e}")
                error_count += 1

        print("")
        print(f"Documentation generation complete!")
        print(f"  Success: {success_count}")
        print(f"  Errors: {error_count}")
        print(f"  Output directory: {self.services_docs_dir}")


def main():
    """Main entry point."""
    # Determine project root (go up 2 levels from scripts directory)
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent.parent

    print("=" * 60)
    print("OnRamp Service Documentation Generator")
    print("=" * 60)
    print("")

    generator = ServiceDocGenerator(root_dir)
    generator.generate_all_docs()


if __name__ == "__main__":
    main()
