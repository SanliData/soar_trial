***REMOVED***!/usr/bin/env python3
"""
H-043 verification: long-context, private runtime isolation, ensemble governance foundations.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND = REPO_ROOT / "backend"

REQUIRED_FILES = [
    REPO_ROOT / "docs" / "H-043_LONG_CONTEXT_PRIVATE_RUNTIME_ENSEMBLE_LAYER.md",
    REPO_ROOT / "docs" / "H-043_IMPLEMENTATION_PROOF.md",
    BACKEND / "src" / "long_context_runtime" / "__init__.py",
    BACKEND / "src" / "long_context_runtime" / "adaptive_context_loader.py",
    BACKEND / "src" / "long_context_runtime" / "context_pressure_service.py",
    BACKEND / "src" / "long_context_runtime" / "context_partition_service.py",
    BACKEND / "src" / "long_context_runtime" / "sparse_activation_service.py",
    BACKEND / "src" / "long_context_runtime" / "long_context_validation_service.py",
    BACKEND / "src" / "long_context_runtime" / "retrieval_fallback_service.py",
    BACKEND / "src" / "long_context_runtime" / "h043_inference_hooks.py",
    BACKEND / "src" / "private_runtime_security" / "__init__.py",
    BACKEND / "src" / "private_runtime_security" / "private_mesh_policy_service.py",
    BACKEND / "src" / "private_runtime_security" / "runtime_isolation_service.py",
    BACKEND / "src" / "private_runtime_security" / "execution_boundary_service.py",
    BACKEND / "src" / "private_runtime_security" / "network_exposure_service.py",
    BACKEND / "src" / "private_runtime_security" / "tailscale_policy_service.py",
    BACKEND / "src" / "private_runtime_security" / "non_root_execution_service.py",
    BACKEND / "src" / "private_runtime_security" / "runtime_access_validation.py",
    BACKEND / "src" / "ensemble_governance" / "__init__.py",
    BACKEND / "src" / "ensemble_governance" / "multi_evaluator_service.py",
    BACKEND / "src" / "ensemble_governance" / "consensus_scoring_service.py",
    BACKEND / "src" / "ensemble_governance" / "variance_detection_service.py",
    BACKEND / "src" / "ensemble_governance" / "evaluation_randomization_service.py",
    BACKEND / "src" / "ensemble_governance" / "ensemble_validation_service.py",
    BACKEND / "src" / "http" / "v1" / "long_context_runtime_router.py",
    BACKEND / "src" / "http" / "v1" / "private_runtime_security_router.py",
    BACKEND / "src" / "http" / "v1" / "ensemble_governance_router.py",
    BACKEND / "tests" / "test_h043_long_context_private_runtime.py",
    BACKEND / "src" / "ui" / "en" / "long_context_runtime_demo.html",
    BACKEND / "src" / "ui" / "tr" / "long_context_runtime_demo.html",
    BACKEND / "src" / "ui" / "en" / "private_runtime_security_demo.html",
    BACKEND / "src" / "ui" / "tr" / "private_runtime_security_demo.html",
    BACKEND / "src" / "ui" / "en" / "ensemble_governance_demo.html",
    BACKEND / "src" / "ui" / "tr" / "ensemble_governance_demo.html",
]

SECRET_RX = [(re.compile(r"(?i)sk_live_[0-9a-zA-Z]{16,}"), "Stripe-like")]
UNSAFE = re.compile(r"(?i)(\beval\s*\(|exec\s*\(|subprocess\.|socket\.socket\s*\()")


def ok(msg: str) -> None:
    print(f"PASS: {msg}", flush=True)


def fail(msg: str) -> int:
    print(f"FAIL: {msg}", flush=True)
    return 1


def has_bom(p: Path) -> bool:
    try:
        return p.read_bytes().startswith(b"\xef\xbb\xbf")
    except OSError:
        return False


def router_thin(p: Path) -> bool:
    t = p.read_text(encoding="utf-8")
    return "APIRouter(" in t and "def export_" not in t


def main() -> int:
    rc = 0
    print("H-043 verification...", flush=True)

    for p in REQUIRED_FILES:
        if p.exists():
            ok(f"exists: {p.relative_to(REPO_ROOT)}")
        else:
            rc |= fail(f"missing {p.relative_to(REPO_ROOT)}")

    scanned = REQUIRED_FILES + [
        BACKEND / "src" / "app.py",
        BACKEND / "src" / "capability_gateway" / "provider_abstraction_service.py",
        BACKEND / "src" / "skill_runtime" / "skill_registry_service.py",
        BACKEND / "src" / "inference_runtime" / "runtime_telemetry_service.py",
        BACKEND / "src" / "agent_proxy_firewall" / "runtime_anomaly_alignment_service.py",
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

    at = (BACKEND / "src" / "app.py").read_text(encoding="utf-8")
    for nid in ("long_context_runtime_router", "private_runtime_security_router", "ensemble_governance_router"):
        if nid in at and f"include_router({nid}" in at:
            ok(f"app.py registers {nid}")
        else:
            rc |= fail(f"app.py missing {nid}")

    for rel in ("http/v1/long_context_runtime_router.py", "http/v1/private_runtime_security_router.py", "http/v1/ensemble_governance_router.py"):
        p = BACKEND / "src" / rel
        if not router_thin(p):
            rc |= fail(f"thin router required: {rel}")
        ok(f"thin: {rel}")

    for pkg in ("long_context_runtime", "private_runtime_security", "ensemble_governance"):
        txt = "".join(x.read_text(encoding="utf-8", errors="replace") for x in (BACKEND / "src" / pkg).glob("*.py"))
        if UNSAFE.search(txt):
            rc |= fail(f"unsafe markers in {pkg}")
        ok(f"safe scan: {pkg}")

    ap = BACKEND / "src" / "capability_gateway" / "provider_abstraction_service.py"
    if ap.exists() and "sparse_long_context_metadata_by_provider" in ap.read_text(encoding="utf-8"):
        ok("H-037 provider sparse metadata present")
    else:
        rc |= fail("provider abstraction missing H-043 metadata")

    sk = BACKEND / "src" / "skill_runtime" / "skill_registry_service.py"
    if sk.exists() and "context_weight" in sk.read_text(encoding="utf-8"):
        ok("H-040 skill context integration present")
    else:
        rc |= fail("skill registry missing H-043 fields")

    inf = BACKEND / "src" / "inference_runtime" / "runtime_telemetry_service.py"
    if inf.exists() and "h043_long_context_integration" in inf.read_text(encoding="utf-8"):
        ok("H-041 telemetry H-043 hooks present")
    else:
        rc |= fail("inference telemetry missing H-043 integration")

    fw = BACKEND / "src" / "agent_proxy_firewall" / "runtime_anomaly_alignment_service.py"
    if fw.exists() and "h043_private_runtime_exposure_alignment" in fw.read_text(encoding="utf-8"):
        ok("H-039 firewall H-043 alignment present")
    else:
        rc |= fail("firewall alignment missing H-043")

    mb = BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html"
    if mb.exists() and "H-043 Long-Context Sparse Inference" in mb.read_text(encoding="utf-8"):
        ok("MainBook H-043")
    else:
        rc |= fail("MainBook missing H-043")

    lb = BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html"
    if lb.exists() and "H-043 Verification" in lb.read_text(encoding="utf-8"):
        ok("LiveBook H-043")
    else:
        rc |= fail("LiveBook missing H-043")

    bl = REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md"
    if bl.exists() and "***REMOVED******REMOVED*** H-043" in bl.read_text(encoding="utf-8"):
        ok("backlog H-043")
    else:
        rc |= fail("backlog missing H-043")

    for p in scanned:
        if p.suffix == ".py" and p.exists():
            t = p.read_text(encoding="utf-8", errors="replace")
            for rx, lab in SECRET_RX:
                if rx.search(t):
                    rc |= fail(f"secret hint {lab}: {p.relative_to(REPO_ROOT)}")

    base = os.environ.get("VERIFY_BASE_URL")
    if base:
        root = base.rstrip("/")
        try:
            for path in (
                "/api/v1/system/context/pressure",
                "/api/v1/system/runtime/isolation",
                "/api/v1/system/ensemble/consensus",
            ):
                req = Request(root + path, headers={"User-Agent": "verify-h043/1"})
                with urlopen(req, timeout=15) as resp:
                    if resp.status != 200:
                        rc |= fail(f"live {path} status {resp.status}")
                    js = json.loads(resp.read().decode("utf-8"))
                    flag = js.get("unrestricted_long_context_loading")
                    if path.startswith("/api/v1/system/context") and flag is not False:
                        rc |= fail(f"context envelope invalid {path}")
            ok("VERIFY_BASE_URL smoke")
        except (HTTPError, URLError, OSError, json.JSONDecodeError, TypeError) as e:
            rc |= fail(f"live probe {e}")

    env = os.environ.copy()
    env.setdefault("JWT_SECRET", "verify-h043-jwt-secret-32characters!!")
    env.setdefault("SOARB2B_API_KEYS", "verify-h043-key")
    out = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(BACKEND / "tests" / "test_h043_long_context_private_runtime.py"),
            str(BACKEND / "tests" / "test_inference_runtime.py"),
            str(BACKEND / "tests" / "test_agent_proxy_firewall.py"),
            str(BACKEND / "tests" / "test_skill_runtime.py"),
            "-q",
        ],
        cwd=str(BACKEND),
        capture_output=True,
        text=True,
        timeout=300,
        env=env,
    )
    if out.returncode != 0:
        rc |= fail(f"pytest:\n{out.stdout}\n{out.stderr}")
    else:
        ok("pytest H-043 + inference + firewall + skill_runtime")

    print("PASS: H-043 verification complete." if rc == 0 else "FAIL: H-043 incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
