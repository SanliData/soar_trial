"""
MODULE: prompt_cache_validation_service
PURPOSE: Validation for prompt cache governance payloads (H-050)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import re
from typing import Any


_VOLATILE_RE = re.compile(r"(\b20\d{2}-\d{2}-\d{2}\b|\buuid\b|\brandom\b|\btimestamp\b)", re.IGNORECASE)


def detect_volatile_content(text: str) -> bool:
    if not isinstance(text, str):
        return True
    return _VOLATILE_RE.search(text) is not None


def require_no_volatile_static_prefix(prefix_components: list[dict[str, Any]]) -> None:
    for c in prefix_components:
        if c.get("cacheable") is True and c.get("volatile_content_detected") is True:
            raise ValueError("volatile content detected in static prefix")


def validate_cache_metrics(metrics: dict[str, Any]) -> None:
    for k in (
        "cache_creation_input_tokens",
        "cache_read_input_tokens",
        "input_tokens",
        "estimated_cost_savings",
        "estimated_prefill_saved_tokens",
    ):
        v = metrics.get(k)
        if not isinstance(v, int) or v < 0:
            raise ValueError(f"invalid {k}")
    ratio = metrics.get("cache_efficiency_ratio")
    if not isinstance(ratio, float) or ratio < 0.0 or ratio > 1.0:
        raise ValueError("invalid cache_efficiency_ratio")

