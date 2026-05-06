***REMOVED***!/usr/bin/env python3
"""
H-045 verification: agent OS, NL control plane, federated retrieval, selective context runtime foundations.
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND = REPO_ROOT / "backend"

REQUIRED_FILES = [
    REPO_ROOT / "docs" / "H-045_AGENT_OS_FEDERATED_RETRIEVAL_SELECTIVE_CONTEXT.md",
    REPO_ROOT / "docs" / "H-045_IMPLEMENTATION_PROOF.md",
    BACKEND / "src" / "agent_operating_system" / "__init__.py",
    BACKEND / "src" / "agent_operating_system" / "agent_registry_service.py",
    BACKEND / "src" / "agent_operating_system" / "agent_role_service.py",
    BACKEND / "src" / "agent_operating_system" / "agent_fleet_service.py",
    BACKEND / "src" / "agent_operating_system" / "agent_permission_governance.py",
    BACKEND / "src" / "natural_language_control_plane" / "__init__.py",
    BACKEND / "src" / "natural_language_control_plane" / "nl_command_parser.py",
    BACKEND / "src" / "natural_language_control_plane" / "human_approval_service.py",
    BACKEND / "src" / "natural_language_control_plane" / "command_audit_service.py",
    BACKEND / "src" / "federated_retrieval" / "__init__.py",
    BACKEND / "src" / "federated_retrieval" / "connector_registry_service.py",
    BACKEND / "src" / "federated_retrieval" / "incremental_sync_service.py",
    BACKEND / "src" / "federated_retrieval" / "federated_search_service.py",
    BACKEND / "src" / "federated_retrieval" / "source_lineage_service.py",
    BACKEND / "src" / "selective_context_runtime" / "__init__.py",
    BACKEND / "src" / "selective_context_runtime" / "selective_expansion_service.py",
    BACKEND / "src" / "selective_context_runtime" / "retrieval_budget_service.py",
    BACKEND / "src" / "http" / "v1" / "agent_operating_system_router.py",
    BACKEND / "src" / "http" / "v1" / "natural_language_control_plane_router.py",
    BACKEND / "src" / "http" / "v1" / "federated_retrieval_router.py",
    BACKEND / "src" / "http" / "v1" / "selective_context_runtime_router.py",
    BACKEND / "tests" / "test_h045_agent_os_federated_retrieval.py",
]

SECRET_RX = [
    (re.compile(r"(?i)sk_live_[0-9a-zA-Z]{16,}"), "Stripe-like"),
    (re.compile(r"(?i)postgresql://[^\s\"']+"), "DB URL-like"),
]


def ok(msg: str) -> None:
    print(f"PASS: {msg}", flush=True)


def fail(msg: str) -> int:
    print(f"FAIL: {msg}", flush=True)
    return 1


def has_bom(p: Path) -> bool:
    try:
        return p.read_bytes().startswith(b"\xef\xbb\xbf")
    except OSError:
        return False


def router_thin(p: Path) -> bool:
    t = p.read_text(encoding="utf-8")
    forbidden = ("_STORE", "class ", "validate_", "compute_", "append(")
    return "APIRouter(" in t and not any(x in t for x in forbidden)


def check_files() -> int:
    rc = 0
    for p in REQUIRED_FILES:
        if not p.exists():
            rc |= fail(f"missing file: {p.relative_to(REPO_ROOT)}")
        else:
            ok(f"exists: {p.relative_to(REPO_ROOT)}")
        if p.exists() and p.is_file() and has_bom(p):
            rc |= fail(f"BOM detected: {p.relative_to(REPO_ROOT)}")
    return rc


def check_router_thinness() -> int:
    rc = 0
    routers = [
        BACKEND / "src" / "http" / "v1" / "agent_operating_system_router.py",
        BACKEND / "src" / "http" / "v1" / "natural_language_control_plane_router.py",
        BACKEND / "src" / "http" / "v1" / "federated_retrieval_router.py",
        BACKEND / "src" / "http" / "v1" / "selective_context_runtime_router.py",
    ]
    for r in routers:
        if not router_thin(r):
            rc |= fail(f"router not thin: {r.relative_to(REPO_ROOT)}")
        else:
            ok(f"router thin: {r.relative_to(REPO_ROOT)}")
    return rc


def check_app_registration() -> int:
    rc = 0
    app_py = BACKEND / "src" / "app.py"
    txt = app_py.read_text(encoding="utf-8")
    for needle in (
        "agent_operating_system_router",
        "natural_language_control_plane_router",
        "federated_retrieval_router",
        "selective_context_runtime_router",
    ):
        if needle not in txt:
            rc |= fail(f"app wiring missing: {needle}")
        else:
            ok(f"app wiring includes: {needle}")
    return rc


def check_books_backlog() -> int:
    rc = 0
    main_book = REPO_ROOT / "backend/docs/main_book/FinderOS_MainBook_v0.1.html"
    live_book = REPO_ROOT / "backend/docs/live_book/FinderOS_LiveBook_2025-12-13.html"
    backlog = REPO_ROOT / "docs/SOARB2B_MASTER_BACKLOG.md"
    for p, needle in (
        (main_book, "H-045 Unified Agent Operating System"),
        (live_book, "H-045 Verification"),
        (backlog, "***REMOVED******REMOVED*** H-045 — Unified Agent Operating System"),
    ):
        if needle not in p.read_text(encoding="utf-8"):
            rc |= fail(f"missing content: {p.relative_to(REPO_ROOT)} => {needle}")
        else:
            ok(f"contains: {p.relative_to(REPO_ROOT)} => {needle}")
    return rc


def check_no_secrets_scan() -> int:
    rc = 0
    scan = [
        BACKEND / "src" / "federated_retrieval" / "connector_registry_service.py",
        BACKEND / "src" / "natural_language_control_plane" / "command_audit_service.py",
        BACKEND / "src" / "agent_operating_system" / "agent_registry_service.py",
    ]
    for p in scan:
        blob = p.read_text(encoding="utf-8")
        for rx, label in SECRET_RX:
            if rx.search(blob):
                rc |= fail(f"secret-like material in {p.relative_to(REPO_ROOT)} ({label})")
    if rc == 0:
        ok("no secret-like material detected in sampled files")
    return rc


def optional_http_checks() -> int:
    base = os.environ.get("VERIFY_BASE_URL", "").strip()
    if not base:
        ok("VERIFY_BASE_URL not set; skipping live HTTP checks")
        return 0
    endpoints = [
        "/api/v1/system/agents",
        "/api/v1/system/agents/fleet",
        "/api/v1/system/retrieval/connectors",
        "/api/v1/system/retrieval/lineage",
        "/api/v1/system/selective-context/expansion",
        "/api/v1/system/selective-context/budgets",
    ]
    rc = 0
    for ep in endpoints:
        url = base.rstrip("/") + ep
        try:
            req = Request(url, headers={"User-Agent": "FinderOS-Verify-H045"})
            with urlopen(req, timeout=6) as resp:  ***REMOVED*** noqa: S310 internal verification
                if resp.status != 200:
                    rc |= fail(f"GET {ep} status {resp.status}")
                else:
                    ok(f"GET {ep} 200")
        except (HTTPError, URLError) as exc:
            rc |= fail(f"GET {ep} failed: {exc}")
    return rc


def smoke_import_routes() -> int:
    rc = 0
    sys.path.insert(0, str(BACKEND))
    from src.app import create_app  ***REMOVED*** type: ignore

    app = create_app()
    routes = [r.path for r in app.router.routes]
    required = [
        "/api/v1/system/agents",
        "/api/v1/system/nl-control/intents",
        "/api/v1/system/retrieval/connectors",
        "/api/v1/system/selective-context/expansion",
    ]
    for r in required:
        if r not in routes:
            rc |= fail(f"missing route: {r}")
        else:
            ok(f"route registered: {r}")
    return rc


def main() -> int:
    rc = 0
    rc |= check_files()
    rc |= check_router_thinness()
    rc |= check_app_registration()
    rc |= check_books_backlog()
    rc |= check_no_secrets_scan()
    rc |= smoke_import_routes()
    rc |= optional_http_checks()
    if rc == 0:
        ok("H-045 verification PASS")
    else:
        fail("H-045 verification FAIL")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

