"""
MODULE: speculative_execution_service
PURPOSE: Speculative execution metadata only — governed (H-041)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_SPECULATIVE_MANIFEST: dict[str, Any] = {
    "candidates_template": [
        {
            "candidate_id": "spec_a_primary_path",
            "requires_rollback_plan": True,
            "confidence_floor": 0.72,
            "evaluation_trigger_required": True,
            "tokens_reserved_cap": 2000,
        }
    ],
    "rollback_metadata_default": {"strategy": "discard_outputs_restore_prompt_hash", "autonomous_commit": False},
    "evaluation_requirements": ["human_or_governed_evaluator_flag", "trace_id_binding"],
    "uncontrolled_speculative_execution": False,
    "metadata_only": True,
    "deterministic": True,
}


def export_speculative_execution_manifest() -> dict[str, Any]:
    return dict(_SPECULATIVE_MANIFEST)
