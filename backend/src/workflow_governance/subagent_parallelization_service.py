"""
MODULE: subagent_parallelization_service
PURPOSE: Bounded parallel work — explicit policy and hard caps (H-032)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

MAX_PARALLEL_SUBTASKS: int = 3


def validate_parallel_plan(
    parallel_count: int,
    policy_id: str,
) -> dict[str, Any]:
    if not policy_id or not str(policy_id).strip():
        raise ValueError("parallelization policy_id is required")
    pid = str(policy_id).strip()
    if pid not in ("bounded_fanout", "sequential_only"):
        raise ValueError(f"unknown parallelization policy: {pid}")
    n = int(parallel_count)
    if n < 0:
        raise ValueError("parallel_count must be non-negative")
    if n > MAX_PARALLEL_SUBTASKS:
        raise ValueError(f"parallel_count exceeds cap: {n} > {MAX_PARALLEL_SUBTASKS}")
    if pid == "sequential_only" and n > 1:
        raise ValueError("sequential_only policy does not allow parallel_count > 1")
    return {
        "parallel_ok": True,
        "parallel_count": n,
        "max_parallel": MAX_PARALLEL_SUBTASKS,
        "policy_id": pid,
        "unrestricted_spawning": False,
    }


def describe_parallel_policies() -> dict[str, Any]:
    return {
        "max_parallel_subtasks": MAX_PARALLEL_SUBTASKS,
        "policies": {
            "bounded_fanout": "Up to max_parallel subtasks with explicit task ids.",
            "sequential_only": "Forces serial execution (parallel_count must be 1).",
        },
    }
