"""
ROUTER: selective_context_runtime_router
PURPOSE: HTTP facade for selective context runtime (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.selective_context_runtime.chunk_compression_service import compress_chunk_deterministically
from src.selective_context_runtime.compressed_embedding_service import export_compressed_embedding_manifest
from src.selective_context_runtime.relevance_policy_service import score_relevance_policy
from src.selective_context_runtime.retrieval_budget_service import export_retrieval_budgets
from src.selective_context_runtime.selective_expansion_service import decide_selective_expansion
from src.selective_context_runtime.token_pressure_router import route_token_pressure_mode

router = APIRouter(tags=["selective-context-runtime"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "selective_context_runtime_foundation": True,
        "rl_training_enabled": False,
        "hidden_context_expansion": False,
        "unlimited_retrieval_expansion": False,
        "deterministic": True,
    }
    merged.update(payload)
    return merged


def _sample_chunks() -> list[dict[str, Any]]:
    return [
        {
            "chunk_id": "c1",
            "text": "RFP requires ISO 27001 and net-30 terms. Delivery 12 weeks.",
            "source_lineage": {"authority_score": 0.88, "freshness_days": 3},
        },
        {
            "chunk_id": "c2",
            "text": "General marketing brochure. No procurement terms mentioned.",
            "source_lineage": {"authority_score": 0.55, "freshness_days": 21},
        },
        {
            "chunk_id": "c3",
            "text": "Permit inspection scheduled; compliance notes attached.",
            "source_lineage": {"authority_score": 0.78, "freshness_days": 7},
        },
    ]


@router.get("/system/selective-context/compression")
async def get_chunk_compression() -> Dict[str, Any]:
    ch = _sample_chunks()[0]
    compressed = compress_chunk_deterministically(
        chunk_id=ch["chunk_id"],
        text=ch["text"],
        source_lineage=ch["source_lineage"],
        expansion_allowed=True,
    )
    return _envelope({"chunk_compression": compressed, "embedding_metadata": export_compressed_embedding_manifest()})


@router.get("/system/selective-context/relevance")
async def get_relevance_policy() -> Dict[str, Any]:
    ch = _sample_chunks()[0]
    return _envelope(
        {
            "relevance": score_relevance_policy(
                query="telecom bid ISO",
                chunk_text=ch["text"],
                source_authority=0.88,
                freshness_days=3,
                workflow_scope="procurement_analysis",
                commercial_relevance=0.8,
                geographic_relevance=0.55,
            )
        }
    )


@router.get("/system/selective-context/expansion")
async def get_selective_expansion() -> Dict[str, Any]:
    return _envelope(
        {
            "expansion": decide_selective_expansion(
                workflow_name="procurement_analysis",
                query="ISO 27001 net-30",
                chunks=_sample_chunks(),
            )
        }
    )


@router.get("/system/selective-context/token-pressure")
async def get_token_pressure() -> Dict[str, Any]:
    return _envelope({"token_pressure": route_token_pressure_mode(context_tokens=22000, max_tokens=32000)})


@router.get("/system/selective-context/budgets")
async def get_retrieval_budgets() -> Dict[str, Any]:
    return _envelope({"budgets": export_retrieval_budgets()})

