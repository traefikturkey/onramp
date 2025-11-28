"""Scaffold management API."""

import subprocess
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()


@router.get("/{name}")
async def get_scaffold_info(request: Request, name: str):
    """Get scaffold information for a service."""
    base_dir = request.app.state.services._manager.base_dir
    scaffold_dir = base_dir / "services-scaffold" / name

    if not scaffold_dir.exists():
        return {
            "service": name,
            "exists": False,
            "files": [],
            "has_manifest": False,
            "message": None,
        }

    files = []
    for f in scaffold_dir.rglob("*"):
        if f.is_file():
            rel_path = f.relative_to(scaffold_dir)
            file_type = "template" if f.suffix == ".template" else "static"
            if f.name == "scaffold.yml":
                file_type = "manifest"
            elif f.name == "MESSAGE.txt":
                file_type = "message"
            files.append({
                "path": str(rel_path),
                "type": file_type,
                "size": f.stat().st_size,
            })

    # Check for manifest
    has_manifest = (scaffold_dir / "scaffold.yml").exists()

    # Get MESSAGE.txt if exists
    message = None
    message_path = scaffold_dir / "MESSAGE.txt"
    if message_path.exists():
        message = message_path.read_text(encoding="utf-8")

    return {
        "service": name,
        "exists": True,
        "files": files,
        "has_manifest": has_manifest,
        "message": message,
    }


@router.get("/{name}/file/{file_path:path}")
async def get_scaffold_file(request: Request, name: str, file_path: str):
    """Get content of a scaffold file."""
    base_dir = request.app.state.services._manager.base_dir
    scaffold_dir = base_dir / "services-scaffold" / name
    full_path = scaffold_dir / file_path

    if not full_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

    # Security: ensure path is within scaffold dir
    try:
        full_path.resolve().relative_to(scaffold_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    content = full_path.read_text(encoding="utf-8")
    return {
        "service": name,
        "path": file_path,
        "content": content,
    }


@router.get("/{name}/generated")
async def get_generated_config(request: Request, name: str):
    """List generated config files in etc/<service>/."""
    base_dir = request.app.state.services._manager.base_dir
    etc_dir = base_dir / "etc" / name

    if not etc_dir.exists():
        return {"service": name, "exists": False, "files": []}

    files = []
    for f in etc_dir.rglob("*"):
        if f.is_file():
            rel_path = f.relative_to(etc_dir)
            files.append({
                "path": str(rel_path),
                "size": f.stat().st_size,
                "modified": f.stat().st_mtime,
            })

    return {"service": name, "exists": True, "files": files}


@router.post("/{name}/build")
async def run_scaffold_build(request: Request, name: str):
    """Run scaffold build for a service."""
    base_dir = request.app.state.services._manager.base_dir

    try:
        result = subprocess.run(
            ["make", "scaffold-build", name],
            cwd=str(base_dir),
            capture_output=True,
            text=True,
            timeout=60,
        )

        return {
            "success": result.returncode == 0,
            "service": name,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Scaffold build timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
