#!/bin/bash
# OnRamp Recovery Script v2.0
# Fixes git state after main branch force-push while preserving .env files
# Safe to run multiple times (idempotent)
#
# Usage: bash <(curl -fsSL https://raw.githubusercontent.com/traefikturkey/onramp/main/recovery-v2.sh)

set -euo pipefail

VERSION="2.0"
BACKUP_DIR="/tmp/onramp-env-backup-$$"
FINAL_BACKUP_DIR="/tmp/onramp-env-backup"
ENV_DIR="services-enabled"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}✓${NC} $1"; }
log_warn()  { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }
log_step()  { echo -e "\n${GREEN}==>${NC} $1"; }

die() {
    log_error "$1"
    exit 1
}

cleanup() {
    if [[ -d "$BACKUP_DIR" ]] && [[ ! -d "$FINAL_BACKUP_DIR" ]]; then
        mv "$BACKUP_DIR" "$FINAL_BACKUP_DIR" 2>/dev/null || true
    fi
}
trap cleanup EXIT

echo ""
echo -e "${GREEN}OnRamp Recovery Script v${VERSION}${NC}"
echo "========================================"

#######################################
# PREFLIGHT CHECKS
#######################################
log_step "Running preflight checks..."

if ! git rev-parse --git-dir &>/dev/null; then
    die "Not in a git repository. cd to your onramp directory first."
fi

if [[ ! -d "services-available" ]] || [[ ! -f "Makefile" ]]; then
    die "This doesn't look like an onramp repo. Missing services-available/ or Makefile."
fi

CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")
if [[ -z "$CURRENT_BRANCH" ]]; then
    log_warn "Detached HEAD state detected"
elif [[ "$CURRENT_BRANCH" != "main" ]]; then
    log_warn "On branch '$CURRENT_BRANCH', not 'main'"
fi

log_info "Preflight checks passed"

#######################################
# BACKUP .ENV FILES
#######################################
log_step "Backing up .env files..."

ENV_FILES_FOUND=0
mkdir -p "$BACKUP_DIR"

# First priority: backup from services-enabled/ if files exist there
if [[ -d "$ENV_DIR" ]]; then
    for env_file in "$ENV_DIR"/.env "$ENV_DIR"/.env.*; do
        if [[ -f "$env_file" ]] && [[ ! "$env_file" =~ \.example$ ]]; then
            cp "$env_file" "$BACKUP_DIR/"
            log_info "Backed up: $env_file"
            ((ENV_FILES_FOUND++)) || true
        fi
    done
fi

# Second priority: check existing backup location
if [[ $ENV_FILES_FOUND -eq 0 ]] && [[ -d "$FINAL_BACKUP_DIR" ]]; then
    for env_file in "$FINAL_BACKUP_DIR"/.env "$FINAL_BACKUP_DIR"/.env.*; do
        if [[ -f "$env_file" ]] && [[ ! "$env_file" =~ \.example$ ]]; then
            cp "$env_file" "$BACKUP_DIR/"
            log_info "Found in previous backup: $(basename "$env_file")"
            ((ENV_FILES_FOUND++)) || true
        fi
    done
fi

# Third priority: check /tmp/env-backup (from the original fix script)
if [[ $ENV_FILES_FOUND -eq 0 ]] && [[ -d "/tmp/env-backup" ]]; then
    for env_file in /tmp/env-backup/.env /tmp/env-backup/.env.*; do
        if [[ -f "$env_file" ]] && [[ ! "$env_file" =~ \.example$ ]]; then
            cp "$env_file" "$BACKUP_DIR/"
            log_info "Found in /tmp/env-backup: $(basename "$env_file")"
            ((ENV_FILES_FOUND++)) || true
        fi
    done
fi

if [[ $ENV_FILES_FOUND -eq 0 ]]; then
    log_warn "No .env files found to backup!"
    echo ""
    read -p "Continue anyway? Your .env files may be lost! (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        die "Aborted by user. Find your .env files first."
    fi
else
    log_info "Backed up $ENV_FILES_FOUND .env file(s) to $BACKUP_DIR"
    rm -rf "$FINAL_BACKUP_DIR"
    mv "$BACKUP_DIR" "$FINAL_BACKUP_DIR"
    BACKUP_DIR="$FINAL_BACKUP_DIR"
