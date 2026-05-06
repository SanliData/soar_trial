"""
MODULE: validation_agent_service
PURPOSE: Isolated validation agent constraints — bounded context (H-035)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

MAX_VALIDATION_CONTEXT_CHARS = 64_000
ALLOWED_VALIDATION_PREFIXES = ("validation:", "read:")


def enforce_isolated_validation(
    *,
    context_payload_chars: int,
    permission: str,
    delegation_depth: int,
) -> dict[str, Any]:
    if int(context_payload_chars) > MAX_VALIDATION_CONTEXT_CHARS:
        raise ValueError("context exceeds isolated validation agent budget")
    perm = (permission or "").strip()
    if not perm:
        raise ValueError("permission required for validation agent")
    if not any(perm.startswith(p) for p in ALLOWED_VALIDATION_PREFIXES):
        raise ValueError("validation agents require validation: or read: permission prefix")
    if int(delegation_depth) > 1:
        raise ValueError("validation agents cannot delegate beyond depth 1 in foundation mode")
    return {
        "isolated": True,
        "compressed_summaries_only": True,
        "unrestricted_delegation": False,
        "max_context_chars": MAX_VALIDATION_CONTEXT_CHARS,
        "policy_version": "validation_agent_v1",
    }
