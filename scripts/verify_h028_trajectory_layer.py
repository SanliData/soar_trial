***REMOVED***!/usr/bin/env python3
"""
H-028 verification: relative trajectory evaluation foundation.
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
    REPO_ROOT / "docs" / "H-028_TRAJECTORY_EVALUATION_LAYER.md",
    REPO_ROOT / "docs" / "H-028_IMPLEMENTATION_PROOF.md",
    BACKEND / "src" / "trajectory_evaluation" / "__init__.py",
    BACKEND / "src" / "trajectory_evaluation" / "trajectory_schema.py",
    BACKEND / "src" / "trajectory_evaluation" / "trajectory_group_service.py",
    BACKEND / "src" / "trajectory_evaluation" / "relative_scoring_service.py",
    BACKEND / "src" / "trajectory_evaluation" / "trajectory_registry.py",
    BACKEND / "src" / "trajectory_evaluation" / "comparison_reasoning_service.py",
    BACKEND / "src" / "trajectory_evaluation" / "evaluation_trace_service.py",
    BACKEND / "src" / "trajectory_evaluation" / "trajectory_validation_service.py",
    BACKEND / "src" / "http" / "v1" / "trajectory_evaluation_router.py",
    BACKEND / "tests" / "test_trajectory_evaluation.py",
    BACKEND / "src" / "ui" / "en" / "trajectory_evaluation_demo.html",
    BACKEND / "src" / "ui" / "tr" / "trajectory_evaluation_demo.html",
]

SECRET_PATTERNS = [
    (re.compile(r"(?i)sk_live_[0-9a-zA-Z]{16,}"), "Stripe-like"),
]

***REMOVED*** Block accidental RL training stack markers inside the evaluation package (foundation guardrail).
RL_INFRA_FORBIDDEN = re.compile(
    r"(?i)(torch\.distributed|ray\.train|deepspeed|accelerate\.Accelerator|ppo\s+trainer|proximal\s+policy\s+optimization)"
)


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
    if "execute_relative_evaluation" not in txt:
        return False
    if "rank_trajectories(" in txt or "total_score(" in txt:
        return False
    return True


def main() -> int:
    rc = 0
    print("H-028 verification...", flush=True)

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
    if "trajectory_evaluation_router" in app_txt and "include_router(trajectory_evaluation_router" in app_txt:
        ok("app.py registers trajectory_evaluation_router")
    else:
        rc |= fail("app.py missing trajectory_evaluation_router")

    kr = BACKEND / "src" / "http" / "v1" / "trajectory_evaluation_router.py"
    if kr.exists():
        rt = kr.read_text(encoding="utf-8")
        if "deterministic_trajectory_evaluation" not in rt:
            rc |= fail("router missing deterministic_trajectory_evaluation envelope")
        else:
            ok("router defines governance envelope")
        if "hidden_reasoning_exposure" not in rt:
            rc |= fail("router missing hidden_reasoning_exposure declaration")
        if not router_is_thin(kr):
            rc |= fail("router must delegate scoring to services")
        else:
            ok("trajectory router delegates to services")

    pkg = BACKEND / "src" / "trajectory_evaluation"
    if pkg.is_dir():
        combined = "".join(p.read_text(encoding="utf-8", errors="replace") for p in pkg.glob("*.py"))
        if RL_INFRA_FORBIDDEN.search(combined):
            rc |= fail("RL training infrastructure markers found in trajectory_evaluation package")
        else:
            ok("no RL infrastructure markers in trajectory_evaluation package")

    reg = BACKEND / "src" / "semantic_capabilities" / "capability_registry.py"
    if reg.exists():
        rtxt = reg.read_text(encoding="utf-8")
        for cid in ("trajectory.create", "trajectory.group", "trajectory.evaluate", "trajectory.list_groups"):
            if cid not in rtxt:
                rc |= fail(f"capability_registry missing {cid}")
        ok("semantic registry lists trajectory capabilities")

    mb = BACKEND / "docs" / "main_book" / "FinderOS_MainBook_v0.1.html"
    if mb.exists() and "H-028 Relative Trajectory Evaluation" in mb.read_text(encoding="utf-8"):
        ok("MainBook contains H-028 section")
    else:
        rc |= fail("MainBook missing H-028")

    lb = BACKEND / "docs" / "live_book" / "FinderOS_LiveBook_2025-12-13.html"
    if lb.exists() and "H-028 Verification" in lb.read_text(encoding="utf-8"):
        ok("LiveBook contains H-028 verification")
    else:
        rc |= fail("LiveBook missing H-028 verification")

    bl = REPO_ROOT / "docs" / "SOARB2B_MASTER_BACKLOG.md"
    if bl.exists() and "H-028" in bl.read_text(encoding="utf-8"):
        ok("Master backlog references H-028")
    else:
        rc |= fail("Master backlog missing H-028")

    for h in scan_secrets([p for p in scanned if p.exists() and p.suffix == ".py"]):
        rc |= fail(f"secret heuristic: {h}")

    base_url = os.environ.get("VERIFY_BASE_URL")
    if base_url:
        root = base_url.rstrip("/")
        try:
            p1 = json.dumps(
                {
                    "workflow_name": "verify_wf",
                    "strategy_name": "direct_prompting",
                    "input_summary": "in",
                    "output_summary": "out",
                    "reasoning_metadata": {"commercial_usefulness": 0.8},
                    "tags": [],
                }
            ).encode("utf-8")
            r1 = Request(
                root + "/api/v1/system/trajectory",
                data=p1,
                headers={"Content-Type": "application/json", "User-Agent": "verify-h028/1"},
                method="POST",
            )
            with urlopen(r1, timeout=15) as resp:
                if resp.status != 200:
                    rc |= fail(f"live POST trajectory status {resp.status}")
            ok("live VERIFY_BASE_URL POST trajectory passed")
        except (HTTPError, URLError, json.JSONDecodeError, KeyError, TypeError) as exc:
            rc |= fail(f"live probe failed: {exc}")

    try:
        env = os.environ.copy()
        env.setdefault("JWT_SECRET", "verify-h028-jwt-secret-32characters!!!")
        env.setdefault("SOARB2B_API_KEYS", "verify-h028-key")
        out = subprocess.run(
            [sys.executable, "-m", "pytest", str(BACKEND / "tests" / "test_trajectory_evaluation.py"), "-q"],
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        if out.returncode != 0:
            rc |= fail(f"pytest failed:\n{out.stdout}\n{out.stderr}")
        else:
            ok("pytest tests/test_trajectory_evaluation.py passed")
    except Exception as exc:
        rc |= fail(f"pytest launcher: {exc}")

    print("PASS: H-028 verification complete." if rc == 0 else "FAIL: H-028 incomplete.", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
