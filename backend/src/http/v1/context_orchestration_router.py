"""
ROUTER: context_orchestration_router
PURPOSE: HTTP facade for typed context orchestration (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.context_orchestration.context_validation_service import ALLOWED_CONTEXT_TYPES
from src.context_orchestration.example_context_service import export_example_context_examples
from src.context_orchestration.guardrail_context_service import export_guardrail_context_examples
from src.context_orchestration.instruction_context_service import export_instruction_context_examples
from src.context_orchestration.knowledge_context_service import export_knowledge_context_examples
from src.context_orchestration.memory_context_service import export_memory_context_examples
from src.context_orchestration.tool_context_service import export_tool_context_examples
from src.context_orchestration.context_lifecycle_service import prioritize_context, summarize_context_set

router = APIRouter(tags=["context-orchestration"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "typed_context_orchestration_foundation": True,
        "shared_global_context_blob": False,
        "hidden_context_mutation": False,
        "uncontrolled_subagent_spawning": False,
    }
    merged.update(payload)
    return merged


def _sample_context_items() -> list[dict[str, Any]]:
    return (
        export_guardrail_context_examples()
        + export_instruction_context_examples()
        + export_tool_context_examples()
        + export_knowledge_context_examples()
        + export_memory_context_examples()
        + export_example_context_examples()
    )


@router.get("/system/context/types")
async def get_context_types() -> Dict[str, Any]:
    return _envelope(
        {
            "types": sorted(ALLOWED_CONTEXT_TYPES),
            "required_fields": [
                "context_id",
                "context_type",
                "workflow_scope",
                "content_summary",
                "source_lineage",
                "priority",
                "token_estimate",
                "isolation_required",
                "compression_allowed",
                "created_at",
                "tags",
            ],
            "rules": {
                "invalid_context_type_rejected": True,
                "knowledge_and_memory_require_lineage": True,
                "guardrails_not_compressed_by_default": True,
                "tool_context_requires_capability_references": True,
            },
        }
    )


@router.get("/system/context/lifecycle")
async def get_context_lifecycle() -> Dict[str, Any]:
    items = _sample_context_items()
    return _envelope(
        {
            "lifecycle": {
                "register_context": "deterministic_validation_only",
                "list_context": "workflow_filtered_views",
                "prioritize_context": "priority_then_stale_then_id",
                "mark_context_stale": "audit_preserving_no_deletion",
                "summarize_context_set": "deterministic_head_tail_truncation",
            },
            "sample_summary": summarize_context_set(items, max_tokens_total=2400, allow_guardrail_compression=False),
        }
    )


@router.get("/system/context/priorities")
async def get_context_priorities() -> Dict[str, Any]:
    items = _sample_context_items()
    ordered = prioritize_context(items)
    return _envelope(
        {
            "prioritization": {
                "strategy": "priority_desc_nonstale_then_id",
                "items": [{"context_id": x["context_id"], "context_type": x["context_type"], "priority": x["priority"]} for x in ordered],
            }
        }
    )

