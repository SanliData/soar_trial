"""
MODULE: document_validation_service
PURPOSE: Validate document extraction objects and reject unsafe metadata (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


_UNSAFE_META_KEYS = frozenset({"authorization", "cookie", "set-cookie", "proxy-authorization"})


def validate_document_extraction(extraction: dict[str, Any]) -> None:
    if not isinstance(extraction, dict):
        raise ValueError("invalid extraction")
    did = extraction.get("document_id")
    if not isinstance(did, str) or not did.strip():
        raise ValueError("missing document_id")

    lineage = extraction.get("source_lineage")
    if not isinstance(lineage, dict) or not lineage:
        raise ValueError("missing lineage")
    if not isinstance(lineage.get("source_type"), str) or not lineage.get("source_type", "").strip():
        raise ValueError("missing lineage.source_type")
    if not isinstance(lineage.get("source_record_id"), str) or not lineage.get("source_record_id", "").strip():
        raise ValueError("missing lineage.source_record_id")

    file_meta = extraction.get("file_metadata") or {}
    if file_meta:
        if not isinstance(file_meta, dict):
            raise ValueError("invalid file_metadata")
        lowered_keys = {str(k).strip().lower() for k in file_meta.keys()}
        if lowered_keys & _UNSAFE_META_KEYS:
            raise ValueError("unsafe file metadata rejected")

    if extraction.get("gpu_required") is True:
        raise ValueError("gpu OCR infrastructure not permitted in foundation")

