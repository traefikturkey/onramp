"""Dashboard home page views."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()

PAGE_SIZE = 12

# Core services that are always shown but can't be stopped/restarted
CORE_SERVICES = {
    "traefik": {
        "description": "Cloud native application proxy and load balancer",
        "url": "https://doc.traefik.io/traefik/",
    },
}


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Dashboard home page."""
    templates = request.app.state.templates
    docker = request.app.state.docker
    services_mgr = request.app.state.services

    # Get service counts (include core services in enabled count)
    available_count = len(services_mgr.get_available_names())
    enabled_count = len(services_mgr.get_enabled_names()) + len(CORE_SERVICES)

    # Get enabled services with container status
    enabled_services = _get_enabled_services_with_status(services_mgr, docker)

    # Count running vs stopped enabled services (includes core)
    running_services = sum(
        1
        for s in enabled_services
        if s.get("container") and s["container"].get("status") == "running"
    )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "stats": {
                "services_running": running_services,
                "services_enabled": enabled_count,
                "services_available": available_count,
            },
            "enabled_services": enabled_services[:PAGE_SIZE],
            "has_more": len(enabled_services) > PAGE_SIZE,
            "next_offset": PAGE_SIZE,
        },
    )


def _get_enabled_services_with_status(services_mgr, docker):
    """Get enabled services with their container status."""
    enabled_services = []

    # Add core services first (like traefik)
    for name, info in CORE_SERVICES.items():
        container = docker.get_container(name)
        if container:
            enabled_services.append(
                {
                    "name": name,
                    "description": info.get("description", f"Core service - {name}"),
                    "url": info.get("url"),
                    "container": container,
                    "core": True,  # Mark as core - can't be stopped/restarted
                }
            )

    # Add enabled services
    for service in services_mgr.list_enabled():
        container = docker.get_container(service["name"])
        enabled_services.append(
            {
                **service,
                "container": container,
                "core": False,
            }
        )
    return enabled_services


@router.get("/api/home/services", response_class=HTMLResponse)
async def load_more_services(request: Request, offset: int = 0):
    """Load more services for infinite scroll (returns HTML fragment)."""
    templates = request.app.state.templates
    docker = request.app.state.docker
    services_mgr = request.app.state.services

    enabled_services = _get_enabled_services_with_status(services_mgr, docker)

    # Get the slice for this page
    end = offset + PAGE_SIZE
    page_services = enabled_services[offset:end]
    has_more = end < len(enabled_services)

    return templates.TemplateResponse(
        "partials/service_cards_batch.html",
        {
            "request": request,
            "services": page_services,
            "has_more": has_more,
            "next_offset": end,
        },
    )
