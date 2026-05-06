***REMOVED***!/usr/bin/env python3
"""
H-047 verification: Commercial Intelligence Results Hub.
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
    REPO_ROOT / "docs" / "H-047_COMMERCIAL_INTELLIGENCE_RESULTS_HUB.md",
    BACKEND / "src" / "results_hub" / "__init__.py",
    BACKEND / "src" / "results_hub" / "opportunity_card_service.py",
    BACKEND / "src" / "results_hub" / "contractor_profile_service.py",
    BACKEND / "src" / "results_hub" / "risk_analysis_service.py",
    BACKEND / "src" / "results_hub" / "executive_summary_service.py",
    BACKEND / "src" / "results_hub" / "evidence_trace_service.py",
    BACKEND / "src" / "results_hub" / "workflow_recommendation_service.py",
    BACKEND / "src" / "results_hub" / "relationship_snapshot_service.py",
    BACKEND / "src" / "results_hub" / "explainability_panel_service.py",
    BACKEND / "src" / "results_hub" / "results_hub_validation_service.py",
    BACKEND / "src" / "http" / "v1" / "results_hub_router.py",
    BACKEND / "src" / "ui" / "en" / "results_hub.html",
    BACKEND / "src" / "ui" / "tr" / "results_hub.html",
    BACKEND / "src" / "ui" / "en" / "system_admin_index.html",
    BACKEND / "src" / "ui" / "tr" / "system_admin_index.html",
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

    router_path = BACKEND / "src" / "http" / "v1" / "results_hub_router.py"
    if router_path.exists() and router_thin(router_path):
        rc |= ok("router thinness check passed")
    else:
        rc |= fail("router thinness check failed")

    ***REMOVED*** Import smoke + lineage enforcement
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(BACKEND)
        chk = subprocess.run(
            [
                sys.executable,
                "-c",
                "from src.results_hub.opportunity_card_service import export_opportunities; "
                "from src.results_hub.explainability_panel_service import export_explainability_panels; "
                "o=export_opportunities(); "
                "assert o['opportunities'][0]['retrieval_sources'][0]['source_name']; "
                "x=export_explainability_panels(); "
                "assert x['explainability'][0]['scoring_explanation']['hidden_ranking_logic'] is False; "
                "print('ok');",
            ],
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
        if chk.returncode != 0:
            rc |= fail(f"import/lineage smoke failed:\n{chk.stdout}\n{chk.stderr}")
        else:
            rc |= ok("import/lineage smoke passed")
    except Exception as exc:
        rc |= fail(f"import smoke launcher: {exc}")

    return int(rc)


if __name__ == "__main__":
    raise SystemExit(main())

