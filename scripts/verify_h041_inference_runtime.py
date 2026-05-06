***REMOVED***!/usr/bin/env python3
"""
H-041 verification: governed inference runtime governance foundation.
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
    REPO_ROOT / "docs" / "H-041_INFERENCE_RUNTIME_LAYER.md",
    REPO_ROOT / "docs" / "H-041_IMPLEMENTATION_PROOF.md",
    BACKEND / "src" / "inference_runtime" / "__init__.py",
    BACKEND / "src" / "inference_runtime" / "kv_cache_registry.py",
    BACKEND / "src" / "inference_runtime" / "continuous_batching_service.py",
    BACKEND / "src" / "inference_runtime" / "runtime_token_budget_service.py",
    BACKEND / "src" / "inference_runtime" / "prefill_decode_optimizer.py",
    BACKEND / "src" / "inference_runtime" / "inference_cost_governance_service.py",
    BACKEND / "src" / "inference_runtime" / "speculative_execution_service.py",
    BACKEND / "src" / "inference_runtime" / "runtime_parallelism_service.py",
    BACKEND / "src" / "inference_runtime" / "runtime_telemetry_service.py",
    BACKEND / "src" / "inference_runtime" / "runtime_collapse_detection_service.py",
    BACKEND / "src" / "inference_runtime" / "prefill_pressure_service.py",
    BACKEND / "src" / "inference_runtime" / "runtime_efficiency_service.py",
    BACKEND / "src" / "inference_runtime" / "inference_validation_service.py",
    BACKEND / "src" / "http" / "v1" / "inference_runtime_router.py",
    BACKEND / "src" / "agent_proxy_firewall" / "runtime_anomaly_alignment_service.py",
    BACKEND / "tests" / "test_inference_runtime.py",
    BACKEND / "src" / "ui" / "en" / "inference_runtime_demo.html",
    BACKEND / "src" / "ui" / "tr" / "inference_runtime_demo.html",
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


def inference_router_is_thin(path: Path) -> bool:
    txt = path.read_text(encoding="utf-8")
    if "_envelope(" not in txt or "APIRouter(" not in txt:
        return False
    return "def export_" not in txt


def main() -> int:
    rc = 0
    print("H-041 verification...", flush=True)

    for p in REQUIRED_FILES:
        if p.exists():
            ok(f"exists: {p.relative_to(REPO_ROOT)}")
        else:
            rc |= fail(f"missing {p.relative_to(REPO_ROOT)}")

    scanned = REQUIRED_FILES + [
        BACKEND / "src" / "semantic_capabilities" / "capability_registry.py",
        BACKEND / "src" / "app.py",
        BACKEND / "src" / "skill_runtime" / "skill_registry_service.py",
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
    if "inference_runtime_router" in app_txt and "include_router(inference_runtime_router" in app_txt:
        ok("app.py registers inference_runtime_router")
    else:
        rc |= fail("app.py missing inference_runtime_router")

    rr = BACKEND / "src" / "http" / "v1" / "inference_runtime_router.py"
    if rr.exists():
        rt = rr.read_text(encoding="utf-8")
        if "uncontrolled_runtime_expansion" not in rt:
            rc |= fail("router missing uncontrolled_runtime_expansion envelope")
        else:
            ok("router defines governance envelope")
        if rt.count("autonomous_runtime_scheduling") < 1:
            rc |= fail("router missing autonomous_runtime_scheduling flag")
        if not inference_router_is_thin(rr):
            rc |= fail("inference router must delegate to services (no local export defs)")
        else:
            ok("inference router delegates to services")

    pkg = BACKEND / "src" / "inference_runtime"
    if pkg.is_dir():
        combined = "".join(p.read_text(encoding="utf-8", errors="replace") for p in pkg.glob("*.py"))
        if UNSAFE_MARKERS.search(combined):
            rc |= fail("unsafe execution markers in inference_runtime package")
        else:
            ok("no unsafe execution markers in inference_runtime package")

    tb = BACKEND / "src" / "inference_runtime" / "runtime_token_budget_service.py"
    if tb.exists() and "export_runtime_token_budgets_manifest" in tb.read_text(encoding="utf-8"):
        ok("token budgets present")
    else:
        rc |= fail("runtime_token_budget_service incomplete")

    cb = BACKEND / "src" / "inference_runtime" / "continuous_batching_service.py"
    if cb.exists() and "export_continuous_batching_manifest" in cb.read_text(encoding="utf-8"):
        ok("batching metadata present")
    else:
        rc |= fail("continuous_batching_service incomplete")

    tel = BACKEND / "src" / "inference_runtime" / "runtime_telemetry_service.py"
    if tel.exists() and "export_runtime_telemetry_manifest" in tel.read_text(encoding="utf-8"):
        ok("runtime telemetry present")
    else:
        rc |= fail("runtime_telemetry_service incomplete")

    col = BACKEND / "src" / "inference_runtime" / "runtime_collapse_detection_service.py"
    if col.exists() and "assess_runtime_collapse_risk" in col.read_text(encoding="utf-8"):
        ok("collapse detection present")
    else:
        rc |= fail("runtime_collapse_detection_service incomplete")

    pp = BACKEND / "src" / "inference_runtime" / "prefill_pressure_service.py"
    if pp.exists() and "classify_prefill_pressure" in pp.read_text(encoding="utf-8"):
        ok("prefill pressure present")
    else:
        rc |= fail("prefill_pressure_service incomplete")

    ef = BACKEND / "src" / "inference_runtime" / "runtime_efficiency_service.py"
    if ef.exists() and "compute_runtime_efficiency_score" in ef.read_text(encoding="utf-8"):
        ok("runtime efficiency scoring present")
    else:
        rc |= fail("runtime_efficiency_service incomplete")

    skb = BACKEND / "src" / "skill_runtime" / "skill_registry_service.py"
    if skb.exists() and "estimated_token_cost" in skb.read_text(encoding="utf-8"):
        ok("skill registry integrates H-041 metadata fields")
    else:
        rc |= fail("skill_registry missing H-041 metadata fields")

    fwr = BACKEND / "src" / "http" / "v1" / "agent_proxy_firewall_router.py"
    if fwr.exists() and "runtime_inference_alignment" in fwr.read_text(encoding="utf-8"):
        ok("firewall gateways include runtime inference alignment")
    else:
        rc |= fail("firewall router missing runtime_inference_alignment")

    cap_reg = BACKEND / "src" / "semantic_capabilities" / "capability_registry.py"
    if cap_reg.exists():
        crt = cap_reg.read_text(encoding="utf-8")
        for cid in (
            "inference.kv_cache",
            "inference.batching",
            "inference.token_budgets",
            "inference.parallelism",
            "inference.costs",
            "inference.telemetry",
            "inference.collapse_detection",
            "inference.prefill_pressure",
            "inference.runtime_efficiency",
        ):
            if f'capability_id="{cid}"' not in crt:
                rc |= fail(f"capability_registry missing {cid}")
        ok("H-020 capability_registry includes inference.* entries")

    mb = BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html"
    if mb.exists() and "H-041 Inference Runtime Intelligence" in mb.read_text(encoding="utf-8"):
        ok("MainBook contains H-041 section")
    else:
        rc |= fail("MainBook missing H-041")

    lb = BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html"
    if lb.exists() and "H-041 Verification" in lb.read_text(encoding="utf-8"):
        ok("LiveBook contains H-041 verification")
    else:
        rc |= fail("LiveBook missing H-041 verification")

    bl = REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md"
    if bl.exists() and "***REMOVED******REMOVED*** H-041" in bl.read_text(encoding="utf-8"):
        ok("Master backlog references H-041")
    else:
        rc |= fail("Master backlog missing H-041")

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
                "/api/v1/system/inference/token-budgets",
                "/api/v1/system/inference/batching",
                "/api/v1/system/inference/telemetry",
                "/api/v1/system/inference/collapse-risk",
                "/api/v1/system/inference/efficiency",
            ):
                req = Request(root + path, headers={"User-Agent": "verify-h041/1"})
                with urlopen(req, timeout=15) as resp:
                    if resp.status != 200:
                        rc |= fail(f"live GET {path} status {resp.status}")
                    body = json.loads(resp.read().decode("utf-8"))
                    if body.get("uncontrolled_runtime_expansion") is not False:
                        rc |= fail(f"live envelope invalid for {path}")
            ok("live VERIFY_BASE_URL inference runtime smoke passed")
        except (HTTPError, URLError, json.JSONDecodeError, KeyError, TypeError) as exc:
            rc |= fail(f"live probe failed: {exc}")

    try:
        env = os.environ.copy()
        env.setdefault("JWT_SECRET", "verify-h041-jwt-secret-32characters!!!")
        env.setdefault("SOARB2B_API_KEYS", "verify-h041-key")
        out = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(BACKEND / "tests" / "test_inference_runtime.py"),
                str(BACKEND / "tests" / "test_semantic_capabilities.py"),
                str(BACKEND / "tests" / "test_agent_proxy_firewall.py"),
                "-q",
            ],
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            timeout=240,
            env=env,
        )
        if out.returncode != 0:
            rc |= fail(f"pytest failed:\n{out.stdout}\n{out.stderr}")
        else:
            ok("pytest test_inference_runtime + semantic + firewall passed")
    except Exception as exc:
        rc |= fail(f"pytest launcher: {exc}")

    print("PASS: H-041 verification complete." if rc == 0 else "FAIL: H-041 incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
