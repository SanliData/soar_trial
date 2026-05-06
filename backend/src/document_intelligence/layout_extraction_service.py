"""
MODULE: layout_extraction_service
PURPOSE: Layout structures (bounding boxes/tables/forms) metadata (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_layout_extraction_manifest() -> dict[str, Any]:
    return {
        "coordinate_system": "pdf_points_top_left_origin",
        "supported_structures": ["paragraph", "table", "form", "image", "signature_block"],
        "bounding_box_schema": {
            "x": "float",
            "y": "float",
            "width": "float",
            "height": "float",
            "page": "int",
        },
        "table_schema": {"rows": "list[list[cell]]", "cell": {"text": "str", "bbox": "BoundingBox"}},
        "deterministic": True,
        "placeholder_only": True,
    }


def placeholder_layout(*, document_id: str) -> dict[str, Any]:
    did = (document_id or "").strip()
    if not did:
        raise ValueError("invalid document_id")
    return {
        "document_id": did,
        "pages": [
            {
                "page": 1,
                "blocks": [
                    {
                        "block_id": "p1",
                        "type": "paragraph",
                        "bbox": {"x": 72.0, "y": 72.0, "width": 468.0, "height": 120.0, "page": 1},
                    }
                ],
            }
        ],
        "deterministic": True,
        "placeholder_only": True,
    }

