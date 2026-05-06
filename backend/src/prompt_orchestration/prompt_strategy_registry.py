"""
MODULE: prompt_strategy_registry
PURPOSE: Static approved prompt strategies (H-027)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

ALLOWED_STRATEGIES: frozenset[str] = frozenset(
    {
        "direct_prompting",
        "json_prompting",
        "role_prompting",
        "negative_prompting",
        "arq_reasoning",
        "few_shot_prompting",
        "constrained_summary",
    }
)

STRATEGY_METADATA: dict[str, dict[str, Any]] = {
    "direct_prompting": {
        "label": "Direct prompting",
        "hierarchy_rank": 1,
        "description": "Single-turn instruction without structured scaffolding.",
    },
    "json_prompting": {
        "label": "JSON prompting",
        "hierarchy_rank": 4,
        "description": "Structured outputs validated against approved JSON contracts.",
    },
    "role_prompting": {
        "label": "Role prompting",
        "hierarchy_rank": 3,
        "description": "Approved persona templates bound to commercial domains.",
    },
    "negative_prompting": {
        "label": "Negative prompting",
        "hierarchy_rank": 2,
        "description": "Explicit exclusion and refusal boundaries layered onto base strategy.",
    },
    "arq_reasoning": {
        "label": "ARQ structured reasoning",
        "hierarchy_rank": 5,
        "description": "Checklist-bound reasoning templates—no hidden chain-of-thought.",
    },
    "few_shot_prompting": {
        "label": "Few-shot prompting",
        "hierarchy_rank": 3,
        "description": "Bounded exemplars from curated corpora only (foundation metadata only).",
    },
    "constrained_summary": {
        "label": "Constrained summary",
        "hierarchy_rank": 4,
        "description": "Length-bounded summarisation with mandatory citation hooks.",
    },
}


def export_strategies_manifest() -> dict[str, Any]:
    rows = []
    for sid in sorted(ALLOWED_STRATEGIES):
        meta = dict(STRATEGY_METADATA[sid])
        meta["strategy_id"] = sid
        rows.append(meta)
    return {"strategies": rows}
