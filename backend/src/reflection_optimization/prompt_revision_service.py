"""
MODULE: prompt_revision_service
PURPOSE: Deterministic prompt revision suggestions from structured traces (H-022)
ENCODING: UTF-8 WITHOUT BOM

No LLM calls — template expansion only.
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from src.reflection_optimization.feedback_contracts import recommendation_for_code
from src.reflection_optimization.reflection_schema import PromptCandidate, ReflectionTrace


def build_candidate_from_trace(trace: ReflectionTrace) -> PromptCandidate:
    """
    Produce a review-only PromptCandidate from structured trace fields.
    """
    codes = list(trace.failure_modes) if trace.failure_modes else ["unspecified_failure"]
    rec_lines = [recommendation_for_code(c) for c in codes]

    proposed = (
        "[Deterministic revision proposal]\n"
        + "\n".join(f"- {line}" for line in rec_lines)
    )

    reasoning = (
        "Reflection synthesis (template-bound): aggregated structured failure signals "
        f"({', '.join(codes)}) into actionable prompt scaffolding updates."
    )

    improvement = (
        "Expected reduction in recurrence for modes: "
        + ", ".join(codes)
        + "; targets measurable specificity and orchestration clarity."
    )

    current_snapshot = (
        f"Prior behaviour inferred from trace output_summary (score={trace.score:.3f}, "
        f"success={trace.success})."
    )

    return PromptCandidate(
        candidate_id=str(uuid4()),
        workflow_name=trace.workflow_name,
        current_prompt_summary=current_snapshot[:2000],
        proposed_prompt_summary=proposed[:8000],
        reflection_reasoning=reasoning[:4000],
        expected_improvement=improvement[:2000],
        human_review_required=True,
        approval_status="pending",
        created_at=datetime.utcnow(),
    )
