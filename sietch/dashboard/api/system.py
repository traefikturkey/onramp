"""System health and status API routes."""

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health_check(request: Request):
    """Health check endpoint."""
    docker = request.app.state.docker
    docker_ok = docker.ping()

    return {
        "status": "healthy" if docker_ok else "degraded",
        "docker": docker_ok,
    }


@router.get("/stats")
async def system_stats(request: Request):
    """Get system-wide statistics."""
    docker = request.app.state.docker
    services_mgr = request.app.state.services

    containers = docker.list_containers(all=True)
    running = sum(1 for c in containers if c["status"] == "running")
    stopped = len(containers) - running

    available_count = len(services_mgr.get_available_names())
    enabled_count = len(services_mgr.get_enabled_names())

    return {
        "containers": {
            "total": len(containers),
            "running": running,
            "stopped": stopped,
        },
        "services": {
            "available": available_count,
            "enabled": enabled_count,
        },
    }


@router.get("/info")
async def system_info(request: Request):
    """Get Docker system info."""
    docker = request.app.state.docker

    try:
        info = docker.client.info()
        return {
            "docker_version": info.get("ServerVersion", "unknown"),
            "os": info.get("OperatingSystem", "unknown"),
            "architecture": info.get("Architecture", "unknown"),
            "cpus": info.get("NCPU", 0),
            "memory": info.get("MemTotal", 0),
            "containers": info.get("Containers", 0),
            "images": info.get("Images", 0),
        }
    except Exception as e:
        return {"error": str(e)}