fi

#######################################
# FIX GIT STATE
#######################################
log_step "Fixing git state..."

# Remove conflicting scripts if untracked
for conflict_file in "fix-env-pull.sh" "recovery-v2.sh"; do
    if [[ -f "$conflict_file" ]]; then
        if git ls-files --error-unmatch "$conflict_file" &>/dev/null; then
            log_info "$conflict_file is tracked, leaving alone"
        else
            rm -f "$conflict_file"
            log_info "Removed untracked $conflict_file"
        fi
    fi
done

log_info "Fetching from origin..."
if ! git fetch origin; then
    die "Failed to fetch from origin. Check your network connection."
fi

# Determine target branch
TARGET_BRANCH=""
if git rev-parse --verify origin/main &>/dev/null; then
    TARGET_BRANCH="main"
elif git rev-parse --verify origin/master &>/dev/null; then
    TARGET_BRANCH="master"
else
    die "Could not find origin/main or origin/master"
fi

log_info "Target branch: $TARGET_BRANCH"

LOCAL_HEAD=$(git rev-parse HEAD 2>/dev/null || echo "none")
REMOTE_HEAD=$(git rev-parse "origin/$TARGET_BRANCH" 2>/dev/null || echo "none")

if [[ "$LOCAL_HEAD" == "$REMOTE_HEAD" ]]; then
    log_info "Already up to date with origin/$TARGET_BRANCH"
else
    if ! git diff --quiet || ! git diff --cached --quiet; then
        log_warn "Stashing uncommitted changes..."
        git stash push -m "onramp-recovery-$(date +%s)" || true
    fi

    log_info "Resetting to origin/$TARGET_BRANCH..."
    if ! git checkout "$TARGET_BRANCH" 2>/dev/null; then
        git checkout -b "$TARGET_BRANCH" "origin/$TARGET_BRANCH" 2>/dev/null || true
    fi

    if ! git reset --hard "origin/$TARGET_BRANCH"; then
        die "Failed to reset to origin/$TARGET_BRANCH"
    fi

    log_info "Reset to $(git rev-parse --short HEAD)"
fi

#######################################
# RESTORE .ENV FILES
#######################################
log_step "Restoring .env files..."

RESTORED=0
if [[ -d "$FINAL_BACKUP_DIR" ]]; then
    mkdir -p "$ENV_DIR"
    for env_file in "$FINAL_BACKUP_DIR"/.env "$FINAL_BACKUP_DIR"/.env.*; do
        if [[ -f "$env_file" ]]; then
            cp "$env_file" "$ENV_DIR/"
            log_info "Restored: $(basename "$env_file")"
            ((RESTORED++)) || true
        fi
    done
fi

if [[ $RESTORED -eq 0 ]] && [[ $ENV_FILES_FOUND -gt 0 ]]; then
    log_warn "Expected to restore files but none were found in backup!"
fi

#######################################
# VERIFY
#######################################
log_step "Verifying..."

if git diff --quiet && git diff --cached --quiet; then
    log_info "Git working tree is clean"
else
    log_warn "Git working tree has changes (this may be expected for .env files)"
fi

FINAL_BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")
if [[ "$FINAL_BRANCH" == "$TARGET_BRANCH" ]]; then
    log_info "On branch: $TARGET_BRANCH"
else
    log_warn "On branch: $FINAL_BRANCH (expected $TARGET_BRANCH)"
fi

ENV_COUNT=$(find "$ENV_DIR" -maxdepth 1 -name '.env*' ! -name '*.example' 2>/dev/null | wc -l)
log_info "Found $ENV_COUNT .env file(s) in $ENV_DIR"

echo ""
log_info "Current commit: $(git log --oneline -1)"

#######################################
# DONE
#######################################
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Recovery complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Backup location: $FINAL_BACKUP_DIR"
echo ""
echo "Next steps:"
echo "  1. Verify your services: make list-enabled"
echo "  2. Check your config:    ls -la services-enabled/.env*"
echo "  3. Start services:       make up"
echo ""
