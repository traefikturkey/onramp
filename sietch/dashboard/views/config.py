"""Configuration management views."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def config_home(request: Request):
    """Configuration management home page."""
    templates = request.app.state.templates
    services_mgr = request.app.state.services

    enabled = services_mgr.get_enabled_names()

    return templates.TemplateResponse(
        "config/index.html",
        {
            "request": request,
            "enabled_services": enabled,
        },
    )


@router.get("/global", response_class=HTMLResponse)
async def global_env_editor(request: Request):
    """Global .env editor page."""
    templates = request.app.state.templates
    services_enabled = request.app.state.services._manager.services_enabled
    env_path = services_enabled / ".env"

    content = ""
    if env_path.exists():
        content = env_path.read_text(encoding="utf-8")

    return templates.TemplateResponse(
        "config/editor.html",
        {
            "request": request,
            "title": "Global Environment",
            "file_path": str(env_path),
            "content": content,
            "save_url": "/api/config/global",
            "service": None,
        },
    )


@router.get("/service/{name}", response_class=HTMLResponse)
async def service_env_editor(request: Request, name: str):
    """Service-specific .env editor page."""
    templates = request.app.state.templates
    services_mgr = request.app.state.services

    service = services_mgr.get_service_info(name)
    if not service:
        return templates.TemplateResponse(
            "services/not_found.html",
            {"request": request, "name": name},
            status_code=404,
        )

    services_enabled = services_mgr._manager.services_enabled
    env_path = services_enabled / f"{name}.env"

    content = ""
    if env_path.exists():
        content = env_path.read_text(encoding="utf-8")

    # Get template for reference
    scaffold_dir = services_mgr._manager.base_dir / "services-scaffold" / name
    template_path = scaffold_dir / "env.template"
    template_content = ""
    if template_path.exists():
        template_content = template_path.read_text(encoding="utf-8")

    return templates.TemplateResponse(
        "config/editor.html",
        {
            "request": request,
            "title": f"{name} Environment",
            "file_path": str(env_path),
            "content": content,
            "template_content": template_content,
            "save_url": f"/api/config/service/{name}",
            "service": service,
        },
    )
