***REMOVED***!/usr/bin/env python3
"""
H-022 verification: reflection-driven prompt optimization foundation.
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
    REPO_ROOT / "docs" / "H-022_REFLECTION_OPTIMIZATION_LAYER.md",
    REPO_ROOT / "docs" / "H-022_IMPLEMENTATION_PROOF.md",
    BACKEND / "src" / "reflection_optimization" / "__init__.py",
    BACKEND / "src" / "reflection_optimization" / "reflection_schema.py",
    BACKEND / "src" / "reflection_optimization" / "reflection_trace_service.py",
    BACKEND / "src" / "reflection_optimization" / "feedback_contracts.py",
    BACKEND / "src" / "reflection_optimization" / "prompt_candidate_registry.py",
    BACKEND / "src" / "reflection_optimization" / "prompt_revision_service.py",
    BACKEND / "src" / "reflection_optimization" / "optimization_history_service.py",
    BACKEND / "src" / "reflection_optimization" / "reflection_validation_service.py",
    BACKEND / "src" / "http" / "v1" / "reflection_optimization_router.py",
    BACKEND / "tests" / "test_reflection_optimization.py",
    BACKEND / "src" / "ui" / "en" / "reflection_review_demo.html",
    BACKEND / "src" / "ui" / "tr" / "reflection_review_demo.html",
]

SECRET_PATTERNS = [
    (re.compile(r"(?i)sk_live_[0-9a-zA-Z]{16,}"), "Stripe-like"),
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


def main() -> int:
    rc = 0
    print("H-022 verification...", flush=True)

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
    if "reflection_optimization_router" in app_txt and "include_router(reflection_optimization_router" in app_txt:
        ok("app.py registers reflection_optimization_router")
    else:
        rc |= fail("app.py missing reflection_optimization_router")

    rt = (BACKEND / "src" / "http" / "v1" / "reflection_optimization_router.py").read_text(encoding="utf-8")
    if "autonomous_execution" not in rt:
        rc |= fail("router missing autonomous_execution envelope")
    else:
        ok("router defines autonomous_execution")

    deploy_hits = [ln for ln in rt.splitlines() if re.search(r"\bdeploy\b", ln, re.I) and not ln.strip().startswith("***REMOVED***")]
    if deploy_hits:
        rc |= fail(f"router mentions deploy (forbidden auto-deploy hints): {deploy_hits[:2]}")

    mb = BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html"
    if mb.exists() and "H-022 Reflection-Driven" in mb.read_text(encoding="utf-8"):
        ok("MainBook contains H-022 section")
    else:
        rc |= fail("MainBook missing H-022")

    lb = BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html"
    if lb.exists() and "H-022 Verification" in lb.read_text(encoding="utf-8"):
        ok("LiveBook contains H-022 verification")
    else:
        rc |= fail("LiveBook missing H-022 verification")

    bl = REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md"
    if bl.exists() and "H-022" in bl.read_text(encoding="utf-8"):
        ok("Master backlog references H-022")
    else:
        rc |= fail("Master backlog missing H-022")

    reg = BACKEND / "src" / "semantic_capabilities" / "capability_registry.py"
    if reg.exists():
        rtxt = reg.read_text(encoding="utf-8")
        for cid in (
            "reflection.record_trace",
            "reflection.create_candidate",
            "reflection.list_candidates",
            "reflection.approve_candidate",
            "reflection.reject_candidate",
        ):
            if cid not in rtxt:
                rc |= fail(f"capability_registry missing {cid}")
        ok("semantic registry lists reflection capabilities")

    ref_pkg = BACKEND / "src" / "reflection_optimization"
    if ref_pkg.is_dir():
        py_files = list(ref_pkg.glob("*.py"))
        combined = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in py_files)
        for banned in ("openai", "anthropic", "vllm", "fine_tune", "peft"):
            if banned in combined.lower():
                rc |= fail(f"forbidden token in reflection package: {banned}")

    for h in scan_secrets([p for p in scanned if p.exists() and p.suffix == ".py"]):
        rc |= fail(f"secret heuristic: {h}")

    base_url = os.environ.get("VERIFY_BASE_URL")
    if base_url:
        root = base_url.rstrip("/")
        try:
            trace_payload = {
                "task_type": "executive_briefing",
                "workflow_name": "live.verify",
                "success": False,
                "score": 0.2,
                "failure_modes": ["overly_generic_executive_summary"],
            }
            req_t = Request(
                root + "/api/v1/system/reflection/trace",
                data=json.dumps(trace_payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "verify-h022/1"},
                method="POST",
            )
            with urlopen(req_t, timeout=15) as resp:
                trace_status = resp.status
                t_body = json.loads(resp.read().decode("utf-8"))
            if trace_status != 200:
                rc |= fail(f"live trace status {trace_status}")
            if t_body.get("autonomous_execution") is not False:
                rc |= fail("live trace autonomous_execution must be false")
            tid = t_body["trace"]["trace_id"]

            req_c = Request(
                root + "/api/v1/system/reflection/candidate",
                data=json.dumps({"trace_id": tid}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(req_c, timeout=15) as resp2:
                c_body = json.loads(resp2.read().decode("utf-8"))
            cand = c_body.get("candidate") or {}
            if cand.get("human_review_required") is not True:
                rc |= fail("live candidate human_review_required")
            if cand.get("approval_status") != "pending":
                rc |= fail("live candidate must start pending")

            req_g = Request(root + "/api/v1/system/reflection/candidates", headers={"User-Agent": "verify-h022/1"})
            with urlopen(req_g, timeout=15) as resp3:
                g_body = json.loads(resp3.read().decode("utf-8"))
            if g_body.get("autonomous_execution") is not False:
                rc |= fail("live list autonomous_execution")
            ok("live VERIFY_BASE_URL smoke passed")
        except (HTTPError, URLError, json.JSONDecodeError, KeyError) as exc:
            rc |= fail(f"live probe failed: {exc}")

    try:
        env = os.environ.copy()
        env.setdefault("JWT_SECRET", "verify-h022-jwt-secret-32characters!")
        env.setdefault("SOARB2B_API_KEYS", "verify-h022-key")
        out = subprocess.run(
            [sys.executable, "-m", "pytest", str(BACKEND / "tests" / "test_reflection_optimization.py"), "-q"],
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        if out.returncode != 0:
            rc |= fail(f"pytest failed:\n{out.stdout}\n{out.stderr}")
        else:
            ok("pytest tests/test_reflection_optimization.py passed")
    except Exception as exc:
        rc |= fail(f"pytest launcher: {exc}")

    print("PASS: H-022 verification complete." if rc == 0 else "FAIL: H-022 incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
