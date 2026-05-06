#!/usr/bin/env python3
"""
SCRIPT: smoke_local_ui_and_api
PURPOSE: Basic local smoke check for UI pages + key APIs (Phase 1-3)
ENCODING: UTF-8 WITHOUT BOM

Usage:
  cd backend
  BASE_URL=http://127.0.0.1:8000 python scripts/smoke_local_ui_and_api.py
  python scripts/smoke_local_ui_and_api.py --base-url http://127.0.0.1:8082
"""

from __future__ import annotations

import argparse
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def _get(base_url: str, path: str) -> tuple[int, str]:
    url = f"{base_url}{path}"
    req = Request(url, headers={"Accept": "*/*"})
    try:
        with urlopen(req, timeout=8) as r:
            return int(r.status), url
    except HTTPError as e:
        return int(e.code), url
    except URLError:
        return 0, url


def main() -> int:
    parser = argparse.ArgumentParser(description="Local smoke check for FinderOS UI + key APIs.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL, e.g. http://127.0.0.1:8082")
    args = parser.parse_args()
    base_url = str(args.base_url).rstrip("/")

    checks = [
        # Core
        "/healthz",
        "/readyz",
        "/docs",
        "/openapi.json",
        # Phase 1
        "/ui/en/app_shell.html",
        "/ui/en/operational_cockpit.html",
        # Phase 2
        "/ui/en/results_hub_v2.html",
        "/ui/en/retrieval_intelligence.html",
        "/ui/en/procurement_workflow.html",
        "/ui/en/intelligence_search.html",
        "/ui/en/relationship_graphs.html",
        # Phase 3
        "/ui/en/event_stream_center.html",
        "/ui/en/agent_operations_center.html",
        "/ui/en/approval_center.html",
        # Key APIs (GET only)
        "/api/v1/results/opportunities",
        "/api/v1/results/evidence",
        "/api/v1/results/explainability",
        "/api/v1/system/retrieval/connectors",
        "/api/v1/system/visibility/health",
        "/api/v1/system/hitl/review-queue",
        "/api/v1/system/agui/events",
        "/api/v1/system/cache/efficiency",
        "/api/v1/system/identity/registry",
        "/api/v1/system/inference/telemetry",
    ]

    failures: list[tuple[int, str]] = []
    for p in checks:
        status, url = _get(base_url, p)
        ok = status in (200, 301, 302)
        line = f"{'OK ' if ok else 'BAD'} {status:>3} {p}"
        print(line)
        if not ok:
            failures.append((status, url))

    if failures:
        print("\nFAILURES:")
        for status, url in failures:
            print(f"  - {status} {url}")
        return 1

    print("\nLocal smoke check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

