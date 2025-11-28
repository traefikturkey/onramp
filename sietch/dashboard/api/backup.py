"""Backup management API."""

import subprocess
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.get("")
async def list_backups(request: Request):
    """List available backups."""
    base_dir = request.app.state.services._manager.base_dir
    backup_dir = base_dir / "backups"

    if not backup_dir.exists():
        return {"backups": [], "count": 0, "total_size": 0}

    backups = []
    total_size = 0

    for f in sorted(backup_dir.iterdir(), reverse=True):
        if f.is_file() and f.suffix in (".tar", ".gz", ".tgz", ".zip"):
            stat = f.stat()
            backups.append({
                "name": f.name,
                "path": str(f),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
            total_size += stat.st_size

    return {"backups": backups, "count": len(backups), "total_size": total_size}


@router.post("/create")
async def create_backup(request: Request):
    """Create a new backup."""
    base_dir = request.app.state.services._manager.base_dir

    try:
        result = subprocess.run(
            ["make", "create-backup"],
            cwd=str(base_dir),
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes max
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Backup creation timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restore/{backup_name}")
async def restore_backup(request: Request, backup_name: str):
    """Restore from a backup."""
    base_dir = request.app.state.services._manager.base_dir
    backup_dir = base_dir / "backups"
    backup_path = backup_dir / backup_name

    if not backup_path.exists():
        raise HTTPException(status_code=404, detail=f"Backup not found: {backup_name}")

    try:
        result = subprocess.run(
            ["make", "restore-backup", f"BACKUP={backup_name}"],
            cwd=str(base_dir),
            capture_output=True,
            text=True,
            timeout=300,
        )

        return {
            "success": result.returncode == 0,
            "backup": backup_name,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Backup restore timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{backup_name}")
async def delete_backup(request: Request, backup_name: str):
    """Delete a backup file."""
    base_dir = request.app.state.services._manager.base_dir
    backup_dir = base_dir / "backups"
    backup_path = backup_dir / backup_name

    if not backup_path.exists():
        raise HTTPException(status_code=404, detail=f"Backup not found: {backup_name}")

    # Security: ensure file is in backup dir
    try:
        backup_path.resolve().relative_to(backup_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    backup_path.unlink()
    return {"success": True, "deleted": backup_name}
