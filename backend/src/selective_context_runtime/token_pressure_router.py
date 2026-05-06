"""
MODULE: token_pressure_router
PURPOSE: Route retrieval behavior based on token pressure (deterministic) (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def route_token_pressure_mode(*, context_tokens: int, max_tokens: int) -> dict[str, Any]:
    ct = max(0, int(context_tokens))
    mt = max(1, int(max_tokens))
    ratio = ct / float(mt)
    if ratio < 0.55:
        mode = "full_context_allowed"
    elif ratio < 0.75:
        mode = "selective_expansion"
    elif ratio < 0.9:
        mode = "summary_only"
    else:
        mode = "retrieval_fallback"
    return {
        "mode": mode,
        "context_tokens": ct,
        "max_tokens": mt,
        "pressure_ratio": round(ratio, 4),
        "deterministic": True,
        "autonomous_workflow_mutation": False,
    }

