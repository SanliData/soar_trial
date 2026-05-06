"""
MODULE: knowledge_ingestion_service
PURPOSE: Orchestrate validation, scoring, and persistence (H-024)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from src.knowledge_ingestion import authority_scoring_service, ingestion_validation_service
from src.knowledge_ingestion.knowledge_block_schema import CreateKnowledgeBlockRequest, KnowledgeBlock
from src.knowledge_ingestion.knowledge_repository import all_blocks, append_block
from src.knowledge_ingestion.retrieval_policy_service import describe_policies, rank_blocks


def _default_commercial_relevance(block_type: str) -> float:
    weights: dict[str, float] = {
        "opportunity_signal": 0.82,
        "procurement_notice": 0.9,
        "market_signal": 0.78,
        "executive_summary": 0.74,
        "graph_relationship": 0.7,
        "exposure_pattern": 0.76,
        "onboarding_guidance": 0.65,
    }
    return weights.get(block_type, 0.6)


def ingest_block(body: CreateKnowledgeBlockRequest) -> KnowledgeBlock:
    ingestion_validation_service.validate_create_request(body)
    lineage = body.source_lineage
    authority = authority_scoring_service.compute_authority_score(
        source_type=lineage.source_type,
        lineage=lineage,
        freshness_days=body.freshness_days,
    )
    commercial = body.commercial_relevance if body.commercial_relevance is not None else _default_commercial_relevance(
        body.block_type
    )
    block = KnowledgeBlock(
        block_id=str(uuid.uuid4()),
        block_type=body.block_type,
        title=body.title,
        content=body.content,
        authority_score=authority,
        freshness_days=body.freshness_days,
        geographic_scope=body.geographic_scope,
        industry=body.industry,
        commercial_relevance=commercial,
        source_lineage=lineage,
        created_at=datetime.now(timezone.utc),
        tags=list(body.tags),
    )
    append_block(block)
    return block


def list_blocks_response(
    *,
    limit: int = 50,
    geographic_scope: Optional[str] = None,
    industry: Optional[str] = None,
) -> dict[str, Any]:
    blocks = all_blocks()
    ranked, explanations = rank_blocks(blocks, query_geo=geographic_scope, query_industry=industry)
    if limit < len(ranked):
        ranked = ranked[:limit]
        explanations = explanations[:limit]
    return {
        "blocks": [b.model_dump(mode="json") for b in ranked],
        "ranking": explanations,
    }


def policies_response() -> dict[str, Any]:
    return describe_policies()
