The big change is how environment files are handled. Instead of one giant `.env` file, things are now split into modular files under `services-enabled/`:

- `.env` — global stuff (cloudflare, domain, timezone, PUID/PGID)
- `.env.nfs` — NFS mount configs
- `.env.external` — external service proxying (proxmox, truenas, etc)
- `{service}.env` — per-service configs

**Migration is automatic** — whether you're coming from `master` (monolithic `.env`) or Sal's branch (`environments-enabled/`), it detects what you have and converts it. Backups go to `backups/.env.legacy` first obviously.

## Switching from `master` to `main`

```bash
# Stop current services
make down

# Create a full backup first (excludes media/) -- Probably gonna need to add sudo here (or sudo !! after).
tar --exclude='media' -czvf ~/onramp-backup-$(date +%Y%m%d).tar.gz .

# Fetch and switch to main
git fetch origin
git checkout main

# Run make (migration happens automatically)
make

# Verify your services are running
docker compose ps
```

If you want to preview the migration first:
```bash
make migrate-env-dry-run
```

## Other Changes

- **Sietch container** — new Python-based tooling for scaffolding and migration. Auto-builds when you run `make`, auto-rebuilds if `sietch/` files change.
- **Convention-based scaffolding** — drop a `*.template` file in `services-scaffold/{service}/` and it gets rendered to `etc/{service}/` on enable. No more manual config setup or maintaining `builders.mk`.
- **Consolidated directories** — killed `environments-available/` and `environments-enabled/`, everything lives in `services-enabled/` now.
- **Nuke vs disable** — `make disable-service` preserves your configs in `etc/`, `make nuke-service` wipes everything.

## New Commands

```bash
make edit-env <service>    # edit service env
make edit-env-onramp       # edit global config
make scaffold-list         # see available scaffolds
make migrate-env-dry-run   # test migration without changes
make sietch-shell          # debug inside the tool container
```

Currently dogfooding it on my setup and it worked to migrate my setup without issue.
