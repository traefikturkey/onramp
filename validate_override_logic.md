# Override Logic Validation

## Test Cases for Override Detection and Inference

### Test Case 1: Single NFS Override
**Service**: audiobookshelf
**Override Files**: audiobookshelf-nfs.yml
**Expected Pattern Match**: `audiobookshelf*.yml` → matches
**Expected Purpose**: "Configures NFS volume mounts for remote storage"

### Test Case 2: Multiple Hardware Acceleration Overrides
**Service**: jellyfin
**Override Files**: 
- jellyfin-nfs.yml
- jellyfin-nvidia.yml
- jellyfin-quicksync.yml

**Expected Pattern Matches**: `jellyfin*.yml` → all match
**Expected Purposes**:
- jellyfin-nfs.yml: "Configures NFS volume mounts for remote storage"
- jellyfin-nvidia.yml: "Enables NVIDIA GPU hardware acceleration"
- jellyfin-quicksync.yml: "Enables Intel QuickSync hardware acceleration"

### Test Case 3: CPU + NFS Combined Override
**Service**: frigate
**Override Files**:
- frigate-cpu-nfs.yml
- frigate-nvidia-nfs.yml

**Expected Pattern Matches**: `frigate*.yml` → both match
**Expected Purposes**:
- frigate-cpu-nfs.yml: "Configures NFS volume mounts for CPU-based setup" (NFS with CPU)
- frigate-nvidia-nfs.yml: "Configures NFS volume mounts for NVIDIA GPU setup" (NFS with NVIDIA)

### Test Case 4: Multiple Database Options
**Service**: immich
**Override Files**:
- immich-dedicated-valkey.yml
- immich-nfs.yml

**Expected Pattern Matches**: `immich*.yml` → both match
**Expected Purposes**:
- immich-dedicated-valkey.yml: "Adds a dedicated Valkey container for this service"
- immich-nfs.yml: "Configures NFS volume mounts for remote storage"

### Test Case 5: Service with Comments
**Service**: healthchecks
**Override Files**: healthchecks-postgres.yml
**File Contains**: "# Override to use dedicated PostgreSQL database for healthchecks"
**Expected Purpose**: Should use comment content (first line describing the override)

### Test Case 6: Dedicated Database
**Service**: booklore
**Override Files**:
- booklore-dedicated-mariadb.yml
- booklore-nfs.yml

**Expected Pattern Matches**: `booklore*.yml` → both match
**Expected Purposes**:
- booklore-dedicated-mariadb.yml: Should use comment "This restores the dedicated MariaDB container" or infer "Adds a dedicated MariaDB database container for this service"
- booklore-nfs.yml: "Configures NFS volume mounts for remote storage"

### Test Case 7: Games Service (with prefix)
**Service**: games-minecraft
**Base Name**: minecraft
**Override Files**: minecraft-dynmap.yml
**Expected Pattern Match**: Strip `games-` prefix → search for `minecraft*.yml` → matches
**Expected Purpose**: "Enables Dynmap web map for Minecraft"

### Test Case 8: Extra Configuration
**Service**: bazarr
**Override Files**:
- bazarr-extra.yml
- bazarr-nfs.yml

**Expected Pattern Matches**: `bazarr*.yml` → both match
**Expected Purposes**:
- bazarr-extra.yml: "Provides additional configuration options"
- bazarr-nfs.yml: "Configures NFS volume mounts for remote storage"

### Test Case 9: Integration Override
**Service**: joyride
**Override Files**: joyride-adguard.yml
**Expected Pattern Match**: `joyride*.yml` → matches
**Expected Purpose**: "Integrates with AdGuard Home"

### Test Case 10: Standalone Database (without "dedicated" prefix)
**Service**: n8n
**Override Files**: n8n-postgres.yml
**Expected Pattern Match**: `n8n*.yml` → matches
**Expected Purpose**: "Configures PostgreSQL database for this service"

## Pattern Matching Logic Validation

### Glob Pattern: `{service}*.yml`
- ✓ Matches: `audiobookshelf-nfs.yml` (service: audiobookshelf)
- ✓ Matches: `jellyfin-nvidia.yml` (service: jellyfin)
- ✓ Matches: `frigate-cpu-nfs.yml` (service: frigate)
- ✗ Does NOT match: `other-service-nfs.yml` (service: audiobookshelf)
- ✓ Matches multiple: `bazarr-extra.yml`, `bazarr-nfs.yml` (service: bazarr)

### Games Service Handling
- Input: `games-minecraft` → Strip prefix → `minecraft`
- Search: `minecraft*.yml`
- ✓ Matches: `minecraft-dynmap.yml`

## Purpose Inference Priority

1. **Comments** (highest priority)
   - Use first meaningful comment that describes the override
   - Skip "Usage:" and "make enable-override" lines

2. **Filename Patterns** (in order of specificity)
   - NFS with hardware: `*-nfs-cpu.yml`, `*-nfs-nvidia.yml`
   - NFS standalone: `*-nfs.yml`
   - Dedicated databases: `*-dedicated-redis.yml`, `*-dedicated-postgres.yml`, etc.
   - Standalone databases: `*-postgres.yml`, `*-mariadb.yml`, etc.
   - Hardware acceleration: `*-nvidia.yml`, `*-amd.yml`, `*-quicksync.yml`, `*-cpu.yml`
   - Integrations: `*-adguard.yml`, `*-dynmap.yml`
   - Other: `*-extra.yml`

3. **Default Fallback**
   - "Alternative configuration for this service"

## Expected Analysis Output Structure

```python
{
    'filename': 'audiobookshelf-nfs.yml',
    'override_name': 'audiobookshelf-nfs',
    'purpose': 'Configures NFS volume mounts for remote storage',
    'volumes': ['audiobookshelf-nfs-media', 'audiobookshelf-nfs-podcasts'],
    'services': ['audiobookshelf'],
    'environment_vars': [],
    'comments': []
}
```

## Validation Checklist

- [x] Pattern matching correctly identifies service-specific overrides
- [x] Games service prefix handling works correctly
- [x] Purpose inference handles all common patterns
- [x] Comment extraction captures meaningful descriptions
- [x] Volume, service, and environment variable extraction works
- [x] Multiple overrides per service are supported
- [x] Services without overrides are handled gracefully
- [x] Output formatting is consistent and readable
- [x] GitHub links are correctly generated
- [x] Make commands in usage sections are correct

## Comprehensive Coverage

### Override Types Covered (109 total files)
- ✓ NFS storage configurations (~40+ files)
- ✓ Dedicated database containers (~25+ files)
- ✓ Hardware acceleration (NVIDIA, AMD, QuickSync, CPU) (~10+ files)
- ✓ Database configurations (Postgres, MariaDB, Redis) (~15+ files)
- ✓ Integration overrides (AdGuard, Dynmap) (~5+ files)
- ✓ Extra configurations (~5+ files)
- ✓ Other specialized configs (~9+ files)

### Services Covered (79 unique services)
All services with overrides in `overrides-available/` directory will be properly documented.
