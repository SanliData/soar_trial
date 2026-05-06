***REMOVED***!/usr/bin/env python3
"""
H-048 verification: conversational eval + generative operational UI + AG-UI runtime + HITL runtime.
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
    REPO_ROOT / "docs" / "H-048_CONVERSATIONAL_EVAL_AGUI_RUNTIME.md",
    REPO_ROOT / "docs" / "H-048_IMPLEMENTATION_PROOF.md",
    BACKEND / "src" / "conversational_evaluation" / "__init__.py",
    BACKEND / "src" / "conversational_evaluation" / "conversation_eval_service.py",
    BACKEND / "src" / "conversational_evaluation" / "multi_turn_trace_service.py",
    BACKEND / "src" / "conversational_evaluation" / "policy_alignment_service.py",
    BACKEND / "src" / "conversational_evaluation" / "conversation_score_service.py",
    BACKEND / "src" / "conversational_evaluation" / "turn_level_analysis_service.py",
    BACKEND / "src" / "conversational_evaluation" / "evaluation_session_registry.py",
    BACKEND / "src" / "conversational_evaluation" / "conversational_eval_validation.py",
    BACKEND / "src" / "generative_operational_ui" / "__init__.py",
    BACKEND / "src" / "generative_operational_ui" / "ui_component_registry.py",
    BACKEND / "src" / "generative_operational_ui" / "safe_component_projection.py",
    BACKEND / "src" / "generative_operational_ui" / "dashboard_generation_service.py",
    BACKEND / "src" / "generative_operational_ui" / "chart_generation_service.py",
    BACKEND / "src" / "generative_operational_ui" / "graph_visualization_service.py",
    BACKEND / "src" / "generative_operational_ui" / "ui_policy_validation.py",
    BACKEND / "src" / "agui_runtime" / "__init__.py",
    BACKEND / "src" / "agui_runtime" / "event_stream_service.py",
    BACKEND / "src" / "agui_runtime" / "workflow_event_bus.py",
    BACKEND / "src" / "agui_runtime" / "tool_call_stream_service.py",
    BACKEND / "src" / "agui_runtime" / "human_approval_stream.py",
    BACKEND / "src" / "agui_runtime" / "stream_validation_service.py",
    BACKEND / "src" / "hitl_runtime" / "__init__.py",
    BACKEND / "src" / "hitl_runtime" / "approval_checkpoint_service.py",
    BACKEND / "src" / "hitl_runtime" / "human_review_queue.py",
    BACKEND / "src" / "hitl_runtime" / "approval_event_service.py",
    BACKEND / "src" / "hitl_runtime" / "escalation_policy_service.py",
    BACKEND / "src" / "hitl_runtime" / "approval_validation_service.py",
    BACKEND / "src" / "http" / "v1" / "conversational_evaluation_router.py",
    BACKEND / "src" / "http" / "v1" / "generative_operational_ui_router.py",
    BACKEND / "src" / "http" / "v1" / "agui_runtime_router.py",
    BACKEND / "src" / "http" / "v1" / "hitl_runtime_router.py",
    BACKEND / "src" / "ui" / "en" / "conversational_eval_demo.html",
    BACKEND / "src" / "ui" / "en" / "generative_operational_ui_demo.html",
    BACKEND / "src" / "ui" / "en" / "agui_runtime_demo.html",
    BACKEND / "src" / "ui" / "en" / "hitl_runtime_demo.html",
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
        BACKEND / "src" / "http" / "v1" / "conversational_evaluation_router.py",
        BACKEND / "src" / "http" / "v1" / "generative_operational_ui_router.py",
        BACKEND / "src" / "http" / "v1" / "agui_runtime_router.py",
        BACKEND / "src" / "http" / "v1" / "hitl_runtime_router.py",
    ]:
        if r.exists() and router_thin(r):
            rc |= ok(f"router thinness ok: {r.name}")
        else:
            rc |= fail(f"router thinness failed: {r.name}")

    ***REMOVED*** Import smoke
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(BACKEND)
        chk = subprocess.run(
            [
                sys.executable,
                "-c",
                "from src.conversational_evaluation.turn_level_analysis_service import export_turn_level_analysis; "
                "from src.generative_operational_ui.dashboard_generation_service import export_dashboards; "
                "from src.agui_runtime.event_stream_service import export_event_stream; "
                "from src.hitl_runtime.approval_checkpoint_service import export_checkpoints; "
                "assert export_turn_level_analysis()['deterministic'] is True; "
                "assert export_dashboards()['deterministic'] is True; "
                "assert export_event_stream()['auditable'] is True; "
                "assert export_checkpoints()['no_hidden_approval_skipping'] is True; "
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

    ***REMOVED*** Optional live probes
    base_url = os.environ.get("VERIFY_BASE_URL")
    if base_url:
        root = base_url.rstrip("/")
        for path in (
            "/api/v1/system/conversation-eval/sessions",
            "/api/v1/system/agui/events",
            "/api/v1/system/hitl/review-queue",
            "/api/v1/system/generative-ui/components",
        ):
            try:
                req = Request(root + path, headers={"User-Agent": "verify-h048/1"})
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

