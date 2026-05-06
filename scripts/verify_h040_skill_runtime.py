***REMOVED***!/usr/bin/env python3
"""
H-040 verification: governed skill runtime foundation.
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
    REPO_ROOT / "docs" / "H-040_SKILL_RUNTIME_LAYER.md",
    REPO_ROOT / "docs" / "H-040_IMPLEMENTATION_PROOF.md",
    BACKEND / "src" / "skill_runtime" / "__init__.py",
    BACKEND / "src" / "skill_runtime" / "skill_registry_service.py",
    BACKEND / "src" / "skill_runtime" / "dynamic_skill_loader.py",
    BACKEND / "src" / "skill_runtime" / "skill_activation_service.py",
    BACKEND / "src" / "skill_runtime" / "skill_permission_service.py",
    BACKEND / "src" / "skill_runtime" / "skill_dependency_service.py",
    BACKEND / "src" / "skill_runtime" / "skill_context_optimizer.py",
    BACKEND / "src" / "skill_runtime" / "skill_execution_trace_service.py",
    BACKEND / "src" / "skill_runtime" / "skill_validation_service.py",
    BACKEND / "src" / "http" / "v1" / "skill_runtime_router.py",
    BACKEND / "tests" / "test_skill_runtime.py",
    BACKEND / "src" / "ui" / "en" / "skill_runtime_demo.html",
    BACKEND / "src" / "ui" / "tr" / "skill_runtime_demo.html",
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


def skill_router_is_thin(path: Path) -> bool:
    txt = path.read_text(encoding="utf-8")
    if "export_skill_registry_manifest" not in txt:
        return False
    if "def export_skill_registry_manifest(" in txt:
        return False
    if "def plan_skill_load(" in txt:
        return False
    return True


def main() -> int:
    rc = 0
    print("H-040 verification...", flush=True)

    for p in REQUIRED_FILES:
        if p.exists():
            ok(f"exists: {p.relative_to(REPO_ROOT)}")
        else:
            rc |= fail(f"missing {p.relative_to(REPO_ROOT)}")

    scanned = REQUIRED_FILES + [
        BACKEND / "src" / "semantic_capabilities" / "capability_registry.py",
        BACKEND / "src" / "app.py",
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
    if "skill_runtime_router" in app_txt and "include_router(skill_runtime_router" in app_txt:
        ok("app.py registers skill_runtime_router")
    else:
        rc |= fail("app.py missing skill_runtime_router")

    sr = BACKEND / "src" / "http" / "v1" / "skill_runtime_router.py"
    if sr.exists():
        rt = sr.read_text(encoding="utf-8")
        if "skill_runtime_foundation" not in rt:
            rc |= fail("router missing skill_runtime_foundation envelope")
        else:
            ok("router defines governance envelope")
        if rt.count("unrestricted_skill_spawning") < 1:
            rc |= fail("router missing unrestricted_skill_spawning declaration")
        if not skill_router_is_thin(sr):
            rc |= fail("skill runtime router must delegate to services")
        else:
            ok("skill runtime router delegates to services")

    pkg = BACKEND / "src" / "skill_runtime"
    if pkg.is_dir():
        combined = "".join(p.read_text(encoding="utf-8", errors="replace") for p in pkg.glob("*.py"))
        if UNSAFE_MARKERS.search(combined):
            rc |= fail("unsafe execution markers in skill_runtime package")
        else:
            ok("no unsafe execution markers in skill_runtime package")

    reg = BACKEND / "src" / "skill_runtime" / "skill_registry_service.py"
    if reg.exists() and "SKILL_REGISTRY" in reg.read_text(encoding="utf-8"):
        ok("skill registry present")
    else:
        rc |= fail("skill_registry_service incomplete")

    dyn = BACKEND / "src" / "skill_runtime" / "dynamic_skill_loader.py"
    if dyn.exists() and "plan_skill_load" in dyn.read_text(encoding="utf-8"):
        ok("dynamic skill loader present")
    else:
        rc |= fail("dynamic_skill_loader incomplete")

    perm = BACKEND / "src" / "skill_runtime" / "skill_permission_service.py"
    if perm.exists() and "least_privilege_enforced" in perm.read_text(encoding="utf-8"):
        ok("skill permission governance present")
    else:
        rc |= fail("skill_permission_service incomplete")

    ctx = BACKEND / "src" / "skill_runtime" / "skill_context_optimizer.py"
    if ctx.exists() and "export_context_optimization_manifest" in ctx.read_text(encoding="utf-8"):
        ok("context optimization present")
    else:
        rc |= fail("skill_context_optimizer incomplete")

    cap_reg = BACKEND / "src" / "semantic_capabilities" / "capability_registry.py"
    if cap_reg.exists():
        crt = cap_reg.read_text(encoding="utf-8")
        for cid in (
            "skills.registry",
            "skills.activation",
            "skills.permissions",
            "skills.dependencies",
            "skills.context_optimization",
        ):
            if f'capability_id="{cid}"' not in crt:
                rc |= fail(f"capability_registry missing {cid}")
        ok("H-020 capability_registry includes skills.* entries")

    mb = BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html"
    if mb.exists() and "H-040 Scoped AI Skill Runtime" in mb.read_text(encoding="utf-8"):
        ok("MainBook contains H-040 section")
    else:
        rc |= fail("MainBook missing H-040")

    lb = BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html"
    if lb.exists() and "H-040 Verification" in lb.read_text(encoding="utf-8"):
        ok("LiveBook contains H-040 verification")
    else:
        rc |= fail("LiveBook missing H-040 verification")

    bl = REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md"
    if bl.exists() and "***REMOVED******REMOVED*** H-040" in bl.read_text(encoding="utf-8"):
        ok("Master backlog references H-040")
    else:
        rc |= fail("Master backlog missing H-040")

    try:
        env_py = os.environ.copy()
        env_py["PYTHONPATH"] = str(BACKEND)
        chk = subprocess.run(
            [
                sys.executable,
                "-c",
                "from src.semantic_capabilities.capability_registry import CAPABILITY_DEFINITIONS; "
                "assert len(CAPABILITY_DEFINITIONS) == 145",
            ],
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            timeout=30,
            env=env_py,
        )
        if chk.returncode != 0:
            rc |= fail(f"capability count check failed:\n{chk.stdout}\n{chk.stderr}")
        else:
            ok("semantic capability count is 145")
    except Exception as exc:
        rc |= fail(f"capability count launcher: {exc}")

    for h in scan_secrets([p for p in scanned if p.exists() and p.suffix == ".py"]):
        rc |= fail(f"secret heuristic: {h}")

    base_url = os.environ.get("VERIFY_BASE_URL")
    if base_url:
        root = base_url.rstrip("/")
        try:
            for path in (
                "/api/v1/system/skills",
                "/api/v1/system/skills/active",
                "/api/v1/system/skills/permissions",
                "/api/v1/system/skills/traces",
            ):
                req = Request(root + path, headers={"User-Agent": "verify-h040/1"})
                with urlopen(req, timeout=15) as resp:
                    if resp.status != 200:
                        rc |= fail(f"live GET {path} status {resp.status}")
                    body = json.loads(resp.read().decode("utf-8"))
                    if body.get("unrestricted_skill_spawning") is not False:
                        rc |= fail(f"live envelope invalid for {path}")
            ok("live VERIFY_BASE_URL skill runtime smoke passed")
        except (HTTPError, URLError, json.JSONDecodeError, KeyError, TypeError) as exc:
            rc |= fail(f"live probe failed: {exc}")

    try:
        env = os.environ.copy()
        env.setdefault("JWT_SECRET", "verify-h040-jwt-secret-32characters!!!")
        env.setdefault("SOARB2B_API_KEYS", "verify-h040-key")
        out = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(BACKEND / "tests" / "test_skill_runtime.py"),
                str(BACKEND / "tests" / "test_semantic_capabilities.py"),
                "-q",
            ],
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            timeout=180,
            env=env,
        )
        if out.returncode != 0:
            rc |= fail(f"pytest failed:\n{out.stdout}\n{out.stderr}")
        else:
            ok("pytest test_skill_runtime + test_semantic_capabilities passed")
    except Exception as exc:
        rc |= fail(f"pytest launcher: {exc}")

    print("PASS: H-040 verification complete." if rc == 0 else "FAIL: H-040 incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
