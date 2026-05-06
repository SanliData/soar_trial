"""
MODULE: context_token_optimizer
PURPOSE: Token-budget-aware context compression guidance (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.context_compression.duplicate_context_detector import detect_duplicates
from src.context_compression.semantic_context_summarizer import summarize_context_collection
from src.inference_runtime.runtime_token_budget_service import categorize_budget


def export_context_token_optimizer_manifest() -> dict[str, Any]:
    """
    Deterministic manifest only: provides a repeatable calculation shape
    without mutating runtime context.
    """
    # Synthetic demo inputs (not reading files, not invoking models).
    sample_items: list[dict[str, Any]] = [
        {
            "context_id": "sample-inst",
            "context_type": "instruction_context",
            "workflow_scope": "procurement_analysis",
            "content_summary": "Summarize procurement constraints; cite sources; no external execution.",
            "source_lineage": {},
            "priority": 90,
            "token_estimate": 40,
            "isolation_required": True,
            "compression_allowed": True,
            "created_at": "2026-01-01T00:00:00+00:00",
            "tags": ["instructions"],
        },
        {
            "context_id": "sample-gr",
            "context_type": "guardrail_context",
            "workflow_scope": "procurement_analysis",
            "content_summary": "No secrets. No uncontrolled execution. Guardrails visible separately.",
            "source_lineage": {},
            "priority": 100,
            "token_estimate": 30,
            "isolation_required": True,
            "compression_allowed": False,
            "created_at": "2026-01-01T00:00:00+00:00",
            "tags": ["guardrails"],
        },
    ]

    # Budget hint: treat typed context as orchestration budget
    budget = categorize_budget("orchestration")
    max_tokens_total = int(budget["budget_tokens"] * 0.18)

    summary = summarize_context_collection(sample_items, max_tokens_total=max_tokens_total)
    dedup = detect_duplicates(sample_items)

    original = int(summary["original_token_estimate"])
    compressed = int(summary["compressed_token_estimate"])
    savings = max(0, original - compressed)
    waste = int(dedup["estimated_token_waste"])

    prefill_pressure = round(min(1.0, (compressed / float(budget["hard_cap_tokens"])) if budget["hard_cap_tokens"] else 0.0), 4)
    return {
        "budget_category": "orchestration",
        "budget": dict(budget),
        "typed_context_budget_slice": 0.18,
        "example_summary": summary,
        "example_duplicate_detection": dedup,
        "context_token_cost": compressed,
        "compression_savings": savings,
        "duplicate_context_waste": waste,
        "prefill_pressure_from_context": prefill_pressure,
        "deterministic": True,
        "no_hidden_runtime_mutation": True,
    }

