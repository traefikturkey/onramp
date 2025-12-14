# Fix: .env Files Being Deleted on Pull

## Problem

After a force push that removed `services-enabled/.env*` files from git tracking, these files are being deleted when running `git pull` on other machines.

## Root Cause

The files were previously tracked in git but were removed via force push. On other machines, git's index still has references to these files and tries to delete them during pull operations.

## Quick Fix (Copy-Paste)

Run this command on affected machines **before pulling**:

```bash
cd /apps/onramp && \
  mkdir -p /tmp/env-backup && \
  cp services-enabled/.env* /tmp/env-backup/ 2>/dev/null || true && \
  git rm --cached services-enabled/.env* 2>/dev/null || true && \
  git reset --hard HEAD && \
  git pull && \
  cp /tmp/env-backup/.env* services-enabled/ 2>/dev/null || true && \
  echo "✅ Fix complete - .env files preserved"
```

Or download and run the automated script:

```bash
cd /apps/onramp
curl -O https://raw.githubusercontent.com/traefikturkey/onramp/main/fix-env-pull.sh
chmod +x fix-env-pull.sh
./fix-env-pull.sh
```

### Step-by-Step Explanation

1. **Remove from cache**: `git rm --cached services-enabled/.env*` removes the files from git's index without deleting them from disk
2. **Reset index**: `git reset --hard HEAD` cleans up the index
3. **Pull safely**: `git pull` now works without trying to delete the files

## Prevention

The repository now includes:

- **`.gitignore`** patterns:
  ```
  services-enabled/*.env
  services-enabled/*.env.*
  ```

- **`.gitattributes`** entries:
  ```
  services-enabled/.env export-ignore
  services-enabled/.env.* export-ignore
  ```

These ensure the files are never tracked or exported, even if accidentally added.

## Verify Fix

After pulling, verify the files still exist:

```bash
ls -la services-enabled/.env*
```

You should see:
- `services-enabled/.env`
- `services-enabled/.env.example` (tracked)
- `services-enabled/.env.external`
- `services-enabled/.env.nfs`

## Alternative: Nuclear Option

If the simple fix doesn't work, backup and restore:

```bash
# Backup .env files
cp services-enabled/.env /tmp/
cp services-enabled/.env.external /tmp/
cp services-enabled/.env.nfs /tmp/

# Reset repository
git fetch origin
git reset --hard origin/main

# Restore .env files
cp /tmp/.env services-enabled/
cp /tmp/.env.external services-enabled/
cp /tmp/.env.nfs services-enabled/
```
