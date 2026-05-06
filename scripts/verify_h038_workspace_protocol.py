***REMOVED***!/usr/bin/env python3
"""
H-038 verification: workspace protocol governance foundation.
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
    REPO_ROOT / "docs" / "H-038_WORKSPACE_PROTOCOL.md",
    REPO_ROOT / "docs" / "H-038_IMPLEMENTATION_PROOF.md",
    BACKEND / "src" / "workspace_protocol" / "__init__.py",
    BACKEND / "src" / "workspace_protocol" / "workspace_policy_registry.py",
    BACKEND / "src" / "workspace_protocol" / "runtime_rule_service.py",
    BACKEND / "src" / "workspace_protocol" / "project_memory_service.py",
    BACKEND / "src" / "workspace_protocol" / "agent_scope_service.py",
    BACKEND / "src" / "workspace_protocol" / "workspace_command_registry.py",
    BACKEND / "src" / "workspace_protocol" / "workspace_skill_registry.py",
    BACKEND / "src" / "workspace_protocol" / "permission_governance_service.py",
    BACKEND / "src" / "workspace_protocol" / "workspace_validation_service.py",
    BACKEND / "src" / "http" / "v1" / "workspace_protocol_router.py",
    BACKEND / "tests" / "test_workspace_protocol.py",
    BACKEND / "src" / "ui" / "en" / "workspace_protocol_demo.html",
    BACKEND / "src" / "ui" / "tr" / "workspace_protocol_demo.html",
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


def workspace_router_is_thin(path: Path) -> bool:
    txt = path.read_text(encoding="utf-8")
    if "export_workspace_policies_manifest" not in txt:
        return False
    if "def export_workspace_policies_manifest(" in txt:
        return False
    if "def export_runtime_rules_manifest(" in txt:
        return False
    if "def export_project_memory_manifest(" in txt:
        return False
    return True


def main() -> int:
    rc = 0
    print("H-038 verification...", flush=True)

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
    if "workspace_protocol_router" in app_txt and "include_router(workspace_protocol_router" in app_txt:
        ok("app.py registers workspace_protocol_router")
    else:
        rc |= fail("app.py missing workspace_protocol_router")

    wr = BACKEND / "src" / "http" / "v1" / "workspace_protocol_router.py"
    if wr.exists():
        rt = wr.read_text(encoding="utf-8")
        if "workspace_protocol_foundation" not in rt:
            rc |= fail("router missing workspace_protocol_foundation envelope")
        else:
            ok("router defines governance envelope")
        if rt.count("uncontrolled_agent_spawning") < 1:
            rc |= fail("router missing uncontrolled_agent_spawning declaration")
        if not workspace_router_is_thin(wr):
            rc |= fail("workspace protocol router must delegate to services")
        else:
            ok("workspace protocol router delegates to services")

    pkg = BACKEND / "src" / "workspace_protocol"
    if pkg.is_dir():
        combined = "".join(p.read_text(encoding="utf-8", errors="replace") for p in pkg.glob("*.py"))
        if UNSAFE_MARKERS.search(combined):
            rc |= fail("unsafe execution markers in workspace_protocol package")
        else:
            ok("no unsafe execution markers in workspace_protocol package")

    wpr = BACKEND / "src" / "workspace_protocol" / "workspace_policy_registry.py"
    if wpr.exists() and "WORKSPACE_POLICIES" in wpr.read_text(encoding="utf-8"):
        ok("workspace policies registry present")
    else:
        rc |= fail("workspace_policy_registry incomplete")

    rrs = BACKEND / "src" / "workspace_protocol" / "runtime_rule_service.py"
    if rrs.exists() and "export_runtime_rules_manifest" in rrs.read_text(encoding="utf-8"):
        ok("runtime rules export present")
    else:
        rc |= fail("runtime_rule_service incomplete")

    pms = BACKEND / "src" / "workspace_protocol" / "project_memory_service.py"
    if pms.exists() and "unrestricted_persistent_memory" in pms.read_text(encoding="utf-8"):
        ok("project memory declares unrestricted persistence false")
    else:
        rc |= fail("project_memory_service incomplete")

    pgs = BACKEND / "src" / "workspace_protocol" / "permission_governance_service.py"
    if pgs.exists() and "hidden_execution_permissions" in pgs.read_text(encoding="utf-8"):
        ok("permission governance present")
    else:
        rc |= fail("permission_governance_service incomplete")

    cap_reg = BACKEND / "src" / "semantic_capabilities" / "capability_registry.py"
    if cap_reg.exists():
        crt = cap_reg.read_text(encoding="utf-8")
        for cid in (
            "workspace.policies",
            "workspace.rules",
            "workspace.memory",
            "workspace.commands",
            "workspace.skills",
            "workspace.permissions",
        ):
            if f'capability_id="{cid}"' not in crt:
                rc |= fail(f"capability_registry missing {cid}")
        ok("H-020 capability_registry includes workspace.* entries")

    mb = BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html"
    if mb.exists() and "H-038 AI Workspace Protocol" in mb.read_text(encoding="utf-8"):
        ok("MainBook contains H-038 section")
    else:
        rc |= fail("MainBook missing H-038")

    lb = BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html"
    if lb.exists() and "H-038 Verification" in lb.read_text(encoding="utf-8"):
        ok("LiveBook contains H-038 verification")
    else:
        rc |= fail("LiveBook missing H-038 verification")

    bl = REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md"
    if bl.exists() and "***REMOVED******REMOVED*** H-038" in bl.read_text(encoding="utf-8"):
        ok("Master backlog references H-038")
    else:
        rc |= fail("Master backlog missing H-038")

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
                "/api/v1/system/workspaces/policies",
                "/api/v1/system/workspaces/rules",
                "/api/v1/system/workspaces/memory",
                "/api/v1/system/workspaces/commands",
            ):
                req = Request(root + path, headers={"User-Agent": "verify-h038/1"})
                with urlopen(req, timeout=15) as resp:
                    if resp.status != 200:
                        rc |= fail(f"live GET {path} status {resp.status}")
                    body = json.loads(resp.read().decode("utf-8"))
                    if body.get("unrestricted_persistent_memory") is not False:
                        rc |= fail(f"live envelope invalid for {path}")
            ok("live VERIFY_BASE_URL workspace protocol smoke passed")
        except (HTTPError, URLError, json.JSONDecodeError, KeyError, TypeError) as exc:
            rc |= fail(f"live probe failed: {exc}")

    try:
        env = os.environ.copy()
        env.setdefault("JWT_SECRET", "verify-h038-jwt-secret-32characters!!!")
        env.setdefault("SOARB2B_API_KEYS", "verify-h038-key")
        out = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(BACKEND / "tests" / "test_workspace_protocol.py"),
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
            ok("pytest test_workspace_protocol + test_semantic_capabilities passed")
    except Exception as exc:
        rc |= fail(f"pytest launcher: {exc}")

    print("PASS: H-038 verification complete." if rc == 0 else "FAIL: H-038 incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
