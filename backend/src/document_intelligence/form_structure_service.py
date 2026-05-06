"""
MODULE: form_structure_service
PURPOSE: Form field structures (field/value pairs, checkboxes, signatures) (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_form_structure_manifest() -> dict[str, Any]:
    return {
        "supported_field_types": ["text", "date", "checkbox", "signature", "numeric", "currency"],
        "field_schema": {
            "field_id": "str",
            "label": "str",
            "value": "str|bool|None",
            "confidence": "float(0..1)",
            "bbox": "BoundingBox",
        },
        "deterministic": True,
        "placeholder_only": True,
    }


def placeholder_form_fields(*, document_id: str) -> dict[str, Any]:
    did = (document_id or "").strip()
    if not did:
        raise ValueError("invalid document_id")
    return {
        "document_id": did,
        "fields": [
            {"field_id": "company_name", "label": "Company Name", "value": None, "confidence": 0.0},
            {"field_id": "signed", "label": "Signature", "value": False, "confidence": 0.0},
            {"field_id": "date", "label": "Date", "value": None, "confidence": 0.0},
        ],
        "deterministic": True,
        "placeholder_only": True,
    }

