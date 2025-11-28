"""Server-Sent Events for real-time updates."""

import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

router = APIRouter()


async def docker_event_generator(request: Request) -> AsyncGenerator[dict, None]:
    """Generate Docker events as SSE messages."""
    docker = request.app.state.docker

    try:
        # Use docker-py events API
        for event in docker.client.events(decode=True):
            if await request.is_disconnected():
                break

            # Filter to container events
            if event.get("Type") == "container":
                action = event.get("Action", "")
                actor = event.get("Actor", {})
                attributes = actor.get("Attributes", {})
                container_name = attributes.get("name", "unknown")

                yield {
                    "event": "container",
                    "data": json.dumps({
                        "action": action,
                        "container": container_name,
                        "image": attributes.get("image", ""),
                        "time": event.get("time", 0),
                    }),
                }
    except Exception as e:
        yield {
            "event": "error",
            "data": json.dumps({"error": str(e)}),
        }


async def status_generator(request: Request) -> AsyncGenerator[dict, None]:
    """Generate periodic status updates."""
    docker = request.app.state.docker
    services_mgr = request.app.state.services

    while True:
        if await request.is_disconnected():
            break

        try:
            # Get current status
            containers = docker.list_containers(all=True)
            running = sum(1 for c in containers if c["status"] == "running")

            enabled_count = len(services_mgr.get_enabled_names())

            yield {
                "event": "status",
                "data": json.dumps({
                    "containers_total": len(containers),
                    "containers_running": running,
                    "services_enabled": enabled_count,
                }),
            }
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)}),
            }

        # Wait before next update
        await asyncio.sleep(5)


@router.get("/docker")
async def docker_events(request: Request):
    """Stream Docker events via SSE."""
    return EventSourceResponse(docker_event_generator(request))


@router.get("/status")
async def status_updates(request: Request):
    """Stream periodic status updates via SSE."""
    return EventSourceResponse(status_generator(request))
