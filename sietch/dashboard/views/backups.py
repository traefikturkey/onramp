"""Backup management views."""

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def backup_list(request: Request):
    """Backup management page."""
    templates = request.app.state.templates
    base_dir = request.app.state.services._manager.base_dir
    backup_dir = base_dir / "backups"

    backups = []
    total_size = 0

    if backup_dir.exists():
        for f in sorted(backup_dir.iterdir(), reverse=True):
            if f.is_file() and f.suffix in (".tar", ".gz", ".tgz", ".zip"):
                stat = f.stat()
                backups.append({
                    "name": f.name,
                    "size": stat.st_size,
                    "size_human": _format_size(stat.st_size),
                    "created": datetime.fromtimestamp(stat.st_mtime),
                })
                total_size += stat.st_size

    return templates.TemplateResponse(
        "backups/index.html",
        {
            "request": request,
            "backups": backups,
            "total_size": _format_size(total_size),
            "backup_count": len(backups),
        },
    )


def _format_size(size_bytes: int) -> str:
    """Format bytes to human readable size."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"
