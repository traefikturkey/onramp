"""System management views."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def system_home(request: Request):
    """System overview page."""
    templates = request.app.state.templates
    docker = request.app.state.docker

    # Get Docker info
    docker_info = {}
    try:
        info = docker.client.info()
        docker_info = {
            "version": info.get("ServerVersion", "unknown"),
            "os": info.get("OperatingSystem", "unknown"),
            "arch": info.get("Architecture", "unknown"),
            "cpus": info.get("NCPU", 0),
            "memory": info.get("MemTotal", 0),
            "memory_human": _format_size(info.get("MemTotal", 0)),
            "containers": info.get("Containers", 0),
            "images": info.get("Images", 0),
        }
    except Exception:
        pass

    return templates.TemplateResponse(
        "system/index.html",
        {
            "request": request,
            "docker_info": docker_info,
        },
    )


@router.get("/dns", response_class=HTMLResponse)
async def dns_management(request: Request):
    """DNS management page."""
    templates = request.app.state.templates

    return templates.TemplateResponse(
        "system/dns.html",
        {"request": request},
    )


@router.get("/database", response_class=HTMLResponse)
async def database_management(request: Request):
    """Database management page."""
    templates = request.app.state.templates

    return templates.TemplateResponse(
        "system/database.html",
        {"request": request},
    )


def _format_size(size_bytes: int) -> str:
    """Format bytes to human readable size."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"
