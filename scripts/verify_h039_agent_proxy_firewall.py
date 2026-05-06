***REMOVED***!/usr/bin/env python3
"""
H-039 verification: agent proxy firewall foundation.
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
    REPO_ROOT / "docs" / "H-039_AGENT_PROXY_FIREWALL.md",
    REPO_ROOT / "docs" / "H-039_IMPLEMENTATION_PROOF.md",
    BACKEND / "src" / "agent_proxy_firewall" / "__init__.py",
    BACKEND / "src" / "agent_proxy_firewall" / "proxy_gateway_service.py",
    BACKEND / "src" / "agent_proxy_firewall" / "input_filter_chain_service.py",
    BACKEND / "src" / "agent_proxy_firewall" / "output_filter_chain_service.py",
    BACKEND / "src" / "agent_proxy_firewall" / "policy_interceptor_service.py",
    BACKEND / "src" / "agent_proxy_firewall" / "execution_firewall_service.py",
    BACKEND / "src" / "agent_proxy_firewall" / "sensitive_action_guard_service.py",
    BACKEND / "src" / "agent_proxy_firewall" / "compression_resilience_service.py",
    BACKEND / "src" / "agent_proxy_firewall" / "trace_interception_service.py",
    BACKEND / "src" / "agent_proxy_firewall" / "firewall_validation_service.py",
    BACKEND / "src" / "http" / "v1" / "agent_proxy_firewall_router.py",
    BACKEND / "tests" / "test_agent_proxy_firewall.py",
    BACKEND / "src" / "ui" / "en" / "agent_proxy_firewall_demo.html",
    BACKEND / "src" / "ui" / "tr" / "agent_proxy_firewall_demo.html",
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


def firewall_router_is_thin(path: Path) -> bool:
    txt = path.read_text(encoding="utf-8")
    if "export_proxy_gateways_manifest" not in txt:
        return False
    if "def export_proxy_gateways_manifest(" in txt:
        return False
    if "def assess_input_payload(" in txt:
        return False
    return True


def main() -> int:
    rc = 0
    print("H-039 verification...", flush=True)

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
    if "agent_proxy_firewall_router" in app_txt and "include_router(agent_proxy_firewall_router" in app_txt:
        ok("app.py registers agent_proxy_firewall_router")
    else:
        rc |= fail("app.py missing agent_proxy_firewall_router")

    fr = BACKEND / "src" / "http" / "v1" / "agent_proxy_firewall_router.py"
    if fr.exists():
        rt = fr.read_text(encoding="utf-8")
        if "agent_proxy_firewall_foundation" not in rt:
            rc |= fail("router missing agent_proxy_firewall_foundation envelope")
        else:
            ok("router defines governance envelope")
        if rt.count("unrestricted_autonomous_execution") < 1:
            rc |= fail("router missing unrestricted_autonomous_execution declaration")
        if not firewall_router_is_thin(fr):
            rc |= fail("firewall router must delegate to services")
        else:
            ok("firewall router delegates to services")

    pkg = BACKEND / "src" / "agent_proxy_firewall"
    if pkg.is_dir():
        combined = "".join(p.read_text(encoding="utf-8", errors="replace") for p in pkg.glob("*.py"))
        if UNSAFE_MARKERS.search(combined):
            rc |= fail("unsafe execution markers in agent_proxy_firewall package")
        else:
            ok("no unsafe execution markers in agent_proxy_firewall package")

    inp = BACKEND / "src" / "agent_proxy_firewall" / "input_filter_chain_service.py"
    if inp.exists() and "INPUT_FILTER_CHAIN" in inp.read_text(encoding="utf-8"):
        ok("input filter chain present")
    else:
        rc |= fail("input_filter_chain_service incomplete")

    out = BACKEND / "src" / "agent_proxy_firewall" / "output_filter_chain_service.py"
    if out.exists() and "OUTPUT_FILTER_CHAIN" in out.read_text(encoding="utf-8"):
        ok("output filter chain present")
    else:
        rc |= fail("output_filter_chain_service incomplete")

    pol = BACKEND / "src" / "agent_proxy_firewall" / "policy_interceptor_service.py"
    if pol.exists() and "export_policy_interception_manifest" in pol.read_text(encoding="utf-8"):
        ok("policy interception export present")
    else:
        rc |= fail("policy_interceptor_service incomplete")

    cr = BACKEND / "src" / "agent_proxy_firewall" / "compression_resilience_service.py"
    if cr.exists() and "proxy_enforcement_mandatory" in cr.read_text(encoding="utf-8"):
        ok("compression resilience manifest present")
    else:
        rc |= fail("compression_resilience_service incomplete")

    cap_reg = BACKEND / "src" / "semantic_capabilities" / "capability_registry.py"
    if cap_reg.exists():
        crt = cap_reg.read_text(encoding="utf-8")
        for cid in (
            "firewall.gateways",
            "firewall.input_filters",
            "firewall.output_filters",
            "firewall.policies",
            "firewall.protected_actions",
        ):
            if f'capability_id="{cid}"' not in crt:
                rc |= fail(f"capability_registry missing {cid}")
        ok("H-020 capability_registry includes firewall.* entries")

    mb = BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html"
    if mb.exists() and "H-039 AI Proxy Firewall" in mb.read_text(encoding="utf-8"):
        ok("MainBook contains H-039 section")
    else:
        rc |= fail("MainBook missing H-039")

    lb = BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html"
    if lb.exists() and "H-039 Verification" in lb.read_text(encoding="utf-8"):
        ok("LiveBook contains H-039 verification")
    else:
        rc |= fail("LiveBook missing H-039 verification")

    bl = REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md"
    if bl.exists() and "***REMOVED******REMOVED*** H-039" in bl.read_text(encoding="utf-8"):
        ok("Master backlog references H-039")
    else:
        rc |= fail("Master backlog missing H-039")

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
                "/api/v1/system/firewall/input-filters",
                "/api/v1/system/firewall/output-filters",
                "/api/v1/system/firewall/policies",
                "/api/v1/system/firewall/interception-traces",
            ):
                req = Request(root + path, headers={"User-Agent": "verify-h039/1"})
                with urlopen(req, timeout=15) as resp:
                    if resp.status != 200:
                        rc |= fail(f"live GET {path} status {resp.status}")
                    body = json.loads(resp.read().decode("utf-8"))
                    if body.get("unrestricted_autonomous_execution") is not False:
                        rc |= fail(f"live envelope invalid for {path}")
            ok("live VERIFY_BASE_URL firewall smoke passed")
        except (HTTPError, URLError, json.JSONDecodeError, KeyError, TypeError) as exc:
            rc |= fail(f"live probe failed: {exc}")

    try:
        env = os.environ.copy()
        env.setdefault("JWT_SECRET", "verify-h039-jwt-secret-32characters!!!")
        env.setdefault("SOARB2B_API_KEYS", "verify-h039-key")
        out = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(BACKEND / "tests" / "test_agent_proxy_firewall.py"),
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
            ok("pytest test_agent_proxy_firewall + test_semantic_capabilities passed")
    except Exception as exc:
        rc |= fail(f"pytest launcher: {exc}")

    print("PASS: H-039 verification complete." if rc == 0 else "FAIL: H-039 incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
