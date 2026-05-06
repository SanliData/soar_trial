"""
SCRIPT: verify_phase3_operational_ai_experience
PURPOSE: Verify Phase 3 live operational AI experience surfaces exist and books updated
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
    pages = [
        "backend/src/ui/en/event_stream_center.html",
        "backend/src/ui/tr/event_stream_center.html",
        "backend/src/ui/en/agent_operations_center.html",
        "backend/src/ui/tr/agent_operations_center.html",
        "backend/src/ui/en/approval_center.html",
        "backend/src/ui/tr/approval_center.html",
    ]
    for rel in pages:
        _assert_exists(rel)
        _assert_utf8_no_bom(rel)

    mainbook = _read("backend/docs/main_book/FinderOS_MainBook_v0.1.html")
    livebook = _read("backend/docs/live_book/FinderOS_LiveBook_2025-12-13.html")
    assert "48C. Productization Phase 3" in mainbook, "MainBook missing 48C section"
    assert "48C. Verification — Live Operational AI Experience" in livebook, "LiveBook missing 48C verification section"

    print("Phase 3 operational AI experience verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

