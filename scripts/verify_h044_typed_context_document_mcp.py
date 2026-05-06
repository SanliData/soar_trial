"""
H-044 verification: typed context orchestration, document intelligence abstraction, MCP runtime compatibility.
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND = REPO_ROOT / "backend"


def ok(msg: str) -> None:
    print(f"PASS: {msg}", flush=True)


def fail(msg: str) -> int:
    print(f"FAIL: {msg}", flush=True)
    return 1


def has_bom(path: Path) -> bool:
    data = path.read_bytes()
    return data.startswith(b"\xef\xbb\xbf")


def assert_exists(rel: str) -> int:
    p = (REPO_ROOT / rel).resolve()
    if not p.exists():
        return fail(f"missing: {rel}")
    ok(f"exists: {rel}")
    return 0


def assert_contains(path: Path, needle: str) -> int:
    text = path.read_text(encoding="utf-8")
    if needle not in text:
        return fail(f"missing content: {path.relative_to(REPO_ROOT)} => {needle}")
    ok(f"contains: {path.relative_to(REPO_ROOT)} => {needle}")
    return 0


def router_thin(p: Path) -> bool:
    t = p.read_text(encoding="utf-8")
    ***REMOVED*** "thin router" heuristic: APIRouter present, no business logic / no registries
    forbidden = ("_STORE", "def build_", "class ", "validate_context_item(", "compute_")
    return "APIRouter(" in t and not any(x in t for x in forbidden)


def smoke_imports() -> int:
    rc = 0
    ***REMOVED*** In this repo, `backend/` is the sys.path root for the `src` package.
    sys.path.insert(0, str(BACKEND))
    from src.app import create_app  ***REMOVED*** type: ignore

    app = create_app()
    routes = [r.path for r in app.router.routes]
    required = [
        "/api/v1/system/context/types",
        "/api/v1/system/context/compression",
        "/api/v1/system/context/isolation",
        "/api/v1/system/documents/ocr-pipeline",
        "/api/v1/system/mcp/capabilities",
    ]
    for r in required:
        if r not in routes:
            rc |= fail(f"missing route registration: {r}")
        else:
            ok(f"route registered: {r}")
    return rc


def optional_http_checks() -> int:
    base = os.environ.get("VERIFY_BASE_URL", "").strip()
    if not base:
        ok("VERIFY_BASE_URL not set; skipping live HTTP checks")
        return 0
    try:
        import urllib.request
    except Exception as exc:
        return fail(f"urllib unavailable: {exc}")

    endpoints = [
        "/api/v1/system/context/types",
        "/api/v1/system/context/compression",
        "/api/v1/system/context/isolation",
        "/api/v1/system/documents/ocr-pipeline",
        "/api/v1/system/mcp/capabilities",
    ]
    rc = 0
    for ep in endpoints:
        url = base.rstrip("/") + ep
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:  ***REMOVED*** noqa: S310 (internal verification)
                if resp.status != 200:
                    rc |= fail(f"GET {ep} status {resp.status}")
                else:
                    rc |= ok(f"GET {ep} 200")
        except Exception as exc:
            rc |= fail(f"GET {ep} failed: {exc}")
    return rc


def main() -> int:
    rc = 0

    required_files = [
        "backend/src/context_orchestration/context_lifecycle_service.py",
        "backend/src/context_orchestration/context_validation_service.py",
        "backend/src/context_compression/semantic_context_summarizer.py",
        "backend/src/context_compression/duplicate_context_detector.py",
        "backend/src/context_isolation/context_boundary_service.py",
        "backend/src/document_intelligence/ocr_pipeline_service.py",
        "backend/src/mcp_runtime/mcp_tool_projection_service.py",
        "backend/src/http/v1/context_orchestration_router.py",
        "backend/src/http/v1/context_compression_router.py",
        "backend/src/http/v1/context_isolation_router.py",
        "backend/src/http/v1/document_intelligence_router.py",
        "backend/src/http/v1/mcp_runtime_router.py",
        "docs/H-044_TYPED_CONTEXT_DOCUMENT_MCP_LAYER.md",
        "docs/H-044_IMPLEMENTATION_PROOF.md",
        "backend/tests/test_h044_typed_context_document_mcp.py",
    ]
    for f in required_files:
        rc |= assert_exists(f)

    ***REMOVED*** app wiring
    app_py = REPO_ROOT / "backend/src/app.py"
    rc |= assert_contains(app_py, "context_orchestration_router")
    rc |= assert_contains(app_py, "document_intelligence_router")
    rc |= assert_contains(app_py, "mcp_runtime_router")

    ***REMOVED*** books/backlog
    main_book = REPO_ROOT / "backend/docs/main_book/FinderOS_MainBook_v0.1.html"
    live_book = REPO_ROOT / "backend/docs/live_book/FinderOS_LiveBook_2025-12-13.html"
    backlog = REPO_ROOT / "docs/SOARB2B_MASTER_BACKLOG.md"
    rc |= assert_contains(main_book, "H-044 Typed Context Orchestration")
    rc |= assert_contains(live_book, "H-044 Verification")
    rc |= assert_contains(backlog, "***REMOVED******REMOVED*** H-044 — Typed Context Orchestration")

    ***REMOVED*** router thinness
    routers = [
        REPO_ROOT / "backend/src/http/v1/context_orchestration_router.py",
        REPO_ROOT / "backend/src/http/v1/context_compression_router.py",
        REPO_ROOT / "backend/src/http/v1/context_isolation_router.py",
        REPO_ROOT / "backend/src/http/v1/document_intelligence_router.py",
        REPO_ROOT / "backend/src/http/v1/mcp_runtime_router.py",
    ]
    for r in routers:
        if not router_thin(r):
            rc |= fail(f"router not thin: {r.relative_to(REPO_ROOT)}")
        else:
            ok(f"router thin: {r.relative_to(REPO_ROOT)}")

    ***REMOVED*** hygiene: BOM + secrets scan (lightweight)
    scan = [
        REPO_ROOT / "backend/src/http/v1/context_orchestration_router.py",
        REPO_ROOT / "backend/src/context_compression/semantic_context_summarizer.py",
        REPO_ROOT / "backend/src/mcp_runtime/mcp_tool_projection_service.py",
    ]
    for p in scan:
        if has_bom(p):
            rc |= fail(f"BOM detected: {p.relative_to(REPO_ROOT)}")
        else:
            ok(f"No BOM: {p.relative_to(REPO_ROOT)}")
        blob = p.read_text(encoding="utf-8").lower()
        for needle in ("openai_api_key", "stripe_secret", "postgresql://", "BEGIN RSA PRIVATE KEY".lower()):
            if needle.lower() in blob:
                rc |= fail(f"secret-like substring detected: {p.relative_to(REPO_ROOT)} => {needle}")

    rc |= smoke_imports()
    rc |= optional_http_checks()

    if rc == 0:
        ok("H-044 verification PASS")
    else:
        fail("H-044 verification FAIL")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

