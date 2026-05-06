"""
MODULE: markdown_projection_service
PURPOSE: Project extracted document structure into Markdown (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_markdown_projection_manifest() -> dict[str, Any]:
    return {
        "projection": "layout_and_text_to_markdown_v1",
        "features": [
            "headings_from_large_font_blocks_placeholder",
            "tables_to_markdown_placeholder",
            "form_fields_as_bullets_placeholder",
            "lineage_footer",
        ],
        "deterministic": True,
        "placeholder_only": True,
    }


def project_placeholder_markdown(extraction: dict[str, Any]) -> dict[str, Any]:
    did = str(extraction.get("document_id") or "").strip()
    if not did:
        raise ValueError("invalid extraction")
    lineage = extraction.get("source_lineage") or {}
    source_type = str(lineage.get("source_type") or "").strip()
    source_record_id = str(lineage.get("source_record_id") or "").strip()
    if not source_type or not source_record_id:
        raise ValueError("missing lineage")

    md = (
        f"# Document {did}\n\n"
        "## Placeholder Extraction\n\n"
        "- This foundation build does not run OCR models.\n"
        "- Layout and form structures are represented as deterministic placeholders.\n\n"
        "## Lineage\n\n"
        f"- source_type: `{source_type}`\n"
        f"- source_record_id: `{source_record_id}`\n"
    )
    return {"document_id": did, "markdown": md, "deterministic": True, "placeholder_only": True}

