"""
MODULE: subagent_context_service
PURPOSE: Create isolated subagent context metadata (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from src.context_compression.semantic_context_summarizer import summarize_context_collection
from src.context_isolation.isolated_execution_context import IsolatedExecutionContext
from src.context_isolation.workflow_context_partitioning import get_partition
from src.context_orchestration.context_validation_service import validate_context_item


def build_isolated_subagent_context(
    *,
    workflow_scope: str,
    subagent_id: str,
    context_items: list[dict[str, Any]],
    compression_allowed: bool = True,
) -> dict[str, Any]:
    wf = (workflow_scope or "").strip()
    sid = (subagent_id or "").strip()
    if not wf or not sid:
        raise ValueError("invalid workflow_scope or subagent_id")

    part = get_partition(wf)
    allowed = tuple(sorted(set(part["allowed_context_types"])))
    iso = IsolatedExecutionContext(workflow_scope=wf, subagent_id=sid, allowed_context_types=allowed)

    # Filter to allowed types and same workflow by default (isolation)
    filtered = []
    for it in context_items:
        validate_context_item(it)
        if it["context_type"] not in allowed:
            continue
        if it.get("workflow_scope") != wf:
            continue
        filtered.append(dict(it))

    summary = summarize_context_collection(
        filtered,
        max_tokens_total=4800,
        allow_guardrail_compression=False,
    )
    if not compression_allowed:
        # explicit: return only preserved view without compression marker
        summary = summarize_context_collection(
            filtered,
            max_tokens_total=1_000_000,
            allow_guardrail_compression=False,
        )

    digest = hashlib.sha256(json.dumps(summary, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    return {
        "isolated_execution_context": {
            "workflow_scope": iso.workflow_scope,
            "subagent_id": iso.subagent_id,
            "allowed_context_types": list(iso.allowed_context_types),
            "shared_memory_allowed": iso.shared_memory_allowed,
            "created_at": iso.created_at,
            "auditable": iso.auditable,
        },
        "context_summary": summary,
        "context_digest": digest,
        "no_unrestricted_shared_context": True,
        "deterministic": True,
    }

