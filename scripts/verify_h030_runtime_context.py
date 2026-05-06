***REMOVED***!/usr/bin/env python3
"""
H-030 verification: runtime context engineering foundation.
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
    REPO_ROOT / "docs" / "H-030_RUNTIME_CONTEXT_ENGINEERING.md",
    REPO_ROOT / "docs" / "H-030_IMPLEMENTATION_PROOF.md",
    BACKEND / "src" / "runtime_context" / "__init__.py",
    BACKEND / "src" / "runtime_context" / "backend_metadata_service.py",
    BACKEND / "src" / "runtime_context" / "capability_snapshot_service.py",
    BACKEND / "src" / "runtime_context" / "runtime_topology_service.py",
    BACKEND / "src" / "runtime_context" / "orchestration_context_service.py",
    BACKEND / "src" / "runtime_context" / "runtime_hint_service.py",
    BACKEND / "src" / "runtime_context" / "context_budget_service.py",
    BACKEND / "src" / "runtime_context" / "context_trace_service.py",
    BACKEND / "src" / "runtime_context" / "runtime_context_validation_service.py",
    BACKEND / "src" / "http" / "v1" / "runtime_context_router.py",
    BACKEND / "tests" / "test_runtime_context.py",
    BACKEND / "src" / "ui" / "en" / "runtime_context_demo.html",
    BACKEND / "src" / "ui" / "tr" / "runtime_context_demo.html",
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


def router_is_thin(path: Path) -> bool:
    txt = path.read_text(encoding="utf-8")
    if "apply_context_budget" not in txt:
        return False
    if "def apply_context_budget" in txt:
        return False
    return True


def main() -> int:
    rc = 0
    print("H-030 verification...", flush=True)

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
    if "runtime_context_router" in app_txt and "include_router(runtime_context_router" in app_txt:
        ok("app.py registers runtime_context_router")
    else:
        rc |= fail("app.py missing runtime_context_router")

    kr = BACKEND / "src" / "http" / "v1" / "runtime_context_router.py"
    if kr.exists():
        rt = kr.read_text(encoding="utf-8")
        if "runtime_context_foundation" not in rt:
            rc |= fail("router missing runtime_context_foundation envelope")
        else:
            ok("router defines governance envelope")
        if "runtime_self_modification" not in rt:
            rc |= fail("router missing runtime_self_modification declaration")
        if not router_is_thin(kr):
            rc |= fail("router must delegate budgeting to services")
        else:
            ok("runtime router delegates to services")

    pkg = BACKEND / "src" / "runtime_context"
    if pkg.is_dir():
        combined = "".join(p.read_text(encoding="utf-8", errors="replace") for p in pkg.glob("*.py"))
        if UNSAFE_MARKERS.search(combined):
            rc |= fail("unsafe introspection/execution markers in runtime_context package")
        else:
            ok("no unsafe introspection markers in runtime_context package")

    reg = BACKEND / "src" / "semantic_capabilities" / "capability_registry.py"
    if reg.exists():
        rtxt = reg.read_text(encoding="utf-8")
        for cid in (
            "runtime.metadata",
            "runtime.capabilities",
            "runtime.topology",
            "runtime.hints",
            "runtime.context_budget",
        ):
            if cid not in rtxt:
                rc |= fail(f"capability_registry missing {cid}")
        ok("semantic registry lists runtime capabilities")

    mb = BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html"
    if mb.exists() and "H-030 Backend Context Engineering" in mb.read_text(encoding="utf-8"):
        ok("MainBook contains H-030 section")
    else:
        rc |= fail("MainBook missing H-030")

    lb = BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html"
    if lb.exists() and "H-030 Verification" in lb.read_text(encoding="utf-8"):
        ok("LiveBook contains H-030 verification")
    else:
        rc |= fail("LiveBook missing H-030 verification")

    bl = REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md"
    if bl.exists() and "H-030" in bl.read_text(encoding="utf-8"):
        ok("Master backlog references H-030")
    else:
        rc |= fail("Master backlog missing H-030")

    for h in scan_secrets([p for p in scanned if p.exists() and p.suffix == ".py"]):
        rc |= fail(f"secret heuristic: {h}")

    base_url = os.environ.get("VERIFY_BASE_URL")
    if base_url:
        root = base_url.rstrip("/")
        try:
            for path in (
                "/api/v1/system/runtime/metadata",
                "/api/v1/system/runtime/capabilities",
                "/api/v1/system/runtime/topology",
                "/api/v1/system/runtime/hints",
            ):
                req = Request(root + path, headers={"User-Agent": "verify-h030/1"})
                with urlopen(req, timeout=15) as resp:
                    if resp.status != 200:
                        rc |= fail(f"live GET {path} status {resp.status}")
                    body = json.loads(resp.read().decode("utf-8"))
                    if body.get("runtime_self_modification") is not False:
                        rc |= fail(f"live envelope invalid for {path}")
            ok("live VERIFY_BASE_URL GET smoke passed")
        except (HTTPError, URLError, json.JSONDecodeError, KeyError, TypeError) as exc:
            rc |= fail(f"live probe failed: {exc}")

    try:
        env = os.environ.copy()
        env.setdefault("JWT_SECRET", "verify-h030-jwt-secret-32characters!!!")
        env.setdefault("SOARB2B_API_KEYS", "verify-h030-key")
        out = subprocess.run(
            [sys.executable, "-m", "pytest", str(BACKEND / "tests" / "test_runtime_context.py"), "-q"],
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        if out.returncode != 0:
            rc |= fail(f"pytest failed:\n{out.stdout}\n{out.stderr}")
        else:
            ok("pytest tests/test_runtime_context.py passed")
    except Exception as exc:
        rc |= fail(f"pytest launcher: {exc}")

    print("PASS: H-030 verification complete." if rc == 0 else "FAIL: H-030 incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
