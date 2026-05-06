***REMOVED***!/usr/bin/env python3
"""
H-031 verification: agent harness architecture foundation.
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
    REPO_ROOT / "docs" / "H-031_AGENT_HARNESS_ARCHITECTURE.md",
    REPO_ROOT / "docs" / "H-031_IMPLEMENTATION_PROOF.md",
    BACKEND / "src" / "agent_harness" / "__init__.py",
    BACKEND / "src" / "agent_harness" / "memory_registry.py",
    BACKEND / "src" / "agent_harness" / "skill_registry.py",
    BACKEND / "src" / "agent_harness" / "protocol_registry.py",
    BACKEND / "src" / "agent_harness" / "evaluation_router.py",
    BACKEND / "src" / "agent_harness" / "compression_service.py",
    BACKEND / "src" / "agent_harness" / "subagent_boundary_service.py",
    BACKEND / "src" / "agent_harness" / "harness_runtime_service.py",
    BACKEND / "src" / "agent_harness" / "harness_validation_service.py",
    BACKEND / "src" / "http" / "v1" / "agent_harness_router.py",
    BACKEND / "tests" / "test_agent_harness.py",
    BACKEND / "src" / "ui" / "en" / "agent_harness_demo.html",
    BACKEND / "src" / "ui" / "tr" / "agent_harness_demo.html",
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


def harness_router_is_thin(path: Path) -> bool:
    txt = path.read_text(encoding="utf-8")
    if "compress_bundle" not in txt:
        return False
    if "from src.agent_harness.compression_service import compress_bundle" not in txt:
        return False
    if "def summarize_context" in txt or "def compress_trajectory" in txt:
        return False
    return True


def main() -> int:
    rc = 0
    print("H-031 verification...", flush=True)

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
    if "agent_harness_router" in app_txt and "include_router(agent_harness_router" in app_txt:
        ok("app.py registers agent_harness_router")
    else:
        rc |= fail("app.py missing agent_harness_router")

    hr = BACKEND / "src" / "http" / "v1" / "agent_harness_router.py"
    if hr.exists():
        rt = hr.read_text(encoding="utf-8")
        if "agent_harness_foundation" not in rt:
            rc |= fail("router missing agent_harness_foundation envelope")
        else:
            ok("router defines governance envelope")
        if rt.count("recursive_agent_swarm") < 1:
            rc |= fail("router missing recursive_agent_swarm declaration")
        if not harness_router_is_thin(hr):
            rc |= fail("harness router must delegate compression to services")
        else:
            ok("harness router delegates compression to services")

    pkg = BACKEND / "src" / "agent_harness"
    if pkg.is_dir():
        combined = "".join(p.read_text(encoding="utf-8", errors="replace") for p in pkg.glob("*.py"))
        if UNSAFE_MARKERS.search(combined):
            rc |= fail("unsafe execution markers in agent_harness package")
        else:
            ok("no unsafe execution markers in agent_harness package")

    reg = BACKEND / "src" / "semantic_capabilities" / "capability_registry.py"
    if reg.exists():
        rtxt = reg.read_text(encoding="utf-8")
        for cid in (
            "harness.memory",
            "harness.skills",
            "harness.protocols",
            "harness.compress",
            "harness.runtime_summary",
        ):
            if cid not in rtxt:
                rc |= fail(f"capability_registry missing {cid}")
        ok("semantic registry lists harness capabilities")

    mb = BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html"
    if mb.exists() and "H-031 Agent Harness Architecture" in mb.read_text(encoding="utf-8"):
        ok("MainBook contains H-031 section")
    else:
        rc |= fail("MainBook missing H-031")

    lb = BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html"
    if lb.exists() and "H-031 Verification" in lb.read_text(encoding="utf-8"):
        ok("LiveBook contains H-031 verification")
    else:
        rc |= fail("LiveBook missing H-031 verification")

    bl = REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md"
    if bl.exists() and "H-031" in bl.read_text(encoding="utf-8"):
        ok("Master backlog references H-031")
    else:
        rc |= fail("Master backlog missing H-031")

    for h in scan_secrets([p for p in scanned if p.exists() and p.suffix == ".py"]):
        rc |= fail(f"secret heuristic: {h}")

    base_url = os.environ.get("VERIFY_BASE_URL")
    if base_url:
        root = base_url.rstrip("/")
        try:
            for path, method, body in (
                ("/api/v1/system/harness/memory", "GET", None),
                ("/api/v1/system/harness/skills", "GET", None),
                ("/api/v1/system/harness/protocols", "GET", None),
                (
                    "/api/v1/system/harness/compress",
                    "POST",
                    json.dumps({"mode": "context", "payload": "x" * 400}).encode("utf-8"),
                ),
            ):
                req = Request(
                    root + path,
                    data=body,
                    method=method,
                    headers={"User-Agent": "verify-h031/1", "Content-Type": "application/json"},
                )
                with urlopen(req, timeout=15) as resp:
                    if resp.status != 200:
                        rc |= fail(f"live {method} {path} status {resp.status}")
                    payload = json.loads(resp.read().decode("utf-8"))
                    if payload.get("recursive_agent_swarm") is not False:
                        rc |= fail(f"live envelope invalid for {path}")
            ok("live VERIFY_BASE_URL harness smoke passed")
        except (HTTPError, URLError, json.JSONDecodeError, KeyError, TypeError) as exc:
            rc |= fail(f"live probe failed: {exc}")

    try:
        env = os.environ.copy()
        env.setdefault("JWT_SECRET", "verify-h031-jwt-secret-32characters!!!")
        env.setdefault("SOARB2B_API_KEYS", "verify-h031-key")
        out = subprocess.run(
            [sys.executable, "-m", "pytest", str(BACKEND / "tests" / "test_agent_harness.py"), "-q"],
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        if out.returncode != 0:
            rc |= fail(f"pytest failed:\n{out.stdout}\n{out.stderr}")
        else:
            ok("pytest tests/test_agent_harness.py passed")
    except Exception as exc:
        rc |= fail(f"pytest launcher: {exc}")

    print("PASS: H-031 verification complete." if rc == 0 else "FAIL: H-031 incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
