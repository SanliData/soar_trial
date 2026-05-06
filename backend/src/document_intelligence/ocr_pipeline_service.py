"""
MODULE: ocr_pipeline_service
PURPOSE: OCR pipeline metadata and placeholder extraction results (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def placeholder_extract(*, document_id: str, document_type: str, source_lineage: dict[str, Any]) -> dict[str, Any]:
    """
    Deterministic placeholder extraction result.
    No OCR models, no GPU dependencies.
    """
    did = (document_id or "").strip()
    if not did:
        raise ValueError("invalid document_id")
    dt = (document_type or "").strip()
    if not dt:
        raise ValueError("invalid document_type")
    if not isinstance(source_lineage, dict) or not source_lineage:
        raise ValueError("source_lineage required")
    if not source_lineage.get("source_type") or not source_lineage.get("source_record_id"):
        raise ValueError("source_lineage missing required fields")

    return {
        "document_id": did,
        "document_type": dt,
        "extraction_mode": "placeholder_no_ocr_model",
        "text_blocks": [
            {
                "block_id": "b1",
                "text": "PLACEHOLDER: extracted text not available in foundation build.",
                "confidence": 0.0,
            }
        ],
        "layout_available": True,
        "form_fields_available": True,
        "source_lineage": dict(source_lineage),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "deterministic": True,
    }


def export_ocr_pipeline_manifest() -> dict[str, Any]:
    return {
        "supported_document_concepts": [
            "pdf",
            "scanned_form",
            "bid_document",
            "contractor_form",
            "utility_document",
            "permit",
            "invoice",
            "engineering_drawing",
        ],
        "pipeline": {
            "stages": [
                {"stage_id": "ingest", "description": "metadata + lineage capture"},
                {"stage_id": "layout", "description": "page boxes / tables / paragraphs (placeholder)"},
                {"stage_id": "text", "description": "OCR text blocks (placeholder)"},
                {"stage_id": "forms", "description": "field/value inference (placeholder)"},
                {"stage_id": "projection", "description": "markdown projection"},
                {"stage_id": "validation", "description": "lineage + safe metadata checks"},
            ],
            "external_ocr_required_now": False,
            "gpu_infrastructure_required": False,
            "deterministic_placeholder_extraction": True,
        },
        "deterministic": True,
        "no_external_execution": True,
    }

