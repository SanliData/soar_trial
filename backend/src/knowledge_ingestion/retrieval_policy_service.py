"""
MODULE: retrieval_policy_service
PURPOSE: Explainable deterministic retrieval ranking rules (H-024)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from src.knowledge_ingestion.freshness_scoring_service import freshness_confidence_score
from src.knowledge_ingestion.knowledge_block_schema import KnowledgeBlock

WEIGHT_AUTHORITY = 0.42
WEIGHT_FRESHNESS = 0.28
WEIGHT_COMMERCIAL = 0.20
WEIGHT_GEO_INDUSTRY = 0.10


def _geo_industry_match_score(block: KnowledgeBlock, query_geo: str | None, query_industry: str | None) -> float:
    score = 0.0
    if query_geo and block.geographic_scope:
        if query_geo.strip().lower() in block.geographic_scope.lower():
            score += 0.5
    if query_industry and block.industry:
        if query_industry.strip().lower() in block.industry.lower():
            score += 0.5
    if query_geo is None and query_industry is None:
        return 0.35
    return min(1.0, score)


def retrieval_score(
    block: KnowledgeBlock,
    *,
    query_geo: str | None = None,
    query_industry: str | None = None,
) -> tuple[float, dict[str, float]]:
    fresh_conf = freshness_confidence_score(block.freshness_days)
    geo_ind = _geo_industry_match_score(block, query_geo, query_industry)
    total = (
        WEIGHT_AUTHORITY * block.authority_score
        + WEIGHT_FRESHNESS * fresh_conf
        + WEIGHT_COMMERCIAL * block.commercial_relevance
        + WEIGHT_GEO_INDUSTRY * geo_ind
    )
    explain = {
        "authority_component": round(WEIGHT_AUTHORITY * block.authority_score, 4),
        "freshness_component": round(WEIGHT_FRESHNESS * fresh_conf, 4),
        "commercial_component": round(WEIGHT_COMMERCIAL * block.commercial_relevance, 4),
        "geo_industry_component": round(WEIGHT_GEO_INDUSTRY * geo_ind, 4),
    }
    return round(min(1.0, max(0.0, total)), 4), explain


def rank_blocks(
    blocks: list[KnowledgeBlock],
    *,
    query_geo: str | None = None,
    query_industry: str | None = None,
) -> tuple[list[KnowledgeBlock], list[dict[str, object]]]:
    ranked: list[tuple[float, KnowledgeBlock, dict[str, object]]] = []
    for b in blocks:
        score, explain = retrieval_score(b, query_geo=query_geo, query_industry=query_industry)
        ranked.append(
            (
                score,
                b,
                {
                    "block_id": b.block_id,
                    "retrieval_score": score,
                    "factors": explain,
                    "weights": {
                        "authority": WEIGHT_AUTHORITY,
                        "freshness": WEIGHT_FRESHNESS,
                        "commercial": WEIGHT_COMMERCIAL,
                        "geo_industry": WEIGHT_GEO_INDUSTRY,
                    },
                },
            )
        )
    ranked.sort(key=lambda x: x[0], reverse=True)
    return [x[1] for x in ranked], [x[2] for x in ranked]


def describe_policies() -> dict[str, object]:
    """Public contract for clients — no execution, ranking weights only."""
    return {
        "ranking_model": "weighted_linear_deterministic",
        "weights": {
            "authority_score": WEIGHT_AUTHORITY,
            "freshness_confidence": WEIGHT_FRESHNESS,
            "commercial_relevance": WEIGHT_COMMERCIAL,
            "geographic_industry_alignment": WEIGHT_GEO_INDUSTRY,
        },
        "notes": [
            "Ranking is explainable via per-block factor breakdowns on list endpoints.",
            "No autonomous retrieval agents or scraping execution in this foundation.",
        ],
    }
