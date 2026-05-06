"""
MODULE: multilingual_document_service
PURPOSE: Language metadata and multilingual flags for documents (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_multilingual_document_manifest() -> dict[str, Any]:
    return {
        "language_detection": "metadata_only_no_auto_detect",
        "supported_languages": ["en", "tr", "unknown"],
        "multilingual_flags": [
            "bid_document_bilingual",
            "contractor_form_bilingual",
            "invoice_mixed_language",
        ],
        "deterministic": True,
    }


def normalize_language_tag(lang: str | None) -> str:
    l = (lang or "unknown").strip().lower()
    if l in {"en", "tr"}:
        return l
    return "unknown"

