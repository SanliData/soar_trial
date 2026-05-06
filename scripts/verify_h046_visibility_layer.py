***REMOVED***!/usr/bin/env python3
"""
H-046 verification: Unified Operational Admin & System Visibility Layer.
Exit code 0 only if structural checks pass.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND = REPO_ROOT / "backend"

REQUIRED_FILES = [
    REPO_ROOT / "docs" / "H-046_SYSTEM_VISIBILITY_LAYER.md",
    BACKEND / "src" / "system_visibility" / "__init__.py",
    BACKEND / "src" / "system_visibility" / "system_health_service.py",
    BACKEND / "src" / "system_visibility" / "runtime_pressure_service.py",
    BACKEND / "src" / "system_visibility" / "workflow_audit_service.py",
    BACKEND / "src" / "system_visibility" / "retrieval_visibility_service.py",
    BACKEND / "src" / "system_visibility" / "connector_freshness_service.py",
    BACKEND / "src" / "system_visibility" / "orchestration_trace_service.py",
    BACKEND / "src" / "system_visibility" / "approval_queue_service.py",
    BACKEND / "src" / "system_visibility" / "active_agent_visibility_service.py",
    BACKEND / "src" / "system_visibility" / "visibility_validation_service.py",
    BACKEND / "src" / "http" / "v1" / "system_visibility_router.py",
    BACKEND / "src" / "ui" / "en" / "system_visibility_dashboard.html",
    BACKEND / "src" / "ui" / "tr" / "system_visibility_dashboard.html",
]


def ok(msg: str) -> int:
    print(f"[OK] {msg}")
    return 0


def fail(msg: str) -> int:
    print(f"[FAIL] {msg}")
    return 1


def has_bom(path: Path) -> bool:
    raw = path.read_bytes()
    return raw.startswith(b"\xef\xbb\xbf")


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
    if any(f in txt for f in forbidden):
        return False
    return True


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

    router_path = BACKEND / "src" / "http" / "v1" / "system_visibility_router.py"
    if router_path.exists() and router_thin(router_path):
        rc |= ok("router thinness check passed")
    else:
        rc |= fail("router thinness check failed")

    ***REMOVED*** Import smoke
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(BACKEND)
        chk = subprocess.run(
            [
                sys.executable,
                "-c",
                "from src.system_visibility.system_health_service import export_system_health; "
                "from src.system_visibility.runtime_pressure_service import export_runtime_pressure; "
                "print(export_system_health()['health']['level']); "
                "print(export_runtime_pressure()['overall']['level']);",
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

    return int(rc)


if __name__ == "__main__":
    raise SystemExit(main())

