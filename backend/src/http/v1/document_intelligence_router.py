"""
ROUTER: document_intelligence_router
PURPOSE: HTTP facade for document intelligence abstractions (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.document_intelligence.document_validation_service import validate_document_extraction
from src.document_intelligence.form_structure_service import export_form_structure_manifest, placeholder_form_fields
from src.document_intelligence.layout_extraction_service import export_layout_extraction_manifest, placeholder_layout
from src.document_intelligence.markdown_projection_service import export_markdown_projection_manifest, project_placeholder_markdown
from src.document_intelligence.ocr_pipeline_service import export_ocr_pipeline_manifest, placeholder_extract

router = APIRouter(tags=["document-intelligence"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "document_intelligence_foundation": True,
        "external_ocr_required_now": False,
        "gpu_ocr_infrastructure": False,
        "hidden_file_ingestion": False,
    }
    merged.update(payload)
    return merged


@router.get("/system/documents/ocr-pipeline")
async def get_ocr_pipeline() -> Dict[str, Any]:
    return _envelope({"ocr_pipeline": export_ocr_pipeline_manifest()})


@router.get("/system/documents/layout")
async def get_document_layout() -> Dict[str, Any]:
    return _envelope({"layout": export_layout_extraction_manifest(), "sample": placeholder_layout(document_id="doc-demo-001")})


@router.get("/system/documents/form-structure")
async def get_document_form_structure() -> Dict[str, Any]:
    return _envelope({"form_structure": export_form_structure_manifest(), "sample": placeholder_form_fields(document_id="doc-demo-001")})


@router.get("/system/documents/markdown-projection")
async def get_document_markdown_projection() -> Dict[str, Any]:
    extraction = placeholder_extract(
        document_id="doc-demo-001",
        document_type="bid_document",
        source_lineage={"source_type": "ocr_document", "source_record_id": "upload-0001"},
    )
    validate_document_extraction(extraction)
    return _envelope({"markdown_projection": export_markdown_projection_manifest(), "sample": project_placeholder_markdown(extraction)})

