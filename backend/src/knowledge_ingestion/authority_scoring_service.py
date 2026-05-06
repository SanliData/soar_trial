"""
MODULE: authority_scoring_service
PURPOSE: Deterministic authority scores from registry trust and freshness (H-024)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from src.knowledge_ingestion import freshness_scoring_service
from src.knowledge_ingestion.knowledge_block_schema import SourceLineage
from src.knowledge_ingestion.source_registry import registry_trust_for, require_approved_source


def compute_authority_score(
    *,
    source_type: str,
    lineage: SourceLineage,
    freshness_days: int,
) -> float:
    """
    Combines registry trust with freshness decay. Official feeds outweigh anonymous classes,
    which are rejected upstream — this function assumes source passed registry gates.
    """
    require_approved_source(source_type)
    base = registry_trust_for(source_type)
    lineage_boost = 1.0
    if lineage.parent_document_id:
        lineage_boost = min(1.05, lineage_boost + 0.03)
    fresh = freshness_scoring_service.freshness_confidence_score(freshness_days)
    raw = base * fresh * lineage_boost
    return round(min(1.0, max(0.0, raw)), 4)
