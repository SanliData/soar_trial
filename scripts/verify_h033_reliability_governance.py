***REMOVED***!/usr/bin/env python3
"""
H-033 verification: production AI reliability governance foundation.
Exit code 0 only if structural checks + pytest pass.
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

REQUIRED_FILES = [
    REPO_ROOT / "docs" / "H-033_RELIABILITY_GOVERNANCE_LAYER.md",
    REPO_ROOT / "docs" / "H-033_IMPLEMENTATION_PROOF.md",
    BACKEND / "src" / "reliability_governance" / "__init__.py",
    BACKEND / "src" / "reliability_governance" / "drift_monitoring_service.py",
    BACKEND / "src" / "reliability_governance" / "evaluation_governance_service.py",
    BACKEND / "src" / "reliability_governance" / "embedding_health_service.py",
    BACKEND / "src" / "reliability_governance" / "retrieval_quality_service.py",
    BACKEND / "src" / "reliability_governance" / "workflow_reliability_service.py",
    BACKEND / "src" / "reliability_governance" / "runtime_observability_service.py",
    BACKEND / "src" / "reliability_governance" / "context_stability_service.py",
    BACKEND / "src" / "reliability_governance" / "reliability_validation_service.py",
    BACKEND / "src" / "http" / "v1" / "reliability_governance_router.py",
    BACKEND / "tests" / "test_reliability_governance.py",
    BACKEND / "src" / "ui" / "en" / "reliability_governance_demo.html",
    BACKEND / "src" / "ui" / "tr" / "reliability_governance_demo.html",
]

SECRET_PATTERNS = [
    (re.compile(r"(?i)sk_live_[0-9a-zA-Z]{16,}"), "Stripe-like"),
]

UNSAFE_MARKERS = re.compile(r"(?i)(\beval\s*\(|exec\s*\(|subprocess\.|socket\.socket\s*\()")


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


def scan_secrets(paths: list[Path]) -> list[str]:
    bad: list[str] = []
    for p in paths:
        if not p.exists() or p.suffix not in {".py", ".md"}:
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        for rx, label in SECRET_PATTERNS:
            if rx.search(txt):
                bad.append(f"{p.relative_to(REPO_ROOT)} ({label})")
    return bad


def reliability_router_is_thin(path: Path) -> bool:
    txt = path.read_text(encoding="utf-8")
    if "export_drift_report" not in txt:
        return False
    if "from src.reliability_governance.drift_monitoring_service import export_drift_report" not in txt:
        return False
    if "def export_drift_report" in txt or "def detect_drift" in txt:
        return False
    return True


def main() -> int:
    rc = 0
    print("H-033 verification...", flush=True)

    for p in REQUIRED_FILES:
        if p.exists():
            ok(f"exists: {p.relative_to(REPO_ROOT)}")
        else:
            rc |= fail(f"missing {p.relative_to(REPO_ROOT)}")

    scanned = REQUIRED_FILES + [
        BACKEND / "src" / "app.py",
        BACKEND / "src" / "semantic_capabilities" / "capability_registry.py",
        BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html",
        BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html",
        REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md",
        Path(__file__).resolve(),
    ]

    for p in scanned:
        if p.exists() and p.is_file():
            if has_bom(p):
                rc |= fail(f"BOM: {p.relative_to(REPO_ROOT)}")
            else:
                ok(f"No BOM: {p.relative_to(REPO_ROOT)}")

    app_txt = (BACKEND / "src" / "app.py").read_text(encoding="utf-8")
    if "reliability_governance_router" in app_txt and "include_router(reliability_governance_router" in app_txt:
        ok("app.py registers reliability_governance_router")
    else:
        rc |= fail("app.py missing reliability_governance_router")

    rr = BACKEND / "src" / "http" / "v1" / "reliability_governance_router.py"
    if rr.exists():
        rt = rr.read_text(encoding="utf-8")
        if "reliability_governance_foundation" not in rt:
            rc |= fail("router missing reliability_governance_foundation envelope")
        else:
            ok("router defines governance envelope")
        if rt.count("distributed_observability_mesh") < 1:
            rc |= fail("router missing distributed_observability_mesh declaration")
        if not reliability_router_is_thin(rr):
            rc |= fail("reliability router must delegate scoring to services")
        else:
            ok("reliability router delegates to services")

    pkg = BACKEND / "src" / "reliability_governance"
    if pkg.is_dir():
        combined = "".join(p.read_text(encoding="utf-8", errors="replace") for p in pkg.glob("*.py"))
        if UNSAFE_MARKERS.search(combined):
            rc |= fail("unsafe execution markers in reliability_governance package")
        else:
            ok("no unsafe execution markers in reliability_governance package")

    reg = BACKEND / "src" / "semantic_capabilities" / "capability_registry.py"
    if reg.exists():
        rtxt = reg.read_text(encoding="utf-8")
        for cid in (
            "reliability.drift",
            "reliability.retrieval",
            "reliability.embeddings",
            "reliability.workflows",
            "reliability.context",
            "reliability.traces",
        ):
            if cid not in rtxt:
                rc |= fail(f"capability_registry missing {cid}")
        ok("semantic registry lists reliability capabilities")

    mb = BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html"
    if mb.exists() and "H-033 Production AI Reliability" in mb.read_text(encoding="utf-8"):
        ok("MainBook contains H-033 section")
    else:
        rc |= fail("MainBook missing H-033")

    lb = BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html"
    if lb.exists() and "H-033 Verification" in lb.read_text(encoding="utf-8"):
        ok("LiveBook contains H-033 verification")
    else:
        rc |= fail("LiveBook missing H-033 verification")

    bl = REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md"
    if bl.exists() and "H-033" in bl.read_text(encoding="utf-8"):
        ok("Master backlog references H-033")
    else:
        rc |= fail("Master backlog missing H-033")

    for h in scan_secrets([p for p in scanned if p.exists() and p.suffix == ".py"]):
        rc |= fail(f"secret heuristic: {h}")

    base_url = os.environ.get("VERIFY_BASE_URL")
    if base_url:
        root = base_url.rstrip("/")
        try:
            for path in (
                "/api/v1/system/reliability/drift",
                "/api/v1/system/reliability/retrieval",
                "/api/v1/system/reliability/embeddings",
                "/api/v1/system/reliability/workflows",
                "/api/v1/system/reliability/context",
                "/api/v1/system/reliability/traces",
            ):
                req = Request(root + path, headers={"User-Agent": "verify-h033/1"})
                with urlopen(req, timeout=15) as resp:
                    if resp.status != 200:
                        rc |= fail(f"live GET {path} status {resp.status}")
                    body = json.loads(resp.read().decode("utf-8"))
                    if body.get("distributed_observability_mesh") is not False:
                        rc |= fail(f"live envelope invalid for {path}")
            ok("live VERIFY_BASE_URL reliability smoke passed")
        except (HTTPError, URLError, json.JSONDecodeError, KeyError, TypeError) as exc:
            rc |= fail(f"live probe failed: {exc}")

    try:
        env = os.environ.copy()
        env.setdefault("JWT_SECRET", "verify-h033-jwt-secret-32characters!!!")
        env.setdefault("SOARB2B_API_KEYS", "verify-h033-key")
        out = subprocess.run(
            [sys.executable, "-m", "pytest", str(BACKEND / "tests" / "test_reliability_governance.py"), "-q"],
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        if out.returncode != 0:
            rc |= fail(f"pytest failed:\n{out.stdout}\n{out.stderr}")
        else:
            ok("pytest tests/test_reliability_governance.py passed")
    except Exception as exc:
        rc |= fail(f"pytest launcher: {exc}")

    print("PASS: H-033 verification complete." if rc == 0 else "FAIL: H-033 incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
