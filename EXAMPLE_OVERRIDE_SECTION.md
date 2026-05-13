# Example Override Section Output

This is what the generated override section would look like for the audiobookshelf service:

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### audiobookshelf-nfs

**Purpose**: Configures NFS volume mounts for remote storage

**Changes**:
- **Adds/modifies volumes**: `audiobookshelf-nfs-media`, `audiobookshelf-nfs-podcasts`
- **Adds/modifies services**: `audiobookshelf`

**Usage**:
```bash
make enable-override audiobookshelf-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/audiobookshelf-nfs.yml)

---

# Example for a service with multiple overrides (bazarr)

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### bazarr-extra

**Purpose**: Provides additional configuration options

**Changes**:
- **Adds/modifies volumes**: `bazarr-nfs-movies`, `bazarr-nfs-shows`, `bazarr-nfs-extra`
- **Adds/modifies services**: `bazarr`

**Usage**:
```bash
make enable-override bazarr-extra
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/bazarr-extra.yml)

### bazarr-nfs

**Purpose**: Configures NFS volume mounts for remote storage

**Changes**:
- **Adds/modifies volumes**: `bazarr-nfs-movies`, `bazarr-nfs-shows`, `bazarr-nfs-extra`
- **Adds/modifies services**: `bazarr`

**Usage**:
```bash
make enable-override bazarr-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/bazarr-nfs.yml)

---

# Example for a service with dedicated database override (booklore)

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### booklore-dedicated-mariadb

**Purpose**: Adds a dedicated MariaDB database container for this service

**Changes**:
- **Adds/modifies services**: `booklore`, `booklore-db`
- **Adds/modifies environment variables**: `DATABASE_URL`, `PUID`, `PGID`, `TZ`, `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`

**Usage**:
```bash
make enable-override booklore-dedicated-mariadb
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/booklore-dedicated-mariadb.yml)

### booklore-nfs

**Purpose**: Configures NFS volume mounts for remote storage

**Changes**:
- **Adds/modifies volumes**: `booklore-nfs-books`
- **Adds/modifies services**: `booklore`

**Usage**:
```bash
make enable-override booklore-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/booklore-nfs.yml)
