"""FastAPI application factory for OnRamp Dashboard."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup: Initialize clients and state
    from .core.docker_client import DockerClient
    from .core.service_manager import ServiceManager

    app.state.docker = DockerClient(settings.docker_host)
    app.state.services = ServiceManager(str(settings.base_dir))

    yield

    # Shutdown: Cleanup if needed
    pass


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_title,
        lifespan=lifespan,
        docs_url="/api/docs" if settings.debug else None,
        redoc_url="/api/redoc" if settings.debug else None,
    )

    # Static files
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Templates
    templates_dir = Path(__file__).parent / "templates"
    app.state.templates = Jinja2Templates(directory=templates_dir)

    # Include API routers
    from .api import services, docker, system

    app.include_router(services.router, prefix="/api/services", tags=["services"])
    app.include_router(docker.router, prefix="/api/docker", tags=["docker"])
    app.include_router(system.router, prefix="/api/system", tags=["system"])

    # Include view routers
    from .views import dashboard, services as service_views

    app.include_router(dashboard.router, tags=["views"])
    app.include_router(service_views.router, prefix="/services", tags=["views"])

    return app


# For uvicorn: python -m uvicorn dashboard.app:app --factory
app = create_app
