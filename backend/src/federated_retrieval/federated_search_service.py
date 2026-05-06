"""
MODULE: federated_search_service
PURPOSE: Deterministic federated search (mock foundation) with lineage (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import hashlib
from typing import Any

from src.federated_retrieval.connector_registry_service import export_connector_registry, get_connector
from src.federated_retrieval.federated_retrieval_validation_service import validate_retrieval_result
from src.federated_retrieval.source_lineage_service import build_source_lineage


_SAMPLE_INDEX: list[dict[str, Any]] = [
    {
        "record_id": "rec-ud-001",
        "connector_name": "uploaded_documents",
        "title": "Telecom bid requirements summary",
        "snippet": "RFP requires ISO 27001 and net-30 terms…",
        "freshness_days": 14,
        "original_reference": "upload://doc-ud-001",
    },
    {
        "record_id": "rec-pf-001",
        "connector_name": "procurement_feed",
        "title": "City procurement notice",
        "snippet": "Notice includes submission deadline and scope…",
        "freshness_days": 3,
        "original_reference": "feed://notice-001",
    },
    {
        "record_id": "rec-perm-001",
        "connector_name": "permit_repository",
        "title": "Permit status change",
        "snippet": "Inspection scheduled; compliance notes attached…",
        "freshness_days": 7,
        "original_reference": "permit://record-001",
    },
]


def federated_search(*, query: str, mode: str = "hybrid", limit: int = 5) -> dict[str, Any]:
    q = (query or "").strip()
    lim = max(1, min(int(limit), 25))
    lowered = q.lower()

    enabled = {c["connector_name"] for c in export_connector_registry()["connectors"] if c["enabled"]}
    hits = []
    for r in _SAMPLE_INDEX:
        if r["connector_name"] not in enabled:
            continue
        text = (r["title"] + " " + r["snippet"]).lower()
        if not q:
            score = 0.4
        else:
            score = 0.9 if any(tok in text for tok in lowered.split()[:3]) else 0.35
        conn = get_connector(r["connector_name"])
        lineage = build_source_lineage(
            source_name=conn["connector_name"],
            source_type=conn["connector_type"],
            original_reference=r["original_reference"],
            authority_score=float(conn["source_authority"]),
            freshness_days=int(r["freshness_days"]),
        )
        row = {
            "record_id": r["record_id"],
            "connector_name": r["connector_name"],
            "title": r["title"],
            "snippet": r["snippet"],
            "relevance_score": round(float(score), 4),
            "relevance_explain": {
                "mode": mode,
                "query_match": "token_overlap" if q else "empty_query_baseline",
                "deterministic": True,
            },
            "source_lineage": lineage,
        }
        validate_retrieval_result(row)
        hits.append(row)

    hits.sort(key=lambda x: x["relevance_score"], reverse=True)
    hits = hits[:lim]
    digest = hashlib.sha256((q + "|" + mode).encode("utf-8")).hexdigest()[:16]
    return {
        "query": q,
        "mode": mode,
        "results": hits,
        "result_count": len(hits),
        "retrieval_lineage_required": True,
        "deterministic": True,
        "search_digest": digest,
        "no_live_external_api": True,
    }

