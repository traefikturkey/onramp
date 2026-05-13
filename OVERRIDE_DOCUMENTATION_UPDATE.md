# Service Documentation Generation - Override Support Update

## Overview

Updated `sietch/scripts/generate_service_docs.py` to automatically document available configuration overrides for each service. This makes users aware of optional configurations they can enable.

## Changes Made

### 1. Enhanced ServiceDocGenerator Class

Added support for scanning and documenting override files:

#### New Attributes
- `self.overrides_available_dir`: Path to the `overrides-available/` directory

#### New Methods

**`find_service_overrides(service_name: str) -> List[Path]`**
- Scans `overrides-available/` for files matching pattern `{service}*.yml`
- Handles game services by stripping `games-` prefix
- Returns sorted list of override file paths

**`analyze_override(override_path: Path) -> Dict`**
- Parses override YAML file to extract:
  - Volumes added/modified
  - Services added/modified
  - Environment variables added/modified
  - Comments from file header
- Returns structured analysis dictionary

**`infer_override_purpose(analysis: Dict) -> str`**
- Intelligently infers override purpose from filename and content
- Handles patterns including:
  - **NFS mounts**: `*-nfs.yml` - "Configures NFS volume mounts for remote storage"
  - **Dedicated databases**: `*-dedicated-redis.yml`, `*-dedicated-postgres.yml`, etc.
  - **Database configs**: `*-postgres.yml`, `*-mariadb.yml`, etc.
  - **Hardware acceleration**: `*-nvidia.yml`, `*-quicksync.yml`, `*-amd.yml`, `*-cpu.yml`
  - **Integrations**: `*-adguard.yml`, `*-dynmap.yml`
  - **Other**: `*-extra.yml` - "Provides additional configuration options"
- Uses file comments as the primary source when available

**`format_override_section(overrides: List[Dict]) -> str`**
- Formats override information as markdown
- Creates user-friendly documentation with:
  - Purpose description
  - List of changes (volumes, services, env vars)
  - Usage instructions with `make enable-override` command
  - Link to view override file on GitHub

### 2. Updated Documentation Generation

Modified `generate_markdown()` method to:
1. Find service-specific overrides
2. Analyze each override file
3. Insert "Available Overrides" section before "Quick Start" section

### 3. Documentation Format

The generated override section follows this format:

```markdown
## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### override-name

**Purpose**: Brief description of what this override does

**Changes**:
- **Adds/modifies volumes**: `volume-1`, `volume-2`
- **Adds/modifies services**: `service-1`, `service-2`
- **Adds/modifies environment variables**: `VAR_1`, `VAR_2`

**Usage**:
```bash
make enable-override override-name
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/override-name.yml)
```

## Override Patterns Supported

The script intelligently recognizes and documents these override patterns:

### Storage Patterns
- `{service}-nfs.yml` - NFS volume mounts for remote storage
- `{service}-nfs-cpu.yml` - NFS mounts for CPU-based setup
- `{service}-nfs-nvidia.yml` - NFS mounts for NVIDIA GPU setup

### Database Patterns
- `{service}-dedicated-postgres.yml` - Dedicated PostgreSQL container
- `{service}-dedicated-mariadb.yml` - Dedicated MariaDB container
- `{service}-dedicated-redis.yml` - Dedicated Redis container
- `{service}-dedicated-valkey.yml` - Dedicated Valkey container
- `{service}-postgres.yml` - PostgreSQL configuration
- `{service}-mariadb.yml` - MariaDB configuration
- `{service}-redis.yml` - Redis configuration

### Hardware Acceleration Patterns
- `{service}-nvidia.yml` - NVIDIA GPU hardware acceleration
- `{service}-amd.yml` - AMD GPU hardware acceleration
- `{service}-quicksync.yml` - Intel QuickSync hardware acceleration
- `{service}-cpu.yml` - CPU-based processing optimization

### Integration Patterns
- `{service}-adguard.yml` - AdGuard Home integration
- `{service}-dynmap.yml` - Dynmap web map (for Minecraft)

### Other Patterns
- `{service}-extra.yml` - Additional configuration options

## Statistics

- **Total override files**: 109 files in `overrides-available/`
- **Services with overrides**: 79 unique services
- **Common override types**:
  - NFS storage: ~40+ overrides
  - Dedicated databases: ~25+ overrides
  - Hardware acceleration: ~10+ overrides
  - Other configurations: ~34+ overrides

## Usage

To regenerate all service documentation with override information:

```bash
# From the onramp root directory
python3 sietch/scripts/generate_service_docs.py
```

This will:
1. Scan all services in `services-available/`
2. Find matching overrides in `overrides-available/`
3. Generate/update markdown files in `services-docs/`
4. Include override documentation for services that have them

## Example Output

See `EXAMPLE_OVERRIDE_SECTION.md` for examples of what the generated override documentation looks like for various services including:
- Single override (audiobookshelf)
- Multiple overrides (bazarr)
- Database overrides (booklore)

## Benefits

1. **Discoverability**: Users can easily see what optional configurations are available
2. **Clear usage**: Each override includes copy-paste commands to enable it
3. **Transparency**: Links to actual override files for detailed inspection
4. **Intelligent inference**: Purpose descriptions help users understand what each override does
5. **Comprehensive**: Covers all 109 override files across 79 services

## Files Modified

- `sietch/scripts/generate_service_docs.py` - Main documentation generator script

## Files Created (for reference)

- `EXAMPLE_OVERRIDE_SECTION.md` - Example output documentation
- `OVERRIDE_DOCUMENTATION_UPDATE.md` - This summary document
- `test_override_parsing.py` - Test script for verifying override parsing logic

## Next Steps

To apply these updates to your service documentation:

1. Run the documentation generator:
   ```bash
   cd /path/to/onramp
   python3 sietch/scripts/generate_service_docs.py
   ```

2. Review generated documentation in `services-docs/` directory

3. Commit the updated documentation files

4. Optionally test with a specific service:
   ```bash
   python3 test_override_parsing.py
   ```

## Implementation Notes

- The script gracefully handles missing override directories
- Comments in override files are used as the primary source for purpose descriptions
- Filename patterns provide fallback purpose inference
- Services without overrides are unaffected (no override section added)
- The override section appears between "Configuration" and "Quick Start" sections
