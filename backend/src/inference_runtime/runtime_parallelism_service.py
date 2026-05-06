"""
MODULE: runtime_parallelism_service
PURPOSE: Concurrency governance — no runaway parallelism (H-041)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_PARALLELISM_POLICY: dict[str, Any] = {
    "max_parallel_workflows": 4,
    "token_concurrency_cap": 88000,
    "batching_compatibility_required": True,
    "max_retry_concurrency": 2,
    "autonomous_scaling": False,
    "deterministic": True,
}


def export_runtime_parallelism_manifest() -> dict[str, Any]:
    return dict(_PARALLELISM_POLICY)


def evaluate_parallelism_gate(
    *,
    active_workflows: int,
    in_flight_tokens: int,
    active_retries: int,
) -> dict[str, Any]:
    pol = export_runtime_parallelism_manifest()
    ok_wf = active_workflows <= int(pol["max_parallel_workflows"])
    ok_tok = in_flight_tokens <= int(pol["token_concurrency_cap"])
    ok_retry = active_retries <= int(pol["max_retry_concurrency"])
    allowed = ok_wf and ok_tok and ok_retry
    return {
        "allowed": allowed,
        "checks": {
            "workflows_under_cap": ok_wf,
            "tokens_under_cap": ok_tok,
            "retries_under_cap": ok_retry,
        },
        "deterministic": True,
    }
