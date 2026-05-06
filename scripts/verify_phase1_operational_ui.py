"""
SCRIPT: verify_phase1_operational_ui
PURPOSE: Verify Phase 1 operational UI foundation assets + docs
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _assert_exists(rel: str) -> None:
    p = ROOT / rel
    assert p.exists(), f"missing: {rel}"


def _assert_utf8_no_bom(rel: str) -> None:
    raw = (ROOT / rel).read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf"), f"UTF-8 BOM detected: {rel}"


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def main() -> int:
    css = [
        "backend/src/ui/shared/operational_tokens.css",
        "backend/src/ui/shared/operational_theme.css",
        "backend/src/ui/shared/operational_typography.css",
        "backend/src/ui/shared/operational_layout.css",
        "backend/src/ui/shared/operational_components.css",
        "backend/src/ui/shared/operational_tables.css",
        "backend/src/ui/shared/operational_panels.css",
        "backend/src/ui/shared/operational_timeline.css",
        "backend/src/ui/shared/operational_states.css",
    ]
    pages = [
        "backend/src/ui/en/app_shell.html",
        "backend/src/ui/tr/app_shell.html",
        "backend/src/ui/en/operational_cockpit.html",
        "backend/src/ui/tr/operational_cockpit.html",
    ]
    docs = [
        "docs/SOARB2B_OPERATIONAL_UI_GUIDELINES.md",
        "backend/src/ui/shared/ui_validation_rules.md",
    ]

    for rel in css + pages + docs:
        _assert_exists(rel)
        _assert_utf8_no_bom(rel)

    mainbook = _read("backend/docs/main_book/FinderOS_MainBook_v0.1.html")
    livebook = _read("backend/docs/live_book/FinderOS_LiveBook_2025-12-13.html")
    assert "48A. Productization Phase 1" in mainbook, "MainBook missing 48A section"
    assert "48A. Verification — Operational UI Foundation" in livebook, "LiveBook missing 48A verification section"

    ***REMOVED*** Ensure Phase 1 pages are not chatbot-centric.
    shell = _read("backend/src/ui/en/app_shell.html").lower()
    cockpit = _read("backend/src/ui/en/operational_cockpit.html").lower()
    ***REMOVED*** Phase 1 should not be chat-centric; allow the word "streaming" only in "no streaming" contexts.
    banned = ["chatbot", "autonomous", "agentic chat"]
    assert not any(b in shell for b in banned), "shell contains banned Phase 1 term"
    assert not any(b in cockpit for b in banned), "cockpit contains banned Phase 1 term"

    print("Phase 1 operational UI verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

