"""
MODULE: source_registry
PURPOSE: Approved ingestion sources and explicit rejection of unverified scraping classes (H-024)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Mapping

***REMOVED*** Trust anchors are deterministic; tuned for commercial-intelligence governance (foundation).
APPROVED_SOURCE_METADATA: dict[str, Mapping[str, Any]] = {
    "uploaded_documents": {"registry_trust": 0.55, "tier": "internal_controlled"},
    "public_procurement_feed": {"registry_trust": 0.88, "tier": "official_feed"},
    "approved_public_registry": {"registry_trust": 0.78, "tier": "public_registry"},
    "verified_partner_dataset": {"registry_trust": 0.72, "tier": "partner_verified"},
    ***REMOVED*** H-044 document intelligence source types (metadata only; lineage required)
    "ocr_document": {"registry_trust": 0.6, "tier": "document_intelligence"},
    "bid_pdf": {"registry_trust": 0.66, "tier": "document_intelligence"},
    "scanned_form": {"registry_trust": 0.58, "tier": "document_intelligence"},
    "multilingual_document": {"registry_trust": 0.62, "tier": "document_intelligence"},
}

REJECTED_SOURCE_TYPES: frozenset[str] = frozenset(
    {
        "unverified_anonymous_scraping_source",
    }
)


def is_rejected_source(source_type: str) -> bool:
    return source_type.strip() in REJECTED_SOURCE_TYPES


def is_known_approved_source(source_type: str) -> bool:
    return source_type.strip() in APPROVED_SOURCE_METADATA


def require_approved_source(source_type: str) -> None:
    st = source_type.strip()
    if is_rejected_source(st):
        raise ValueError("rejected source_type: unverified or anonymous scraping class not permitted")
    if not is_known_approved_source(st):
        raise ValueError(f"unknown or unregistered source_type: {source_type}")


def registry_trust_for(source_type: str) -> float:
    require_approved_source(source_type)
    meta = APPROVED_SOURCE_METADATA[source_type.strip()]
    return float(meta["registry_trust"])
