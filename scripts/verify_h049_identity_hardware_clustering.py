***REMOVED***!/usr/bin/env python3
"""
H-049 verification: identity governance + hardware runtime + adaptive clustering.
Exit code 0 only if structural checks pass.
"""

from __future__ import annotations

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
    REPO_ROOT / "docs" / "H-049_AGENTIC_IDENTITY_HARDWARE_CLUSTERING.md",
    REPO_ROOT / "docs" / "H-049_IMPLEMENTATION_PROOF.md",
    BACKEND / "src" / "agentic_identity" / "__init__.py",
    BACKEND / "src" / "agentic_identity" / "agent_identity_registry.py",
    BACKEND / "src" / "agentic_identity" / "cryptographic_identity_service.py",
    BACKEND / "src" / "agentic_identity" / "runtime_access_policy.py",
    BACKEND / "src" / "agentic_identity" / "shadow_agent_detection.py",
    BACKEND / "src" / "agentic_identity" / "mcp_endpoint_governance.py",
    BACKEND / "src" / "agentic_identity" / "identity_audit_service.py",
    BACKEND / "src" / "agentic_identity" / "identity_budget_service.py",
    BACKEND / "src" / "agentic_identity" / "identity_validation_service.py",
    BACKEND / "src" / "hardware_aware_runtime" / "__init__.py",
    BACKEND / "src" / "hardware_aware_runtime" / "hardware_profile_service.py",
    BACKEND / "src" / "hardware_aware_runtime" / "runtime_hardware_router.py",
    BACKEND / "src" / "hardware_aware_runtime" / "inference_acceleration_service.py",
    BACKEND / "src" / "hardware_aware_runtime" / "hardware_cost_service.py",
    BACKEND / "src" / "hardware_aware_runtime" / "latency_profile_service.py",
    BACKEND / "src" / "hardware_aware_runtime" / "hardware_validation_service.py",
    BACKEND / "src" / "adaptive_clustering" / "__init__.py",
    BACKEND / "src" / "adaptive_clustering" / "breathing_cluster_service.py",
    BACKEND / "src" / "adaptive_clustering" / "cluster_utility_service.py",
    BACKEND / "src" / "adaptive_clustering" / "adaptive_centroid_service.py",
    BACKEND / "src" / "adaptive_clustering" / "runtime_cluster_optimizer.py",
    BACKEND / "src" / "adaptive_clustering" / "cluster_variance_service.py",
    BACKEND / "src" / "adaptive_clustering" / "clustering_validation_service.py",
    BACKEND / "src" / "http" / "v1" / "agentic_identity_router.py",
    BACKEND / "src" / "http" / "v1" / "hardware_aware_runtime_router.py",
    BACKEND / "src" / "http" / "v1" / "adaptive_clustering_router.py",
    BACKEND / "src" / "ui" / "en" / "agentic_identity_demo.html",
    BACKEND / "src" / "ui" / "en" / "hardware_runtime_demo.html",
    BACKEND / "src" / "ui" / "en" / "adaptive_clustering_demo.html",
]


def ok(msg: str) -> int:
    print(f"[OK] {msg}")
    return 0


def fail(msg: str) -> int:
    print(f"[FAIL] {msg}")
    return 1


def has_bom(path: Path) -> bool:
    return path.read_bytes().startswith(b"\xef\xbb\xbf")


def scan_secrets(paths: list[Path]) -> list[str]:
    hits = []
    secret_re = re.compile(r"(api[_-]?key|secret|token)\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE)
    for p in paths:
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for m in secret_re.finditer(txt):
            hits.append(f"{p}: secret-like assignment near: {m.group(0)[:64]}")
    return hits


def router_thin(path: Path) -> bool:
    txt = path.read_text(encoding="utf-8")
    forbidden = ["requests.", "httpx.", "datetime.now", "time.time", "openai", "anthropic"]
    return not any(f in txt for f in forbidden)


def main() -> int:
    rc = 0
    for f in REQUIRED_FILES:
        if f.exists():
            rc |= ok(f"exists: {f.relative_to(REPO_ROOT)}")
        else:
            rc |= fail(f"missing: {f.relative_to(REPO_ROOT)}")

    py_files = [p for p in REQUIRED_FILES if p.suffix == ".py" and p.exists()]
    for p in py_files:
        if has_bom(p):
            rc |= fail(f"UTF-8 BOM detected: {p.relative_to(REPO_ROOT)}")

    for h in scan_secrets(py_files):
        rc |= fail(h)

    for r in [
        BACKEND / "src" / "http" / "v1" / "agentic_identity_router.py",
        BACKEND / "src" / "http" / "v1" / "hardware_aware_runtime_router.py",
        BACKEND / "src" / "http" / "v1" / "adaptive_clustering_router.py",
    ]:
        if r.exists() and router_thin(r):
            rc |= ok(f"router thinness ok: {r.name}")
        else:
            rc |= fail(f"router thinness failed: {r.name}")

    ***REMOVED*** Import smoke + key invariants
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(BACKEND)
        chk = subprocess.run(
            [
                sys.executable,
                "-c",
                "from src.agentic_identity.agent_identity_registry import export_identity_registry; "
                "from src.agentic_identity.mcp_endpoint_governance import export_mcp_endpoint_governance; "
                "from src.hardware_aware_runtime.runtime_hardware_router import route_workload; "
                "from src.adaptive_clustering.cluster_utility_service import export_cluster_utility; "
                "ids=export_identity_registry(); assert ids['identities'][0]['hidden_identity_escalation'] is False; "
                "m=export_mcp_endpoint_governance(); assert m['mcp_endpoints'][0]['unrestricted_mcp_endpoint_exposure'] is False; "
                "r=route_workload(workload='retrieval'); assert r['recommendation_only'] is True; "
                "u=export_cluster_utility(); assert u['deterministic'] is True; "
                "print('ok');",
            ],
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
        if chk.returncode != 0:
            rc |= fail(f"import smoke failed:\n{chk.stdout}\n{chk.stderr}")
        else:
            rc |= ok("import smoke passed")
    except Exception as exc:
        rc |= fail(f"import smoke launcher: {exc}")

    base_url = os.environ.get("VERIFY_BASE_URL")
    if base_url:
        root = base_url.rstrip("/")
        for path in (
            "/api/v1/system/identity/registry",
            "/api/v1/system/runtime/hardware-profiles",
            "/api/v1/system/clustering/utility",
        ):
            try:
                req = Request(root + path, headers={"User-Agent": "verify-h049/1"})
                with urlopen(req, timeout=15) as resp:
                    if resp.status != 200:
                        rc |= fail(f"live GET {path} status {resp.status}")
                    else:
                        rc |= ok(f"live GET {path} ok")
            except (HTTPError, URLError) as exc:
                rc |= fail(f"live GET {path} failed: {exc}")

    return int(rc)


if __name__ == "__main__":
    raise SystemExit(main())

