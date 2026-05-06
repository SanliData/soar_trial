"""
MODULE: context_decay_service
PURPOSE: Deterministic context-rot heuristics and recommendations (H-032)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

TRUNCATION_MARKER = "[WORKFLOW_CONTEXT_TRUNCATED]"

# rot_score 0.0 = healthy, 1.0 = severe (deterministic blend)
def detect_context_rot(
    token_estimate: int,
    turn_count: int,
    workflow_name: str = "",
) -> dict[str, Any]:
    t = max(0, int(token_estimate))
    n = max(0, int(turn_count))
    # Normalized pressure: more tokens and more turns increase rot.
    token_component = min(1.0, t / 120_000.0)
    turn_component = min(1.0, n / 80.0)
    rot = round((0.6 * token_component + 0.4 * turn_component) * 100) / 100.0
    return {
        "rot_score": rot,
        "components": {"token_pressure": token_component, "turn_pressure": turn_component},
        "heuristic": "linear_cap_v1",
    }


def recommend_compression(rot_score: float) -> dict[str, Any]:
    r = float(rot_score)
    if r < 0.35:
        action = "none"
    elif r < 0.65:
        action = "summarize_sections"
    else:
        action = "summarize_and_trim_tables"
    return {"recommended_action": action, "rot_threshold_rule": "fixed_buckets_v1"}


def recommend_session_reset(rot_score: float, turn_count: int) -> dict[str, Any]:
    reset = float(rot_score) >= 0.85 or int(turn_count) >= 100
    return {
        "reset_recommended": reset,
        "reason": "high_rot" if float(rot_score) >= 0.85 else ("turn_ceiling" if int(turn_count) >= 100 else "below_threshold"),
    }


def summarize_important_context(text: str, max_chars: int = 2000) -> dict[str, Any]:
    s = text or ""
    if len(s) <= max_chars:
        payload = s
        truncated = False
    else:
        payload = s[:max_chars] + TRUNCATION_MARKER
        truncated = True
    return {
        "summary_text": payload,
        "truncated": truncated,
        "marker": TRUNCATION_MARKER if truncated else None,
        "rule": "head_keep_with_explicit_marker_v1",
    }


def workflow_compress_bundle(context_text: str, token_estimate: int, turn_count: int) -> dict[str, Any]:
    rot = detect_context_rot(token_estimate=token_estimate, turn_count=turn_count)
    comp = recommend_compression(rot["rot_score"])
    reset = recommend_session_reset(rot["rot_score"], turn_count)
    summ = summarize_important_context(context_text)
    return {
        "decay": rot,
        "compression": comp,
        "reset": reset,
        "context_preview": summ,
    }
