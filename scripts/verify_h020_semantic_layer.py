***REMOVED***!/usr/bin/env python3
"""
H-020 verification: semantic capability manifest foundation.
Exit code 0 only if deterministic checks succeed.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND = REPO_ROOT / "backend"

RISK_ALLOWED = frozenset({"low", "medium", "high", "critical"})
ORCHESTRATION_KEYS = frozenset(
    {
        "orchestration_safe",
        "destructive_action",
        "human_approval_required",
    },
)
REQUIRED_CAPABILITY_KEYS = frozenset(
    {
        "capability_id",
        "name",
        "domain",
        "description",
        "endpoint",
        "http_method",
        "auth_required",
        "idempotent",
        "rate_limit",
        "risk_level",
        "sensitive_fields",
        "destructive_action",
        "orchestration_safe",
        "human_approval_required",
        "allowed_roles",
        "input_schema_summary",
        "output_schema_summary",
        "tags",
    },
)

FILES_CHECK = [
    REPO_ROOT / "docs" / "H-020_SEMANTIC_CAPABILITY_LAYER.md",
    REPO_ROOT / "docs" / "H-020_IMPLEMENTATION_PROOF.md",
    BACKEND / "src" / "semantic_capabilities" / "__init__.py",
    BACKEND / "src" / "semantic_capabilities" / "capability_types.py",
    BACKEND / "src" / "semantic_capabilities" / "capability_schema.py",
    BACKEND / "src" / "semantic_capabilities" / "capability_registry.py",
    BACKEND / "src" / "semantic_capabilities" / "capability_loader.py",
    BACKEND / "src" / "semantic_capabilities" / "capability_validation.py",
    BACKEND / "src" / "semantic_capabilities" / "capability_export_service.py",
    BACKEND / "src" / "http" / "v1" / "semantic_capability_router.py",
    BACKEND / "tests" / "test_semantic_capabilities.py",
]


def ok(msg: str) -> None:
    print(f"PASS: {msg}", flush=True)


def fail(msg: str) -> int:
    print(f"FAIL: {msg}", flush=True)
    return 1


def has_bom(path: Path) -> bool:
    try:
        return path.read_bytes().startswith(b"\xef\xbb\xbf")
    except OSError:
        return False


SECRET_PATTERNS = [
    (re.compile(r"(?i)sk_live_[0-9a-zA-Z]{16,}"), "Stripe-like"),
]


def scan_secrets(paths: list[Path]) -> list[str]:
    hits: list[str] = []
    for p in paths:
        if not p.exists() or p.suffix not in {".py", ".md"}:
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        for rx, label in SECRET_PATTERNS:
            if rx.search(txt):
                hits.append(f"{p.relative_to(REPO_ROOT)} ({label})")
    return hits


def inspect_registry() -> dict:
    old_path = sys.path[:]
    try:
        sys.path.insert(0, str(BACKEND))
        from src.semantic_capabilities.capability_export_service import (  ***REMOVED*** type: ignore
            build_capabilities_catalog,
        )

        blob = build_capabilities_catalog()
    finally:
        sys.path[:] = old_path
    return blob


def main() -> int:
    rc = 0
    print("H-020 verification...", flush=True)

    for p in FILES_CHECK:
        if p.exists():
            ok(f"exists: {p.relative_to(REPO_ROOT)}")
        else:
            rc |= fail(f"missing file {p.relative_to(REPO_ROOT)}")

    scanned = FILES_CHECK + [
        BACKEND / "src" / "app.py",
        BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html",
        BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html",
        REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md",
        REPO_ROOT / "scripts" / "verify_h020_semantic_layer.py",
    ]

    for p in scanned:
        if p.exists() and p.is_file():
            if has_bom(p):
                rc |= fail(f"BOM detected: {p.relative_to(REPO_ROOT)}")
            else:
                ok(f"No BOM: {p.relative_to(REPO_ROOT)}")

    app_txt = (BACKEND / "src" / "app.py").read_text(encoding="utf-8")
    if "semantic_capability_router" in app_txt and "include_router(semantic_capability_router" in app_txt:
        ok("semantic_capability_router registered in app.py")
    else:
        rc |= fail("app.py missing semantic_capability_router registration")

    rtxt = (BACKEND / "src" / "http" / "v1" / "semantic_capability_router.py").read_text(encoding="utf-8")
    if '"/capabilities"' in rtxt or "'/capabilities'" in rtxt:
        ok("semantic router exposes /capabilities")
    else:
        rc |= fail("semantic_capability_router.py missing GET /capabilities path")

    mb = BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html"
    if mb.exists() and "18. H-020 Semantic Capability Layer" in mb.read_text(encoding="utf-8"):
        ok("MainBook contains Section 18 H-020 heading")
    else:
        rc |= fail("MainBook §18 heading missing")

    lb = BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html"
    if lb.exists() and "18. H-020 Verification" in lb.read_text(encoding="utf-8"):
        ok("LiveBook Section 18 H-020 verification heading present")
    else:
        rc |= fail("LiveBook §18 heading missing")

    doc = REPO_ROOT / "docs" / "H-020_SEMANTIC_CAPABILITY_LAYER.md"
    if not doc.exists():
        rc |= fail("foundation doc missing")
    else:
        ok("foundation doc present")

    bl = REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md"
    if bl.exists() and "H-020" in bl.read_text(encoding="utf-8"):
        ok("Master backlog references H-020")
    else:
        rc |= fail("Master backlog missing H-020 entry")

    for h in scan_secrets([p for p in FILES_CHECK + [BACKEND / "tests" / "test_semantic_capabilities.py"] if p.exists()]):
        rc |= fail(f"secret heuristic: {h}")

    try:
        catalog = inspect_registry()
    except Exception as exc:
        rc |= fail(f"registry/export load failed: {exc}")
        catalog = {}

    caps = catalog.get("capabilities") or []
    if not isinstance(caps, list):
        rc |= fail("capabilities export malformed")
        caps = []

    identifiers = []
    if caps:
        ok(f"export returned {len(caps)} capability rows")
        for row in caps:
            if set(row.keys()) != REQUIRED_CAPABILITY_KEYS:
                missing = REQUIRED_CAPABILITY_KEYS - set(row.keys())
                extra = set(row.keys()) - REQUIRED_CAPABILITY_KEYS
                rc |= fail(f"cap row keys mismatch missing={missing} extra={extra}")
                break
            risk = row.get("risk_level")
            if risk not in RISK_ALLOWED:
                rc |= fail(f"invalid risk_level={risk}")
            if ORCHESTRATION_KEYS - row.keys():
                rc |= fail("missing orchestration metadata columns")
            identifiers.append(row["capability_id"])
        if len(identifiers) != len(set(identifiers)):
            rc |= fail("duplicate capability_id in exported JSON")
        approvals = {"exposure.create", "onboarding.create_plan", "route_export.create_visit_route"}
        for row in caps:
            cid = row.get("capability_id")
            if cid in approvals and not row.get("human_approval_required"):
                rc |= fail(f"{cid} must require human approval")

    blob_dump = json.dumps(catalog).lower()
    if "postgresql://" in blob_dump or "mongodb+srv://" in blob_dump:
        rc |= fail("connection string leaked into capability export snapshot")

    base_url = os.environ.get("VERIFY_BASE_URL")
    if base_url:
        url = base_url.rstrip("/") + "/api/v1/system/capabilities"
        try:
            req = Request(url, headers={"User-Agent": "verify-h020/1"})
            with urlopen(req, timeout=12) as resp:
                raw = resp.read().decode("utf-8")
            live = json.loads(raw)
            if resp.status != 200:
                rc |= fail(f"live probe status={resp.status}")
            if not isinstance(live.get("capabilities"), list):
                rc |= fail("live response missing capability list")
            live_caps = live.get("capabilities") or []
            if len(live_caps) < 100:
                rc |= fail("live capability count unexpectedly low (<129)")
        except HTTPError as exc:
            rc |= fail(f"live probe HTTP error {exc.code}")
        except URLError as exc:
            rc |= fail(f"live probe URL error {exc.reason}")
        except json.JSONDecodeError:
            rc |= fail("live response not JSON")
        except Exception as exc:
            rc |= fail(f"live probe failed {exc}")

    try:
        env = os.environ.copy()
        env["SOARB2B_API_KEYS"] = "verify-h020-key"
        env.setdefault("JWT_SECRET", "verify-h020-jwt-secret-32characters!!!!")
        out = subprocess.run(
            [sys.executable, "-m", "pytest", str(BACKEND / "tests" / "test_semantic_capabilities.py"), "-q"],
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        if out.returncode != 0:
            rc |= fail(f"pytest semantic capabilities failed:\n{out.stdout}\n{out.stderr}")
        else:
            ok("pytest tests/test_semantic_capabilities.py passed")
    except Exception as exc:
        rc |= fail(f"pytest launcher error: {exc}")

    if rc == 0:
        print("PASS: H-020 verification complete.", flush=True)
    else:
        print("FAIL: H-020 verification incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
