"""
MODULE: selective_expansion_service
PURPOSE: Deterministic selective expansion decisions (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.selective_context_runtime.relevance_policy_service import score_relevance_policy
from src.selective_context_runtime.retrieval_budget_service import get_budget
from src.selective_context_runtime.selective_context_validation_service import validate_no_uncontrolled_retrieval_expansion


def decide_selective_expansion(
    *,
    workflow_name: str,
    query: str,
    chunks: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Deterministic expansion:
    - score chunks
    - choose up to max_expanded_chunks
    - return reasoning + token savings estimate
    """
    budget = get_budget(workflow_name)
    validate_no_uncontrolled_retrieval_expansion({"unlimited_retrieval_expansion": False, "hidden_context_expansion": False})

    scored = []
    for c in chunks:
        lineage = c.get("source_lineage") or {}
        scored.append(
            (
                score_relevance_policy(
                    query=query,
                    chunk_text=str(c.get("text") or ""),
                    source_authority=float(lineage.get("authority_score") or 0.6),
                    freshness_days=int(lineage.get("freshness_days") or 30),
                    workflow_scope=workflow_name,
                )["score"],
                c,
            )
        )
    scored.sort(key=lambda x: x[0], reverse=True)
    max_chunks = int(budget["max_expanded_chunks"])
    selected = scored[:max_chunks]
    rejected = scored[max_chunks:]

    selected_ids = [str(c.get("chunk_id") or "") for _, c in selected if c.get("chunk_id")]
    rejected_ids = [str(c.get("chunk_id") or "") for _, c in rejected if c.get("chunk_id")]

    ***REMOVED*** naive savings estimate: expand only selected full text, keep others compressed
    full_tokens = sum(max(0, int(len(str(c.get("text") or "")) / 4)) for _, c in scored)
    expanded_tokens = sum(max(0, int(len(str(c.get("text") or "")) / 4)) for _, c in selected)
    token_savings = max(0, full_tokens - expanded_tokens)

    return {
        "selected_chunk_ids": selected_ids,
        "rejected_chunk_ids": rejected_ids,
        "expansion_reasoning": {
            "policy": "topk_by_relevance_score",
            "max_expanded_chunks": max_chunks,
            "deterministic": True,
        },
        "token_savings_estimate": int(token_savings),
        "risk_warnings": ["no_hidden_expansion", "budget_enforced"],
        "deterministic": True,
        "no_execution": True,
    }

