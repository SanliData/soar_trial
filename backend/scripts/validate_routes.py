***REMOVED***!/usr/bin/env python3
"""
Validate FastAPI routes: fetch OpenAPI schema and check for duplicate paths,
double-prefix (e.g. /v1/v1/...), and list all paths for audit.
Usage:
  From backend/: python scripts/validate_routes.py
  Or against running app: BASE_URL=http://localhost:8000 python scripts/validate_routes.py
"""

import json
import os
import sys
from collections import defaultdict
from urllib.request import urlopen, Request

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
OPENAPI_URL = f"{BASE_URL.rstrip('/')}/openapi.json"


def fetch_openapi() -> dict:
    req = Request(OPENAPI_URL, headers={"Accept": "application/json"})
    with urlopen(req, timeout=10) as r:
        return json.load(r)


def main() -> int:
    print(f"Fetching OpenAPI from {OPENAPI_URL} ...")
    try:
        spec = fetch_openapi()
    except Exception as e:
        print(f"ERROR: Could not fetch OpenAPI: {e}", file=sys.stderr)
        return 1

    paths = spec.get("paths", {})
    path_list = sorted(paths.keys())

    ***REMOVED*** Double-prefix check
    double_prefix = [p for p in path_list if "/v1/v1/" in p or "/api/v1/v1/" in p]
    if double_prefix:
        print("FAIL: Paths with double prefix (/v1/v1/ or /api/v1/v1/):")
        for p in double_prefix:
            print(f"  - {p}")
    else:
        print("OK: No double-prefix paths found.")

    ***REMOVED*** Duplicate path + method
    by_path_method: dict[tuple[str, str], list[str]] = defaultdict(list)
    for path, methods in paths.items():
        for method in methods:
            if method.lower() in ("get", "post", "put", "delete", "patch", "head", "options"):
                by_path_method[(path, method.upper())].append(path)
    duplicates = [(k, v) for k, v in by_path_method.items() if len(v) > 1]
    if duplicates:
        print("FAIL: Duplicate path+method (multiple handlers):")
        for (path, method), _ in duplicates:
            print(f"  - {method} {path}")
    else:
        print("OK: No duplicate path+method.")

    ***REMOVED*** List all paths (summary)
    print("\nAll paths (first 80):")
    for p in path_list[:80]:
        methods = list(paths[p].keys())
        methods = [m.upper() for m in methods if m.lower() in ("get", "post", "put", "delete", "patch")]
        print(f"  {','.join(methods):20} {p}")
    if len(path_list) > 80:
        print(f"  ... and {len(path_list) - 80} more")

    failed = bool(double_prefix or duplicates)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
