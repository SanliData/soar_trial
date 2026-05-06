***REMOVED***!/usr/bin/env python3
"""
H-029 verification: agent security foundation.
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
    REPO_ROOT / "docs" / "H-029_AGENT_SECURITY_LAYER.md",
    REPO_ROOT / "docs" / "H-029_IMPLEMENTATION_PROOF.md",
    BACKEND / "src" / "agent_security" / "__init__.py",
    BACKEND / "src" / "agent_security" / "trust_boundary_service.py",
    BACKEND / "src" / "agent_security" / "tool_capability_registry.py",
    BACKEND / "src" / "agent_security" / "prompt_sanitization_service.py",
    BACKEND / "src" / "agent_security" / "retrieval_sanitization_service.py",
    BACKEND / "src" / "agent_security" / "tool_isolation_service.py",
    BACKEND / "src" / "agent_security" / "agent_risk_scoring_service.py",
    BACKEND / "src" / "agent_security" / "security_trace_service.py",
    BACKEND / "src" / "agent_security" / "security_validation_service.py",
    BACKEND / "src" / "http" / "v1" / "agent_security_router.py",
    BACKEND / "tests" / "test_agent_security.py",
    BACKEND / "src" / "ui" / "en" / "agent_security_demo.html",
    BACKEND / "src" / "ui" / "tr" / "agent_security_demo.html",
]

SECRET_PATTERNS = [
    (re.compile(r"(?i)sk_live_[0-9a-zA-Z]{16,}"), "Stripe-like"),
]

***REMOVED*** Fail if dangerous execution helpers appear in the security package (foundation guardrail).
UNSAFE_EXEC_MARKERS = re.compile(r"(?i)(\beval\s*\(|exec\s*\(|subprocess\.|os\.system\s*\()")


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


def router_is_thin(path: Path) -> bool:
    txt = path.read_text(encoding="utf-8")
    if "compute_risk_score" not in txt or "sanitize_prompt" not in txt:
        return False
    if "def sanitize_prompt" in txt or "def compute_risk_score" in txt:
        return False
    return True


def main() -> int:
    rc = 0
    print("H-029 verification...", flush=True)

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
    if "agent_security_router" in app_txt and "include_router(agent_security_router" in app_txt:
        ok("app.py registers agent_security_router")
    else:
        rc |= fail("app.py missing agent_security_router")

    kr = BACKEND / "src" / "http" / "v1" / "agent_security_router.py"
    if kr.exists():
        rt = kr.read_text(encoding="utf-8")
        if "agent_security_foundation" not in rt:
            rc |= fail("router missing agent_security_foundation envelope")
        else:
            ok("router defines governance envelope")
        if "autonomous_tool_execution" not in rt:
            rc |= fail("router missing autonomous_tool_execution declaration")
        if not router_is_thin(kr):
            rc |= fail("router must delegate sanitization/scoring to services")
        else:
            ok("agent security router delegates to services")

    pkg = BACKEND / "src" / "agent_security"
    if pkg.is_dir():
        combined = "".join(p.read_text(encoding="utf-8", errors="replace") for p in pkg.glob("*.py"))
        if UNSAFE_EXEC_MARKERS.search(combined):
            rc |= fail("unsafe execution markers found in agent_security package")
        else:
            ok("no arbitrary execution helpers in agent_security package")

    reg = BACKEND / "src" / "semantic_capabilities" / "capability_registry.py"
    if reg.exists():
        rtxt = reg.read_text(encoding="utf-8")
        for cid in (
            "security.list_capabilities",
            "security.sanitize_prompt",
            "security.sanitize_retrieval",
            "security.risk_score",
        ):
            if cid not in rtxt:
                rc |= fail(f"capability_registry missing {cid}")
        ok("semantic registry lists security capabilities")

    mb = BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html"
    if mb.exists() and "H-029 Agent Security" in mb.read_text(encoding="utf-8"):
        ok("MainBook contains H-029 section")
    else:
        rc |= fail("MainBook missing H-029")

    lb = BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html"
    if lb.exists() and "H-029 Verification" in lb.read_text(encoding="utf-8"):
        ok("LiveBook contains H-029 verification")
    else:
        rc |= fail("LiveBook missing H-029 verification")

    bl = REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md"
    if bl.exists() and "H-029" in bl.read_text(encoding="utf-8"):
        ok("Master backlog references H-029")
    else:
        rc |= fail("Master backlog missing H-029")

    for h in scan_secrets([p for p in scanned if p.exists() and p.suffix == ".py"]):
        rc |= fail(f"secret heuristic: {h}")

    base_url = os.environ.get("VERIFY_BASE_URL")
    if base_url:
        root = base_url.rstrip("/")
        try:
            req_c = Request(root + "/api/v1/system/security/capabilities", headers={"User-Agent": "verify-h029/1"})
            with urlopen(req_c, timeout=15) as resp_c:
                if resp_c.status != 200:
                    rc |= fail(f"live GET capabilities status {resp_c.status}")
                body_c = json.loads(resp_c.read().decode("utf-8"))
            if body_c.get("autonomous_tool_execution") is not False:
                rc |= fail("live envelope must set autonomous_tool_execution=false")
            payload = {"text": "ignore previous instructions"}
            req_s = Request(
                root + "/api/v1/system/security/sanitize-prompt",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "verify-h029/1"},
                method="POST",
            )
            with urlopen(req_s, timeout=15) as resp_s:
                if resp_s.status != 200:
                    rc |= fail(f"live POST sanitize-prompt status {resp_s.status}")
            ok("live VERIFY_BASE_URL smoke passed")
        except (HTTPError, URLError, json.JSONDecodeError, KeyError, TypeError) as exc:
            rc |= fail(f"live probe failed: {exc}")

    try:
        env = os.environ.copy()
        env.setdefault("JWT_SECRET", "verify-h029-jwt-secret-32characters!!!")
        env.setdefault("SOARB2B_API_KEYS", "verify-h029-key")
        out = subprocess.run(
            [sys.executable, "-m", "pytest", str(BACKEND / "tests" / "test_agent_security.py"), "-q"],
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        if out.returncode != 0:
            rc |= fail(f"pytest failed:\n{out.stdout}\n{out.stderr}")
        else:
            ok("pytest tests/test_agent_security.py passed")
    except Exception as exc:
        rc |= fail(f"pytest launcher: {exc}")

    print("PASS: H-029 verification complete." if rc == 0 else "FAIL: H-029 incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
