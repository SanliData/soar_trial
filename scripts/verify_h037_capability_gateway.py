***REMOVED***!/usr/bin/env python3
"""
H-037 verification: capability gateway governance foundation.
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
    REPO_ROOT / "docs" / "H-037_CAPABILITY_GATEWAY_LAYER.md",
    REPO_ROOT / "docs" / "H-037_IMPLEMENTATION_PROOF.md",
    BACKEND / "src" / "capability_gateway" / "__init__.py",
    BACKEND / "src" / "capability_gateway" / "mcp_gateway_registry.py",
    BACKEND / "src" / "capability_gateway" / "provider_abstraction_service.py",
    BACKEND / "src" / "capability_gateway" / "capability_execution_policy.py",
    BACKEND / "src" / "capability_gateway" / "local_inference_service.py",
    BACKEND / "src" / "capability_gateway" / "external_tool_governance_service.py",
    BACKEND / "src" / "capability_gateway" / "browser_automation_policy_service.py",
    BACKEND / "src" / "capability_gateway" / "hybrid_serving_service.py",
    BACKEND / "src" / "capability_gateway" / "gateway_validation_service.py",
    BACKEND / "src" / "http" / "v1" / "capability_gateway_router.py",
    BACKEND / "tests" / "test_capability_gateway.py",
    BACKEND / "src" / "ui" / "en" / "capability_gateway_demo.html",
    BACKEND / "src" / "ui" / "tr" / "capability_gateway_demo.html",
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


def gateway_router_is_thin(path: Path) -> bool:
    txt = path.read_text(encoding="utf-8")
    if "export_gateways_manifest" not in txt:
        return False
    if "def export_execution_policies(" in txt:
        return False
    if "def select_provider(" in txt:
        return False
    return True


def main() -> int:
    rc = 0
    print("H-037 verification...", flush=True)

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
    if "capability_gateway_router" in app_txt and "include_router(capability_gateway_router" in app_txt:
        ok("app.py registers capability_gateway_router")
    else:
        rc |= fail("app.py missing capability_gateway_router")

    gr = BACKEND / "src" / "http" / "v1" / "capability_gateway_router.py"
    if gr.exists():
        rt = gr.read_text(encoding="utf-8")
        if "capability_gateway_foundation" not in rt:
            rc |= fail("router missing capability_gateway_foundation envelope")
        else:
            ok("router defines governance envelope")
        if rt.count("unrestricted_tool_chaining") < 1:
            rc |= fail("router missing unrestricted_tool_chaining declaration")
        if not gateway_router_is_thin(gr):
            rc |= fail("capability gateway router must delegate to services")
        else:
            ok("capability gateway router delegates to services")

    pkg = BACKEND / "src" / "capability_gateway"
    if pkg.is_dir():
        combined = "".join(p.read_text(encoding="utf-8", errors="replace") for p in pkg.glob("*.py"))
        if UNSAFE_MARKERS.search(combined):
            rc |= fail("unsafe execution markers in capability_gateway package")
        else:
            ok("no unsafe execution markers in capability_gateway package")

    reg = BACKEND / "src" / "capability_gateway" / "mcp_gateway_registry.py"
    if reg.exists() and "GATEWAYS" in reg.read_text(encoding="utf-8") and "browser_intelligence" in reg.read_text(encoding="utf-8"):
        ok("gateway registry defines static gateways")
    else:
        rc |= fail("mcp_gateway_registry incomplete")

    ep = BACKEND / "src" / "capability_gateway" / "capability_execution_policy.py"
    if ep.exists() and "export_execution_policies" in ep.read_text(encoding="utf-8"):
        ok("execution policies export present")
    else:
        rc |= fail("capability_execution_policy incomplete")

    pa = BACKEND / "src" / "capability_gateway" / "provider_abstraction_service.py"
    if pa.exists() and "select_provider" in pa.read_text(encoding="utf-8"):
        ok("provider abstraction present")
    else:
        rc |= fail("provider_abstraction_service incomplete")

    bp = BACKEND / "src" / "capability_gateway" / "browser_automation_policy_service.py"
    if bp.exists() and "unrestricted_browser_automation" in bp.read_text(encoding="utf-8"):
        ok("browser automation policy declares sandbox constraints")
    else:
        rc |= fail("browser_automation_policy_service incomplete")

    cap_reg = BACKEND / "src" / "semantic_capabilities" / "capability_registry.py"
    if cap_reg.exists():
        crt = cap_reg.read_text(encoding="utf-8")
        for cid in (
            "gateways.registry",
            "gateways.providers",
            "gateways.execution_policies",
            "gateways.browser_policies",
            "gateways.hybrid_serving",
        ):
            if f'capability_id="{cid}"' not in crt:
                rc |= fail(f"capability_registry missing {cid}")
        ok("H-020 capability_registry includes gateways.* entries")

    mb = BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html"
    if mb.exists() and "H-037 Local-First AI Infrastructure" in mb.read_text(encoding="utf-8"):
        ok("MainBook contains H-037 section")
    else:
        rc |= fail("MainBook missing H-037")

    lb = BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html"
    if lb.exists() and "H-037 Verification" in lb.read_text(encoding="utf-8"):
        ok("LiveBook contains H-037 verification")
    else:
        rc |= fail("LiveBook missing H-037 verification")

    bl = REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md"
    if bl.exists() and "***REMOVED******REMOVED*** H-037" in bl.read_text(encoding="utf-8"):
        ok("Master backlog references H-037")
    else:
        rc |= fail("Master backlog missing H-037")

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
                "/api/v1/system/gateways",
                "/api/v1/system/providers",
                "/api/v1/system/browser-policies",
                "/api/v1/system/hybrid-serving",
            ):
                req = Request(root + path, headers={"User-Agent": "verify-h037/1"})
                with urlopen(req, timeout=15) as resp:
                    if resp.status != 200:
                        rc |= fail(f"live GET {path} status {resp.status}")
                    body = json.loads(resp.read().decode("utf-8"))
                    if body.get("unrestricted_external_execution") is not False:
                        rc |= fail(f"live envelope invalid for {path}")
            ok("live VERIFY_BASE_URL capability gateway smoke passed")
        except (HTTPError, URLError, json.JSONDecodeError, KeyError, TypeError) as exc:
            rc |= fail(f"live probe failed: {exc}")

    try:
        env = os.environ.copy()
        env.setdefault("JWT_SECRET", "verify-h037-jwt-secret-32characters!!!")
        env.setdefault("SOARB2B_API_KEYS", "verify-h037-key")
        out = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(BACKEND / "tests" / "test_capability_gateway.py"),
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
            ok("pytest test_capability_gateway + test_semantic_capabilities passed")
    except Exception as exc:
        rc |= fail(f"pytest launcher: {exc}")

    print("PASS: H-037 verification complete." if rc == 0 else "FAIL: H-037 incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
