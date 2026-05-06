"""
MODULE: skill_context_optimizer
PURPOSE: Token-aware context guidance — no hidden context mutation (H-040)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.skill_runtime.skill_registry_service import SKILL_REGISTRY


def export_context_optimization_manifest() -> dict[str, Any]:
    rows = []
    for name in sorted(SKILL_REGISTRY.keys()):
        rows.append(
            {
                "skill_name": name,
                "selective_loading": ["tool_schemas_minimal", "workspace_policy_slice"],
                "compression_guidance": "summarize_intermediate_only",
                "token_budget_units": 24,
                "pruning_recommendations": ["drop_redundant_citations", "freeze_evidence_handles"],
            }
        )
    return {
        "per_skill": rows,
        "hidden_context_mutation": False,
        "monolithic_runtime_prompt": False,
        "deterministic": True,
    }
