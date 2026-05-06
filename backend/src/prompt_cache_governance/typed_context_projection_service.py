"""
MODULE: typed_context_projection_service
PURPOSE: Project cache governance into H-044 typed contexts without new context types (H-050)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.context_orchestration.knowledge_context_service import build_knowledge_context
from src.context_orchestration.memory_context_service import build_memory_context
from src.prompt_cache_governance.static_prefix_registry import export_static_prefix_registry
from src.prompt_cache_governance.dynamic_suffix_service import export_dynamic_suffix


def project_static_prefix_context(*, workflow_scope: str = "procurement_analysis") -> dict[str, Any]:
    """
    Implements H-050 'static_prefix_context' support using knowledge_context + tags.
    """
    prefix = export_static_prefix_registry()
    summary = f"static_prefix_components={len(prefix['static_prefix_components'])}; stable={prefix['static_prefix_stable']}"
    return build_knowledge_context(
        context_id="ctx-cache-prefix-001",
        workflow_scope=workflow_scope,
        summary=summary,
        source_type="prompt_cache_static_prefix",
        source_record_id="prefix:v1",
        priority=80,
        isolation_required=True,
        tags=["knowledge", "cacheable_context", "static_prefix_context"],
    )


def project_dynamic_suffix_context(*, session_id: str = "sess-demo-001", workflow_scope: str = "procurement_analysis") -> dict[str, Any]:
    """
    Implements H-050 'dynamic_suffix_context' support using memory_context + tags.
    """
    suffix = export_dynamic_suffix(session_id=session_id)
    summary = f"dynamic_suffix_components={len(suffix['dynamic_suffix_components'])}; auditable={suffix['auditable']}"
    return build_memory_context(
        context_id="ctx-cache-suffix-001",
        workflow_scope=workflow_scope,
        summary=summary,
        source_type="prompt_cache_dynamic_suffix",
        source_record_id=session_id,
        priority=55,
        isolation_required=True,
        tags=["memory", "dynamic_suffix_context", "volatile_context"],
    )

