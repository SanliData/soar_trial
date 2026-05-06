"""
MODULE: agent_scope_service
PURPOSE: Isolated subagent scope definitions — compressed governance surface (H-038)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_AGENT_SCOPES: list[dict[str, Any]] = [
    {
        "scope_id": "research_subagent_a",
        "allowed_tools": ["read_http_allowlisted", "structured_parse_local"],
        "allowed_domains": ["catalog-read.internal", "verification-service.internal"],
        "memory_visibility": "no_cross_project_writes",
        "execution_permissions": ["read_only_aggregate"],
        "escalation_boundary": "human_checkpoint_before_any_write_path",
        "summaries_compressed": True,
    },
    {
        "scope_id": "critique_subagent_b",
        "allowed_tools": ["evaluation_rubric_compare"],
        "allowed_domains": [],
        "memory_visibility": "evaluation_transcripts_only",
        "execution_permissions": ["annotate_only"],
        "escalation_boundary": "cannot_promote_deploy",
        "summaries_compressed": True,
    },
]


def export_agent_scopes_manifest() -> dict[str, Any]:
    return {
        "subagent_scopes": list(_AGENT_SCOPES),
        "isolated_execution_required": True,
        "uncontrolled_spawn": False,
    }
