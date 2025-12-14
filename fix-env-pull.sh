#!/bin/bash
# Quick fix for .env files being deleted on git pull
# Run this in your onramp directory before pulling

set -e

echo "🔧 Fixing .env file tracking issue..."
echo ""

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ] || [ ! -d "services-enabled" ]; then
  echo "❌ Error: Please run this from the onramp directory"
  exit 1
fi

# Backup existing .env files
echo "📦 Backing up .env files..."
mkdir -p /tmp/onramp-env-backup
for file in services-enabled/.env services-enabled/.env.* ; do
  if [ -f "$file" ] && [ "$file" != "services-enabled/.env.example" ]; then
    cp "$file" /tmp/onramp-env-backup/ 2>/dev/null || true
    echo "  ✅ Backed up: $file"
  fi
done

# Remove from git index (won't delete files)
echo ""
echo "🗑️  Removing .env files from git index..."
git rm --cached services-enabled/.env* 2>/dev/null || echo "  (files not in index)"

# Reset any staged changes
echo ""
echo "♻️  Resetting git index..."
git reset --hard HEAD

# Pull latest changes
echo ""
echo "⬇️  Pulling latest changes..."
git pull

# Restore backups if any files are missing
echo ""
echo "🔄 Checking for missing .env files..."
restored=false
for backup in /tmp/onramp-env-backup/.env* ; do
  if [ -f "$backup" ]; then
    filename=$(basename "$backup")
    target="services-enabled/$filename"
    if [ ! -f "$target" ]; then
      cp "$backup" "$target"
      echo "  ✅ Restored: $target"
      restored=true
    fi
  fi
done

if [ "$restored" = false ]; then
  echo "  ✅ All .env files present"
fi

# Verify
echo ""
echo "📋 Current .env files:"
ls -lh services-enabled/.env* 2>/dev/null || echo "  No .env files found"

echo ""
echo "✅ Fix complete!"
echo ""
echo "Your .env files are safe and will no longer be deleted on pull."
