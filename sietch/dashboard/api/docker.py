"""Docker container management API routes."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()


class ActionResponse(BaseModel):
    success: bool
    message: str


@router.get("/containers")
async def list_containers(request: Request, all: bool = True):
    """List all containers."""
    docker = request.app.state.docker
    containers = docker.list_containers(all=all)
    return {"containers": containers, "count": len(containers)}


@router.get("/containers/{name}")
async def get_container(request: Request, name: str):
    """Get a specific container by name."""
    docker = request.app.state.docker
    container = docker.get_container(name)

    if not container:
        raise HTTPException(status_code=404, detail=f"Container '{name}' not found")

    return container


@router.post("/containers/{name}/start")
async def start_container(request: Request, name: str) -> ActionResponse:
    """Start a container."""
    docker = request.app.state.docker
    success, message = docker.start(name)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return ActionResponse(success=success, message=message)


@router.post("/containers/{name}/stop")
async def stop_container(request: Request, name: str) -> ActionResponse:
    """Stop a container."""
    docker = request.app.state.docker
    success, message = docker.stop(name)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return ActionResponse(success=success, message=message)


@router.post("/containers/{name}/restart")
async def restart_container(request: Request, name: str) -> ActionResponse:
    """Restart a container."""
    docker = request.app.state.docker
    success, message = docker.restart(name)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return ActionResponse(success=success, message=message)


@router.get("/containers/{name}/logs")
async def get_container_logs(request: Request, name: str, tail: int = 100):
    """Get container logs."""
    docker = request.app.state.docker
    logs = docker.get_logs(name, tail=tail)
    return {"name": name, "logs": logs}


@router.get("/containers/{name}/stats")
async def get_container_stats(request: Request, name: str):
    """Get container resource stats."""
    docker = request.app.state.docker
    stats = docker.get_stats(name)

    if not stats:
        raise HTTPException(status_code=404, detail=f"Stats not available for '{name}'")

    return {"name": name, **stats}
