#!/usr/bin/env python3
from pathlib import Path
import re

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
ROBOTS_HEADER = "none,noarchive,nosnippet,notranslate,noimageindex,"
WEBSecure_ENTRYPOINT = re.compile(
    r"^\s*- traefik\.http\.routers\.([^.]+)\.entrypoints=websecure\s*$"
)
ROUTER_MIDDLEWARE = re.compile(
    r"^\s*- traefik\.http\.routers\.([^.]+)\.middlewares=(.+?)\s*$"
)


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def main() -> None:
    middleware_path = REPO_ROOT / "external-available" / "middleware.yml"
    template_path = REPO_ROOT / "services-scaffold" / "_templates" / "service.template"

    with middleware_path.open() as f:
        config = yaml.safe_load(f)

    middlewares = config["http"]["middlewares"]
    default_response_headers = middlewares["default-headers"]["headers"][
        "customResponseHeaders"
    ]
    allow_indexing_response_headers = middlewares["allow-indexing-headers"]["headers"][
        "customResponseHeaders"
    ]

    if default_response_headers.get("X-Robots-Tag") != ROBOTS_HEADER:
        fail("default-headers must keep the default X-Robots-Tag noindex policy")

    if allow_indexing_response_headers.get("X-Robots-Tag") != "":
        fail("allow-indexing-headers must remove X-Robots-Tag with an empty value")

    template = template_path.read_text()
    expected_label = (
        "traefik.http.routers.${SERVICE_PASSED_DNCASED}.middlewares="
        "${${SERVICE_PASSED_UPCASED}_MIDDLEWARES:-default-headers@file}"
    )

    if "allow-indexing-headers@file" in template:
        fail("new service template must not allow indexing by default")

    if expected_label not in template:
        fail("new service template must expose a default-headers middleware override")

    for service_file in sorted((REPO_ROOT / "services-available").rglob("*.yml")):
        lines = service_file.read_text().splitlines()
        websecure_routers = {
            match.group(1)
            for line in lines
            if (match := WEBSecure_ENTRYPOINT.match(line))
        }
        middleware_defaults = {
            match.group(1): match.group(2)
            for line in lines
            if (match := ROUTER_MIDDLEWARE.match(line))
        }

        missing = sorted(websecure_routers - middleware_defaults.keys())
        if missing:
            fail(f"{service_file.relative_to(REPO_ROOT)} missing middleware labels: {missing}")

        for router in websecure_routers:
            middleware = middleware_defaults[router]
            if "allow-indexing-headers@file" in middleware:
                fail(
                    f"{service_file.relative_to(REPO_ROOT)} router {router} "
                    "allows indexing by default"
                )
            if not middleware.startswith("${") or ":-" not in middleware:
                fail(
                    f"{service_file.relative_to(REPO_ROOT)} router {router} "
                    "middleware must use an env-var default"
                )

    print("Search indexing configuration is valid")


if __name__ == "__main__":
    main()
