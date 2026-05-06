"""
SCRIPT: verify_phase2_intelligence_surfaces
PURPOSE: Verify Phase 2 intelligence product surfaces exist and books updated
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
        "backend/src/ui/en/results_hub_v2.html",
        "backend/src/ui/tr/results_hub_v2.html",
        "backend/src/ui/en/retrieval_intelligence.html",
        "backend/src/ui/tr/retrieval_intelligence.html",
        "backend/src/ui/en/procurement_workflow.html",
        "backend/src/ui/tr/procurement_workflow.html",
        "backend/src/ui/en/intelligence_search.html",
        "backend/src/ui/tr/intelligence_search.html",
        "backend/src/ui/en/relationship_graphs.html",
        "backend/src/ui/tr/relationship_graphs.html",
    ]
    assets = [
        "backend/src/ui/shared/evidence_drawer.html",
        "backend/src/ui/shared/explainability_panel.html",
        "backend/src/ui/shared/retrieval_lineage_panel.html",
        "backend/src/ui/shared/policy_alignment_panel.html",
        "backend/src/ui/shared/approval_reason_panel.html",
        "backend/src/ui/shared/op_surface_helpers.js",
    ]

    for rel in pages + assets:
        _assert_exists(rel)
        _assert_utf8_no_bom(rel)

    mainbook = _read("backend/docs/main_book/FinderOS_MainBook_v0.1.html")
    livebook = _read("backend/docs/live_book/FinderOS_LiveBook_2025-12-13.html")
    assert "48B. Productization Phase 2" in mainbook, "MainBook missing 48B section"
    assert "48B. Verification — Intelligence Product Surfaces" in livebook, "LiveBook missing 48B verification section"

    print("Phase 2 intelligence surfaces verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

