"""Service management API routes."""

from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.get("")
async def list_services(request: Request, enabled: bool = False, category: str = None):
    """List services with optional filtering."""
    services_mgr = request.app.state.services

    if enabled:
        services = services_mgr.list_enabled()
    elif category:
        services = services_mgr.filter_by_category(category)
    else:
        services = services_mgr.list_available()

    return {"services": services, "count": len(services)}


@router.get("/available")
async def list_available(request: Request):
    """List all available services."""
    services_mgr = request.app.state.services
    services = services_mgr.list_available()
    return {"services": services, "count": len(services)}


@router.get("/enabled")
async def list_enabled(request: Request):
    """List enabled services."""
    services_mgr = request.app.state.services
    services = services_mgr.list_enabled()
    return {"services": services, "count": len(services)}


@router.get("/games")
async def list_games(request: Request):
    """List available games."""
    services_mgr = request.app.state.services
    games = services_mgr.list_games()
    return {"games": games, "count": len(games)}


@router.get("/categories")
async def list_categories(request: Request):
    """Get all service categories."""
    services_mgr = request.app.state.services
    categories = services_mgr.get_categories()
    return {"categories": categories}


@router.get("/search")
async def search_services(request: Request, q: str):
    """Search services by name or description."""
    if len(q) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")

    services_mgr = request.app.state.services
    results = services_mgr.search(q)
    return {"services": results, "count": len(results), "query": q}


@router.get("/{name}")
async def get_service(request: Request, name: str):
    """Get details for a specific service."""
    services_mgr = request.app.state.services
    docker = request.app.state.docker

    info = services_mgr.get_service_info(name)
    if not info:
        raise HTTPException(status_code=404, detail=f"Service '{name}' not found")

    # Add container status if enabled
    if info.get("enabled"):
        container = docker.get_container(name)
        if container:
            info["container"] = container

    return info


@router.get("/{name}/status")
async def get_service_status(request: Request, name: str):
    """Get container status for a service (HTMX partial)."""
    docker = request.app.state.docker
    container = docker.get_container(name)

    if container:
        return {
            "name": name,
            "status": container["status"],
            "health": container["health"],
        }
    else:
        return {
            "name": name,
            "status": "not_found",
            "health": "none",
        }
