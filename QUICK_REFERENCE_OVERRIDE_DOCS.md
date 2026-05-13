# Quick Reference: Override Documentation Feature

## What Was Updated

The service documentation generator (`sietch/scripts/generate_service_docs.py`) now automatically documents available configuration overrides for each service.

## How It Works

### 1. Override Detection
```python
override_paths = self.find_service_overrides(service_name)
```
- Searches `overrides-available/` for files matching `{service}*.yml`
- Handles game services by stripping `games-` prefix

### 2. Override Analysis
```python
overrides = [self.analyze_override(p) for p in override_paths]
```
- Extracts what each override modifies (volumes, services, env vars)
- Reads file comments for purpose description
- Infers purpose from filename patterns

### 3. Documentation Generation
```python
override_section = self.format_override_section(overrides)
md.append(override_section)
```
- Formats as markdown
- Includes purpose, changes, usage, and configuration link
- Inserted before "Quick Start" section

## Key Features

### Intelligent Purpose Inference

The script recognizes these patterns:

| Pattern | Example | Purpose Description |
|---------|---------|-------------------|
| `*-nfs.yml` | `audiobookshelf-nfs.yml` | Configures NFS volume mounts for remote storage |
| `*-nfs-cpu.yml` | `frigate-cpu-nfs.yml` | Configures NFS volume mounts for CPU-based setup |
| `*-nfs-nvidia.yml` | `frigate-nvidia-nfs.yml` | Configures NFS volume mounts for NVIDIA GPU setup |
| `*-dedicated-redis.yml` | `authentik-dedicated-redis.yml` | Adds a dedicated Redis container for this service |
| `*-dedicated-postgres.yml` | `docmost-dedicated-postgres.yml` | Adds a dedicated PostgreSQL database container |
| `*-dedicated-mariadb.yml` | `booklore-dedicated-mariadb.yml` | Adds a dedicated MariaDB database container |
| `*-postgres.yml` | `healthchecks-postgres.yml` | Configures PostgreSQL database for this service |
| `*-nvidia.yml` | `jellyfin-nvidia.yml` | Enables NVIDIA GPU hardware acceleration |
| `*-quicksync.yml` | `jellyfin-quicksync.yml` | Enables Intel QuickSync hardware acceleration |
| `*-amd.yml` | `ollama-amd.yml` | Enables AMD GPU hardware acceleration |
| `*-cpu.yml` | `frigate-cpu.yml` | Configuration optimized for CPU-based processing |
| `*-adguard.yml` | `joyride-adguard.yml` | Integrates with AdGuard Home |
| `*-dynmap.yml` | `minecraft-dynmap.yml` | Enables Dynmap web map for Minecraft |
| `*-extra.yml` | `bazarr-extra.yml` | Provides additional configuration options |

### Comment Extraction

Comments from override files are used as the primary source for purpose descriptions:

```yaml
# Override to use dedicated PostgreSQL database for healthchecks
# This is for backward compatibility with existing deployments
```

The first meaningful comment becomes the purpose description.

### Change Detection

The script automatically detects and lists:
- **Volumes**: All volume definitions in the override
- **Services**: All service definitions added/modified
- **Environment Variables**: All env vars added/modified

## Output Example

```markdown
## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### jellyfin-nvidia

**Purpose**: Enables NVIDIA GPU hardware acceleration

**Changes**:
- **Adds/modifies services**: `jellyfin`
- **Adds/modifies environment variables**: `PUID`, `PGID`, `TZ`, `JELLYFIN_PublishedServerUrl`, `NVIDIA_DRIVER_CAPABILITIES`, `NVIDIA_VISIBLE_DEVICES`

**Usage**:
```bash
make enable-override jellyfin-nvidia
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/jellyfin-nvidia.yml)
```

## Running the Generator

```bash
# From the onramp root directory
python3 sietch/scripts/generate_service_docs.py
```

This will regenerate all service documentation in `services-docs/` with override information.

## Statistics

- **Total Overrides**: 109 files
- **Services with Overrides**: 79 services
- **Documentation Updated**: All service docs in `services-docs/`

## Testing

Use the test script to verify override parsing:

```bash
python3 test_override_parsing.py
```

This will show:
- Found overrides for test service
- Analyzed information (purpose, volumes, services, env vars)
- Formatted output section

## Implementation Details

### Methods Added

1. `find_service_overrides(service_name)` - Finds override files
2. `analyze_override(override_path)` - Parses and analyzes override
3. `infer_override_purpose(analysis)` - Determines purpose from patterns
4. `format_override_section(overrides)` - Formats as markdown

### Integration Point

The override section is inserted in `generate_markdown()` method between:
- **Before**: Quick Start section
- **After**: Configuration section (volumes, networks, labels, dependencies)

### Error Handling

- Gracefully handles missing `overrides-available/` directory
- Catches and logs parsing errors
- Services without overrides simply don't get an override section
- Malformed override files produce warnings but don't break generation

## Files to Review

1. `sietch/scripts/generate_service_docs.py` - Main implementation
2. `OVERRIDE_DOCUMENTATION_UPDATE.md` - Detailed update documentation
3. `EXAMPLE_OVERRIDE_SECTION.md` - Output examples
4. `validate_override_logic.md` - Test cases and validation
5. `test_override_parsing.py` - Test script

## Benefits

✓ **Discoverability** - Users can see available overrides
✓ **Clear Usage** - Copy-paste commands provided
✓ **Comprehensive** - Covers all 109 overrides
✓ **Intelligent** - Smart purpose inference
✓ **Transparent** - Links to actual override files
✓ **Automatic** - No manual documentation needed
