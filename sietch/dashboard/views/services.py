"""Service management views."""

from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def service_catalog(request: Request, category: str = None, q: str = None):
    """Service catalog page - list available services."""
    templates = request.app.state.templates
    services_mgr = request.app.state.services

    # Get services based on filters
    if q:
        services = services_mgr.search(q)
    elif category:
        services = services_mgr.filter_by_category(category)
    else:
        services = services_mgr.list_available()

    categories = services_mgr.get_categories()

    return templates.TemplateResponse(
        "services/catalog.html",
        {
            "request": request,
            "services": services,
            "categories": categories,
            "current_category": category,
            "search_query": q,
        },
    )


# Core services that are always shown but can't be stopped/restarted
CORE_SERVICES = {
    "traefik": {
        "description": "Cloud native application proxy and load balancer",
        "url": "https://doc.traefik.io/traefik/",
    },
}


@router.get("/enabled", response_class=HTMLResponse)
async def enabled_services(request: Request):
    """Enabled services page."""
    templates = request.app.state.templates
    services_mgr = request.app.state.services
    docker = request.app.state.docker

    # Start with core services
    enabled = []
    for name, info in CORE_SERVICES.items():
        container = docker.get_container(name)
        if container:
            enabled.append(
                {
                    "name": name,
                    "description": info.get("description", f"Core service - {name}"),
                    "container": container,
                    "core": True,
                    "url": info.get("url"),
                }
            )

    # Add enabled services
    for service in services_mgr.list_enabled():
        container = docker.get_container(service["name"])
        enabled.append(
            {
                **service,
                "container": container,
                "core": False,
            }
        )

    return templates.TemplateResponse(
        "services/enabled.html",
        {
            "request": request,
            "services": enabled,
        },
    )


@router.get("/{name}", response_class=HTMLResponse)
async def service_detail(request: Request, name: str):
    """Service detail page."""
    templates = request.app.state.templates
    services_mgr = request.app.state.services
    docker = request.app.state.docker

    service = services_mgr.get_service_info(name)

    # Handle core services (like traefik) that aren't in services-available
    if not service and name in CORE_SERVICES:
        container = docker.get_container(name)
        if container:
            # Check for etc/ directory
            from pathlib import Path

            base_dir = Path("/app")
            has_etc = (base_dir / "etc" / name).exists()

            service = {
                "name": name,
                "description": f"Core service - {name}",
                "enabled": True,
                "core": True,
                "url": None,
                "has_env": True,  # Core services use the main .env file
                "has_etc": has_etc,
                "category": "core",
            }
        else:
            return templates.TemplateResponse(
                "services/not_found.html",
                {"request": request, "name": name},
                status_code=404,
            )
    elif not service:
        return templates.TemplateResponse(
            "services/not_found.html",
            {"request": request, "name": name},
            status_code=404,
        )
    else:
        service["core"] = False

    container = docker.get_container(name)

    return templates.TemplateResponse(
        "services/detail.html",
        {
            "request": request,
            "service": service,
            "container": container,
        },
    )
