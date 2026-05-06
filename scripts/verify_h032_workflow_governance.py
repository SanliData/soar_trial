***REMOVED***!/usr/bin/env python3
"""
H-032 verification: workflow governance foundation.
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
    REPO_ROOT / "docs" / "H-032_WORKFLOW_GOVERNANCE_LAYER.md",
    REPO_ROOT / "docs" / "H-032_IMPLEMENTATION_PROOF.md",
    BACKEND / "src" / "workflow_governance" / "__init__.py",
    BACKEND / "src" / "workflow_governance" / "workflow_contract_registry.py",
    BACKEND / "src" / "workflow_governance" / "adaptive_effort_service.py",
    BACKEND / "src" / "workflow_governance" / "delegation_policy_service.py",
    BACKEND / "src" / "workflow_governance" / "workflow_session_service.py",
    BACKEND / "src" / "workflow_governance" / "context_decay_service.py",
    BACKEND / "src" / "workflow_governance" / "subagent_parallelization_service.py",
    BACKEND / "src" / "workflow_governance" / "workflow_acceptance_service.py",
    BACKEND / "src" / "workflow_governance" / "workflow_validation_service.py",
    BACKEND / "src" / "http" / "v1" / "workflow_governance_router.py",
    BACKEND / "tests" / "test_workflow_governance.py",
    BACKEND / "src" / "ui" / "en" / "workflow_governance_demo.html",
    BACKEND / "src" / "ui" / "tr" / "workflow_governance_demo.html",
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


def wg_router_is_thin(path: Path) -> bool:
    txt = path.read_text(encoding="utf-8")
    if "workflow_compress_bundle" not in txt:
        return False
    if "from src.workflow_governance.context_decay_service import workflow_compress_bundle" not in txt:
        return False
    if "def detect_context_rot" in txt or "def workflow_compress_bundle" in txt:
        return False
    return True


def main() -> int:
    rc = 0
    print("H-032 verification...", flush=True)

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
    if "workflow_governance_router" in app_txt and "include_router(workflow_governance_router" in app_txt:
        ok("app.py registers workflow_governance_router")
    else:
        rc |= fail("app.py missing workflow_governance_router")

    wr = BACKEND / "src" / "http" / "v1" / "workflow_governance_router.py"
    if wr.exists():
        rt = wr.read_text(encoding="utf-8")
        if "workflow_governance_foundation" not in rt:
            rc |= fail("router missing workflow_governance_foundation envelope")
        else:
            ok("router defines governance envelope")
        if rt.count("unrestricted_autonomous_execution") < 1:
            rc |= fail("router missing unrestricted_autonomous_execution declaration")
        if not wg_router_is_thin(wr):
            rc |= fail("workflow governance router must delegate compress/decay to services")
        else:
            ok("workflow governance router delegates to services")

    pkg = BACKEND / "src" / "workflow_governance"
    if pkg.is_dir():
        combined = "".join(p.read_text(encoding="utf-8", errors="replace") for p in pkg.glob("*.py"))
        if UNSAFE_MARKERS.search(combined):
            rc |= fail("unsafe execution markers in workflow_governance package")
        else:
            ok("no unsafe execution markers in workflow_governance package")

    reg = BACKEND / "src" / "semantic_capabilities" / "capability_registry.py"
    if reg.exists():
        rtxt = reg.read_text(encoding="utf-8")
        for cid in (
            "workflows.contracts",
            "workflows.sessions",
            "workflows.compress",
            "workflows.validate",
            "workflows.runtime_summary",
        ):
            if cid not in rtxt:
                rc |= fail(f"capability_registry missing {cid}")
        ok("semantic registry lists workflow governance capabilities")

    mb = BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html"
    if mb.exists() and "H-032 Delegated Autonomous Workflow Execution" in mb.read_text(encoding="utf-8"):
        ok("MainBook contains H-032 section")
    else:
        rc |= fail("MainBook missing H-032")

    lb = BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html"
    if lb.exists() and "H-032 Verification" in lb.read_text(encoding="utf-8"):
        ok("LiveBook contains H-032 verification")
    else:
        rc |= fail("LiveBook missing H-032 verification")

    bl = REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md"
    if bl.exists() and "H-032" in bl.read_text(encoding="utf-8"):
        ok("Master backlog references H-032")
    else:
        rc |= fail("Master backlog missing H-032")

    for h in scan_secrets([p for p in scanned if p.exists() and p.suffix == ".py"]):
        rc |= fail(f"secret heuristic: {h}")

    base_url = os.environ.get("VERIFY_BASE_URL")
    if base_url:
        root = base_url.rstrip("/")
        try:
            for path in (
                "/api/v1/system/workflows/contracts",
                "/api/v1/system/workflows/runtime-summary",
            ):
                req = Request(root + path, headers={"User-Agent": "verify-h032/1"})
                with urlopen(req, timeout=15) as resp:
                    if resp.status != 200:
                        rc |= fail(f"live GET {path} status {resp.status}")
                    body = json.loads(resp.read().decode("utf-8"))
                    if body.get("unrestricted_autonomous_execution") is not False:
                        rc |= fail(f"live envelope invalid for {path}")
            for path, data in (
                (
                    "/api/v1/system/workflows/session",
                    {"workflow_name": "opportunity_ranking", "label": "verify"},
                ),
                (
                    "/api/v1/system/workflows/validate",
                    {
                        "workflow_name": "opportunity_ranking",
                        "outputs": {
                            "ranked_list": 1,
                            "score_breakdown": 1,
                            "exclusion_rules": 1,
                        },
                        "constraints_respected": True,
                        "escalation_acknowledged": True,
                    },
                ),
            ):
                req = Request(
                    root + path,
                    data=json.dumps(data).encode("utf-8"),
                    method="POST",
                    headers={"User-Agent": "verify-h032/1", "Content-Type": "application/json"},
                )
                with urlopen(req, timeout=15) as resp:
                    if resp.status != 200:
                        rc |= fail(f"live POST {path} status {resp.status}")
                    body = json.loads(resp.read().decode("utf-8"))
                    if body.get("recursive_workflow_swarm") is not False:
                        rc |= fail(f"live envelope invalid for {path}")
            ok("live VERIFY_BASE_URL workflow governance smoke passed")
        except (HTTPError, URLError, json.JSONDecodeError, KeyError, TypeError) as exc:
            rc |= fail(f"live probe failed: {exc}")

    try:
        env = os.environ.copy()
        env.setdefault("JWT_SECRET", "verify-h032-jwt-secret-32characters!!!")
        env.setdefault("SOARB2B_API_KEYS", "verify-h032-key")
        out = subprocess.run(
            [sys.executable, "-m", "pytest", str(BACKEND / "tests" / "test_workflow_governance.py"), "-q"],
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        if out.returncode != 0:
            rc |= fail(f"pytest failed:\n{out.stdout}\n{out.stderr}")
        else:
            ok("pytest tests/test_workflow_governance.py passed")
    except Exception as exc:
        rc |= fail(f"pytest launcher: {exc}")

    print("PASS: H-032 verification complete." if rc == 0 else "FAIL: H-032 incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
