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


@router.get("/enabled", response_class=HTMLResponse)
async def enabled_services(request: Request):
    """Enabled services page."""
    templates = request.app.state.templates
    services_mgr = request.app.state.services
    docker = request.app.state.docker

    # Get enabled services with container status
    enabled = []
    for service in services_mgr.list_enabled():
        container = docker.get_container(service["name"])
        enabled.append({
            **service,
            "container": container,
        })

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
    if not service:
        return templates.TemplateResponse(
            "services/not_found.html",
            {"request": request, "name": name},
            status_code=404,
        )

    container = None
    if service.get("enabled"):
        container = docker.get_container(name)

    return templates.TemplateResponse(
        "services/detail.html",
        {
            "request": request,
            "service": service,
            "container": container,
        },
    )
