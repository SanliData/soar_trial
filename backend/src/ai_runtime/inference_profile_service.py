"""
MODULE: inference_profile_service
PURPOSE: Build deterministic AIRuntimeProfile from task + context (H-021)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import time

from src.ai_runtime.model_routing_service import route_model
from src.ai_runtime.prompt_compaction_service import compact_context
from src.ai_runtime.runtime_schema import AIRuntimeProfile, AIRuntimeTask
from src.ai_runtime.token_budget_service import enforce_token_budget, estimate_tokens


def _estimate_output_tokens(task: AIRuntimeTask) -> int:
    """Upper-bound heuristic without invoking a model."""
    return max(1, min(task.max_output_tokens, task.max_output_tokens // 2 + 32))


def build_inference_profile(task: AIRuntimeTask, input_context: str) -> AIRuntimeProfile:
    """
    Compose routing + sizing metadata. Does NOT call remote LLMs.
    """
    t0 = time.perf_counter()
    warnings: list[str] = []

    routed = route_model(task)
    selected_model = routed["selected_model"]
    model_family = routed["model_family"]

    working = input_context or ""
    ein = estimate_tokens(working)

    prompt_compaction_applied = False

    if ein > task.max_input_tokens:
        if task.allow_compaction:
            cr = compact_context(working, task.max_input_tokens)
            working = cr.compacted_text
            ein = estimate_tokens(working)
            prompt_compaction_applied = cr.compaction_applied
            if cr.compaction_applied:
                warnings.append("Context compacted deterministically to satisfy token budget.")
        else:
            tb = enforce_token_budget(working, task.max_input_tokens)
            working = tb.text
            ein = estimate_tokens(working)
            if tb.warning:
                warnings.append(tb.warning)

        if ein > task.max_input_tokens:
            tb2 = enforce_token_budget(working, task.max_input_tokens)
            working = tb2.text
            ein = estimate_tokens(working)
            if tb2.warning:
                warnings.append(tb2.warning)

    eout = _estimate_output_tokens(task)
    total = ein + eout

    t1 = time.perf_counter()
    latency_ms = max(1, int((t1 - t0) * 1000))
    ttft = max(1, latency_ms // 4) if latency_ms > 0 else None

    status_literal = "adjusted" if prompt_compaction_applied or warnings else "ready"

    return AIRuntimeProfile(
        task_id=task.task_id,
        task_type=task.task_type,
        selected_model=selected_model,
        model_family=model_family,
        quality_tier=task.requested_quality_tier,
        estimated_input_tokens=ein,
        estimated_output_tokens=eout,
        estimated_total_tokens=total,
        prompt_compaction_applied=prompt_compaction_applied,
        latency_ms=latency_ms,
        time_to_first_token_ms=ttft,
        status=status_literal,  ***REMOVED*** type: ignore[arg-type]
        warnings=warnings,
    )
