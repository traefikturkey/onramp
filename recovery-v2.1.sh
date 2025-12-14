#!/bin/bash
# OnRamp Recovery Script v2.1
# Fixes git state after main branch force-push while preserving .env files
# Also backs up modified tracked files and untracked files in key directories
# Safe to run multiple times (idempotent)
#
# Usage: bash <(curl -fsSL https://raw.githubusercontent.com/traefikturkey/onramp/main/recovery-v2.1.sh)

set -euo pipefail

VERSION="2.1"
BACKUP_DIR="/tmp/onramp-backup-$$"
FINAL_BACKUP_DIR="/tmp/onramp-backup"
ENV_DIR="services-enabled"
CHANGES_BACKUP_DIR="$FINAL_BACKUP_DIR/modified-files"

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
mkdir -p "$BACKUP_DIR/env-files"

# First priority: backup from services-enabled/ if files exist there
if [[ -d "$ENV_DIR" ]]; then
    for env_file in "$ENV_DIR"/.env "$ENV_DIR"/.env.*; do
        if [[ -f "$env_file" ]] && [[ ! "$env_file" =~ \.example$ ]]; then
            cp "$env_file" "$BACKUP_DIR/env-files/"
            log_info "Backed up: $env_file"
            ((ENV_FILES_FOUND++)) || true
        fi
    done
fi

# Second priority: check existing backup location
if [[ $ENV_FILES_FOUND -eq 0 ]] && [[ -d "$FINAL_BACKUP_DIR/env-files" ]]; then
    for env_file in "$FINAL_BACKUP_DIR/env-files"/.env "$FINAL_BACKUP_DIR/env-files"/.env.*; do
        if [[ -f "$env_file" ]] && [[ ! "$env_file" =~ \.example$ ]]; then
            cp "$env_file" "$BACKUP_DIR/env-files/"
            log_info "Found in previous backup: $(basename "$env_file")"
            ((ENV_FILES_FOUND++)) || true
        fi
    done
fi

# Third priority: check /tmp/env-backup (from the original fix script)
if [[ $ENV_FILES_FOUND -eq 0 ]] && [[ -d "/tmp/env-backup" ]]; then
    for env_file in /tmp/env-backup/.env /tmp/env-backup/.env.*; do
        if [[ -f "$env_file" ]] && [[ ! "$env_file" =~ \.example$ ]]; then
            cp "$env_file" "$BACKUP_DIR/env-files/"
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
    log_info "Backed up $ENV_FILES_FOUND .env file(s)"
fi

#######################################
# BACKUP MODIFIED TRACKED FILES
#######################################
log_step "Checking for other local changes..."

MODIFIED_FILES_COUNT=0
mkdir -p "$BACKUP_DIR/modified-files"

# Get list of modified tracked files (both staged and unstaged)
MODIFIED_FILES=$(git diff --name-only HEAD 2>/dev/null || true)
STAGED_FILES=$(git diff --cached --name-only 2>/dev/null || true)
ALL_CHANGED_FILES=$(echo -e "$MODIFIED_FILES\n$STAGED_FILES" | sort -u | grep -v '^$' || true)

if [[ -n "$ALL_CHANGED_FILES" ]]; then
    log_warn "Found modified tracked files:"
    while IFS= read -r file; do
        if [[ -n "$file" ]] && [[ -f "$file" ]]; then
            # Create directory structure in backup
            mkdir -p "$BACKUP_DIR/modified-files/$(dirname "$file")"
            cp "$file" "$BACKUP_DIR/modified-files/$file"
            echo "    - $file"
            ((MODIFIED_FILES_COUNT++)) || true
        fi
    done <<< "$ALL_CHANGED_FILES"
    log_info "Backed up $MODIFIED_FILES_COUNT modified file(s)"

    # Save the list of modified files for reference
    echo "$ALL_CHANGED_FILES" > "$BACKUP_DIR/modified-files.txt"
else
    log_info "No modified tracked files found"
fi

# Check for untracked files in key directories
UNTRACKED_IMPORTANT=""
for dir in services-available overrides-available services-scaffold; do
    if [[ -d "$dir" ]]; then
        UNTRACKED_IN_DIR=$(git ls-files --others --exclude-standard "$dir" 2>/dev/null || true)
        if [[ -n "$UNTRACKED_IN_DIR" ]]; then
            UNTRACKED_IMPORTANT="${UNTRACKED_IMPORTANT}${UNTRACKED_IN_DIR}\n"
        fi
    fi
done

if [[ -n "$UNTRACKED_IMPORTANT" ]]; then
    log_warn "Found untracked files in important directories:"
    mkdir -p "$BACKUP_DIR/untracked-files"
    while IFS= read -r file; do
        if [[ -n "$file" ]] && [[ -f "$file" ]]; then
            mkdir -p "$BACKUP_DIR/untracked-files/$(dirname "$file")"
            cp "$file" "$BACKUP_DIR/untracked-files/$file"
            echo "    - $file"
        fi
    done <<< "$(echo -e "$UNTRACKED_IMPORTANT")"
    log_info "Backed up untracked files"
fi

# Finalize backup directory
rm -rf "$FINAL_BACKUP_DIR"
mv "$BACKUP_DIR" "$FINAL_BACKUP_DIR"
BACKUP_DIR="$FINAL_BACKUP_DIR"

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
if [[ -d "$FINAL_BACKUP_DIR/env-files" ]]; then
    mkdir -p "$ENV_DIR"
    for env_file in "$FINAL_BACKUP_DIR/env-files"/.env "$FINAL_BACKUP_DIR/env-files"/.env.*; do
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
# REPORT OTHER BACKED UP FILES
#######################################
if [[ -d "$FINAL_BACKUP_DIR/modified-files" ]] && [[ -f "$FINAL_BACKUP_DIR/modified-files.txt" ]]; then
    MODIFIED_COUNT=$(wc -l < "$FINAL_BACKUP_DIR/modified-files.txt" 2>/dev/null || echo "0")
    if [[ "$MODIFIED_COUNT" -gt 0 ]]; then
        log_warn "$MODIFIED_COUNT modified file(s) were backed up but NOT auto-restored"
        log_info "Review and restore manually from: $FINAL_BACKUP_DIR/modified-files/"
    fi
fi

if [[ -d "$FINAL_BACKUP_DIR/untracked-files" ]]; then
    UNTRACKED_COUNT=$(find "$FINAL_BACKUP_DIR/untracked-files" -type f 2>/dev/null | wc -l || echo "0")
    if [[ "$UNTRACKED_COUNT" -gt 0 ]]; then
        log_warn "$UNTRACKED_COUNT untracked file(s) were backed up"
        log_info "Review and restore manually from: $FINAL_BACKUP_DIR/untracked-files/"
    fi
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
echo "  - env-files/       : Your .env configuration files (auto-restored)"
echo "  - modified-files/  : Modified tracked files (review manually)"
echo "  - untracked-files/ : Untracked files from key directories"
echo ""
echo "Next steps:"
echo "  1. Verify your services: make list-enabled"
echo "  2. Check your config:    ls -la services-enabled/.env*"
echo "  3. Review any modified files that were backed up:"
echo "     ls -la $FINAL_BACKUP_DIR/modified-files/ 2>/dev/null"
echo "  4. Start services:       make up"
echo ""
