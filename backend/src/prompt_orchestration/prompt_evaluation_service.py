"""
MODULE: prompt_evaluation_service
PURPOSE: Deterministic prompt configuration scoring — no LLM calls (H-027)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.prompt_orchestration.prompt_strategy_registry import ALLOWED_STRATEGIES, STRATEGY_METADATA
from src.prompt_orchestration.reasoning_policy_service import select_strategy_for_task
from src.prompt_orchestration.prompt_validation_service import EvaluatePromptRequest, validate_evaluate_request


def _strategy_alignment_score(recommended: str, chosen: str, override_used: bool) -> tuple[float, str]:
    if not override_used:
        return 1.0, "no override — policy default applies"
    if chosen == recommended:
        return 1.0, "override matches policy recommendation"
    if chosen not in ALLOWED_STRATEGIES:
        return 0.0, "invalid strategy id"
    rec_rank = STRATEGY_METADATA[recommended]["hierarchy_rank"]
    ch_rank = STRATEGY_METADATA[chosen]["hierarchy_rank"]
    if abs(rec_rank - ch_rank) <= 1:
        return 0.85, "override adjacent to policy — acceptable with review"
    return 0.55, "override diverges from policy — requires governance review"


def evaluate_prompt_configuration(body: EvaluatePromptRequest) -> dict[str, Any]:
    validate_evaluate_request(body)
    policy = select_strategy_for_task(body.task_type)
    recommended = policy["recommended_strategy"]
    override_used = body.strategy_override is not None
    effective = body.strategy_override if override_used else recommended

    align_score, align_note = _strategy_alignment_score(recommended, effective, override_used)

    issues: list[str] = []
    score = 70.0
    score += align_score * 15.0

    if body.contract_id:
        score += 8.0
    else:
        issues.append("missing JSON contract — structured outputs not pinned")

    if body.persona:
        score += 5.0
    else:
        issues.append("missing approved persona — role boundaries weaker")

    if effective == "arq_reasoning" and not body.arq_template_id:
        issues.append("ARQ strategy without explicit template id — bind a checklist")

    if body.include_negative_constraints:
        score += 2.0
    else:
        issues.append("negative constraints not enabled — add refusal boundaries for production")

    score = min(100.0, max(0.0, round(score, 2)))

    return {
        "evaluation_score": score,
        "recommended_strategy": recommended,
        "effective_strategy": effective,
        "policy": policy,
        "alignment": {"score": align_score, "note": align_note},
        "issues": issues,
        "checks": {
            "json_contract_present": body.contract_id is not None,
            "persona_present": body.persona is not None,
            "negative_constraints_enabled": body.include_negative_constraints,
            "arq_template_present": body.arq_template_id is not None,
        },
    }
