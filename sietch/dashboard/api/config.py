"""Environment variable and configuration management API."""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()


class EnvUpdate(BaseModel):
    """Request body for updating environment variables."""
    content: str


@router.get("/global")
async def get_global_env(request: Request):
    """Get global .env file content."""
    services_enabled = request.app.state.services._manager.services_enabled
    env_path = services_enabled / ".env"

    if not env_path.exists():
        return {"path": str(env_path), "content": "", "exists": False}

    content = env_path.read_text(encoding="utf-8")
    return {"path": str(env_path), "content": content, "exists": True}


@router.put("/global")
async def update_global_env(request: Request, data: EnvUpdate):
    """Update global .env file."""
    services_enabled = request.app.state.services._manager.services_enabled
    env_path = services_enabled / ".env"

    # Backup before writing
    if env_path.exists():
        backup_path = env_path.with_suffix(".env.bak")
        backup_path.write_text(env_path.read_text(encoding="utf-8"), encoding="utf-8")

    env_path.write_text(data.content, encoding="utf-8")
    return {"success": True, "path": str(env_path)}


@router.get("/service/{name}")
async def get_service_env(request: Request, name: str):
    """Get service-specific .env file content."""
    services_enabled = request.app.state.services._manager.services_enabled
    env_path = services_enabled / f"{name}.env"

    if not env_path.exists():
        return {"path": str(env_path), "content": "", "exists": False, "service": name}

    content = env_path.read_text(encoding="utf-8")
    return {"path": str(env_path), "content": content, "exists": True, "service": name}


@router.put("/service/{name}")
async def update_service_env(request: Request, name: str, data: EnvUpdate):
    """Update service-specific .env file."""
    services_enabled = request.app.state.services._manager.services_enabled
    env_path = services_enabled / f"{name}.env"

    # Backup before writing
    if env_path.exists():
        backup_path = env_path.with_suffix(".env.bak")
        backup_path.write_text(env_path.read_text(encoding="utf-8"), encoding="utf-8")

    env_path.write_text(data.content, encoding="utf-8")
    return {"success": True, "path": str(env_path), "service": name}


@router.get("/service/{name}/template")
async def get_service_env_template(request: Request, name: str):
    """Get env.template for a service scaffold."""
    services_scaffold = request.app.state.services._manager.base_dir / "services-scaffold" / name
    template_path = services_scaffold / "env.template"

    if not template_path.exists():
        return {"path": str(template_path), "content": None, "exists": False, "service": name}

    content = template_path.read_text(encoding="utf-8")
    return {"path": str(template_path), "content": content, "exists": True, "service": name}


@router.get("/service/{name}/variables")
async def get_service_variables(request: Request, name: str):
    """Parse and return variables from service env template."""
    import re

    services_scaffold = request.app.state.services._manager.base_dir / "services-scaffold" / name
    template_path = services_scaffold / "env.template"

    variables = []

    if template_path.exists():
        content = template_path.read_text(encoding="utf-8")
        # Parse VAR=value or VAR=${DEFAULT:-value} patterns
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                var_name = line.split("=", 1)[0]
                var_value = line.split("=", 1)[1] if "=" in line else ""
                variables.append({
                    "name": var_name,
                    "default": var_value,
                    "required": "${" not in var_value,  # Has default if uses ${VAR:-default}
                })

    return {"service": name, "variables": variables}
