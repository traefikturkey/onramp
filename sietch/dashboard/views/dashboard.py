"""Dashboard home page views."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Dashboard home page."""
    templates = request.app.state.templates
    docker = request.app.state.docker
    services_mgr = request.app.state.services

    # Get container stats
    containers = docker.list_containers(all=True)
    running = sum(1 for c in containers if c["status"] == "running")
    stopped = len(containers) - running

    # Get service counts
    available_count = len(services_mgr.get_available_names())
    enabled_count = len(services_mgr.get_enabled_names())

    # Get enabled services with container status
    enabled_services = []
    for service in services_mgr.list_enabled():
        container = docker.get_container(service["name"])
        enabled_services.append({
            **service,
            "container": container,
        })

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "stats": {
                "containers_total": len(containers),
                "containers_running": running,
                "containers_stopped": stopped,
                "services_available": available_count,
                "services_enabled": enabled_count,
            },
            "enabled_services": enabled_services[:12],  # Show first 12
            "more_services": max(0, len(enabled_services) - 12),
        },
    )
