***REMOVED***!/usr/bin/env python3
"""
H-035 verification: specification-driven governance foundation.
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
    REPO_ROOT / "docs" / "H-035_SPEC_VERIFICATION_GOVERNANCE.md",
    REPO_ROOT / "docs" / "H-035_IMPLEMENTATION_PROOF.md",
    BACKEND / "src" / "spec_verification_governance" / "__init__.py",
    BACKEND / "src" / "spec_verification_governance" / "specification_registry.py",
    BACKEND / "src" / "spec_verification_governance" / "acceptance_criteria_service.py",
    BACKEND / "src" / "spec_verification_governance" / "verification_trace_service.py",
    BACKEND / "src" / "spec_verification_governance" / "trace_to_eval_service.py",
    BACKEND / "src" / "spec_verification_governance" / "validation_agent_service.py",
    BACKEND / "src" / "spec_verification_governance" / "architecture_contract_service.py",
    BACKEND / "src" / "spec_verification_governance" / "review_governance_service.py",
    BACKEND / "src" / "spec_verification_governance" / "spec_validation_service.py",
    BACKEND / "src" / "http" / "v1" / "spec_verification_governance_router.py",
    BACKEND / "tests" / "test_spec_verification_governance.py",
    BACKEND / "src" / "ui" / "en" / "spec_verification_demo.html",
    BACKEND / "src" / "ui" / "tr" / "spec_verification_demo.html",
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


def spec_router_is_thin(path: Path) -> bool:
    txt = path.read_text(encoding="utf-8")
    if "export_specifications_manifest" not in txt:
        return False
    if "def validate_acceptance(" in txt:
        return False
    if "def map_trace_to_eval(" in txt:
        return False
    if "def export_verification_traces(" in txt:
        return False
    return True


def main() -> int:
    rc = 0
    print("H-035 verification...", flush=True)

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
    if "spec_verification_governance_router" in app_txt and "include_router(spec_verification_governance_router" in app_txt:
        ok("app.py registers spec_verification_governance_router")
    else:
        rc |= fail("app.py missing spec_verification_governance_router")

    sr = BACKEND / "src" / "http" / "v1" / "spec_verification_governance_router.py"
    if sr.exists():
        rt = sr.read_text(encoding="utf-8")
        if "spec_verification_foundation" not in rt:
            rc |= fail("router missing spec_verification_foundation envelope")
        else:
            ok("router defines governance envelope")
        if rt.count("recursive_self_modifying_governance") < 1:
            rc |= fail("router missing recursive_self_modifying_governance declaration")
        if not spec_router_is_thin(sr):
            rc |= fail("spec governance router must delegate to services")
        else:
            ok("spec governance router delegates to services")

    pkg = BACKEND / "src" / "spec_verification_governance"
    if pkg.is_dir():
        combined = "".join(p.read_text(encoding="utf-8", errors="replace") for p in pkg.glob("*.py"))
        if UNSAFE_MARKERS.search(combined):
            rc |= fail("unsafe execution markers in spec_verification_governance package")
        else:
            ok("no unsafe execution markers in spec_verification_governance package")

    reg = BACKEND / "src" / "spec_verification_governance" / "specification_registry.py"
    if reg.exists() and "SPECIFICATIONS" in reg.read_text(encoding="utf-8") and "procurement_analysis" in reg.read_text(encoding="utf-8"):
        ok("specification registry defines static specifications")
    else:
        rc |= fail("specification_registry incomplete")

    ac = BACKEND / "src" / "spec_verification_governance" / "architecture_contract_service.py"
    if ac.exists() and "ARCHITECTURE_CONTRACTS" in ac.read_text(encoding="utf-8"):
        ok("architecture contracts module present")
    else:
        rc |= fail("architecture_contract_service missing ARCHITECTURE_CONTRACTS")

    vt = BACKEND / "src" / "spec_verification_governance" / "verification_trace_service.py"
    if vt.exists() and "export_verification_traces" in vt.read_text(encoding="utf-8"):
        ok("verification trace export present")
    else:
        rc |= fail("verification_trace_service missing export")

    te = BACKEND / "src" / "spec_verification_governance" / "trace_to_eval_service.py"
    if te.exists() and "autonomous_rule_mutation" in te.read_text(encoding="utf-8"):
        ok("trace-to-eval declares autonomous_rule_mutation=false path")
    else:
        rc |= fail("trace_to_eval_service missing autonomous_rule_mutation guard")

    cap_reg = BACKEND / "src" / "semantic_capabilities" / "capability_registry.py"
    if cap_reg.exists():
        crt = cap_reg.read_text(encoding="utf-8")
        for cid in ("specs.registry", "specs.validation", "specs.traces", "specs.trace_to_eval", "specs.review_status"):
            if f'capability_id="{cid}"' not in crt:
                rc |= fail(f"capability_registry missing {cid}")
        ok("H-020 capability_registry includes specs.* entries")

    mb = BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html"
    if mb.exists() and "H-035 Spec-Driven Engineering" in mb.read_text(encoding="utf-8"):
        ok("MainBook contains H-035 section")
    else:
        rc |= fail("MainBook missing H-035")

    lb = BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html"
    if lb.exists() and "H-035 Verification" in lb.read_text(encoding="utf-8"):
        ok("LiveBook contains H-035 verification")
    else:
        rc |= fail("LiveBook missing H-035 verification")

    bl = REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md"
    if bl.exists() and "***REMOVED******REMOVED*** H-035" in bl.read_text(encoding="utf-8"):
        ok("Master backlog references H-035")
    else:
        rc |= fail("Master backlog missing H-035")

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
                "/api/v1/system/specs",
                "/api/v1/system/specs/traces",
                "/api/v1/system/specs/review-status",
            ):
                req = Request(root + path, headers={"User-Agent": "verify-h035/1"})
                with urlopen(req, timeout=15) as resp:
                    if resp.status != 200:
                        rc |= fail(f"live GET {path} status {resp.status}")
                    body = json.loads(resp.read().decode("utf-8"))
                    if body.get("autonomous_architecture_mutation") is not False:
                        rc |= fail(f"live envelope invalid for {path}")
            post_body = json.dumps(
                {"trace_category": "workflow_failure", "trace_code": "acceptance"}
            ).encode("utf-8")
            post_req = Request(
                root + "/api/v1/system/specs/trace-to-eval",
                data=post_body,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "verify-h035/1",
                },
                method="POST",
            )
            with urlopen(post_req, timeout=15) as resp:
                if resp.status != 200:
                    rc |= fail(f"live POST trace-to-eval status {resp.status}")
                te_body = json.loads(resp.read().decode("utf-8"))
                if te_body.get("trace_to_eval", {}).get("autonomous_rule_mutation") is not False:
                    rc |= fail("live trace-to-eval missing autonomous_rule_mutation=false")
            ok("live VERIFY_BASE_URL spec governance smoke passed")
        except (HTTPError, URLError, json.JSONDecodeError, KeyError, TypeError) as exc:
            rc |= fail(f"live probe failed: {exc}")

    try:
        env = os.environ.copy()
        env.setdefault("JWT_SECRET", "verify-h035-jwt-secret-32characters!!!")
        env.setdefault("SOARB2B_API_KEYS", "verify-h035-key")
        out = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(BACKEND / "tests" / "test_spec_verification_governance.py"),
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
            ok("pytest test_spec_verification_governance + test_semantic_capabilities passed")
    except Exception as exc:
        rc |= fail(f"pytest launcher: {exc}")

    print("PASS: H-035 verification complete." if rc == 0 else "FAIL: H-035 incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
