"""
MODULE: prefill_decode_optimizer
PURPOSE: Prefill/decode guidance metadata — no hidden mutation (H-041)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_prefill_decode_guidance_manifest() -> dict[str, Any]:
    return {
        "selective_context_loading": {
            "enabled_governance": True,
            "rule": "include_only_manifest_referenced_documents",
        },
        "prefill_reduction_guidance": [
            {"pattern": "repeated_system_prompt_blocks", "action": "dedupe_via_template_id"},
            {"pattern": "verbose_tool_schemas_in_context", "action": "bind_schema_by_capability_id_reference"},
        ],
        "decode_efficiency_metadata": {
            "streaming_recommended_for_long_outputs": True,
            "max_decode_tokens_soft_cap": 4096,
        },
        "long_context_governance": {
            "max_context_window_claim_tokens": 128000,
            "warn_above_soft_tokens": 64000,
        },
        "duplicate_context_detection": {
            "strategy": "hash_paragraph_slices_deterministic",
            "automatic_removal": False,
        },
        "metadata_only": True,
        "deterministic": True,
    }
