"""
ROUTER: context_compression_router
PURPOSE: HTTP facade for deterministic context compression (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.context_compression.context_token_optimizer import export_context_token_optimizer_manifest
from src.context_compression.duplicate_context_detector import detect_duplicates
from src.context_compression.retrieval_relevance_service import score_retrieval_relevance
from src.context_compression.semantic_context_summarizer import summarize_context_collection
from src.context_orchestration.guardrail_context_service import export_guardrail_context_examples
from src.context_orchestration.instruction_context_service import export_instruction_context_examples

router = APIRouter(tags=["context-compression"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "context_compression_foundation": True,
        "llm_calls_for_compression": False,
        "automatic_context_deletion": False,
        "guardrail_compression_default": False,
    }
    merged.update(payload)
    return merged


@router.get("/system/context/compression")
async def get_context_compression() -> Dict[str, Any]:
    items = export_guardrail_context_examples() + export_instruction_context_examples()
    return _envelope(
        {
            "token_optimizer": export_context_token_optimizer_manifest(),
            "sample_collection_summary": summarize_context_collection(items, max_tokens_total=1200),
        }
    )


@router.get("/system/context/duplicates")
async def get_context_duplicates() -> Dict[str, Any]:
    ***REMOVED*** create a deterministic duplicate sample
    items = export_instruction_context_examples() + export_instruction_context_examples()
    return _envelope({"duplicates": detect_duplicates(items)})


@router.get("/system/context/relevance")
async def get_context_relevance() -> Dict[str, Any]:
    return _envelope(
        {
            "sample_relevance": score_retrieval_relevance(
                source_type="uploaded_documents",
                freshness_days=21,
                workflow_scope="procurement_analysis",
                geographic_scope="TX",
                commercial_relevance=0.8,
            )
        }
    )

