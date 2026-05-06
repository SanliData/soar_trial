"""
MODULE: compression_service
PURPOSE: Deterministic orchestration context compression — visible markers (H-031)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def summarize_context(text: str, max_chars: int = 3500) -> dict[str, Any]:
    if len(text) <= max_chars:
        return {"summary": text, "truncated": False, "kind": "context"}
    half = max_chars // 2 - 24
    body = text[:half] + "\n...[HARNESS_CONTEXT_TRUNCATED]...\n" + text[-half:]
    return {"summary": body, "truncated": True, "kind": "context", "original_chars": len(text)}


def compress_trajectory(steps: list[str], max_items: int = 12) -> dict[str, Any]:
    trimmed = steps[:max_items]
    dropped = max(0, len(steps) - max_items)
    digest = hashlib.sha256(json.dumps(steps, sort_keys=False).encode()).hexdigest()[:12]
    return {
        "steps": trimmed,
        "dropped_tail_count": dropped,
        "digest": digest,
        "truncated": dropped > 0,
        "kind": "trajectory",
    }


def compress_memory(memory_type: str, payload: str, max_chars: int = 2000) -> dict[str, Any]:
    s = summarize_context(payload, max_chars=max_chars)
    s["memory_type"] = memory_type
    s["kind"] = "memory"
    return s


def prioritize_runtime_context(layers: list[str], budget_units: float) -> dict[str, Any]:
    order = ["working_memory", "workflow_memory", "semantic_memory", "user_context_memory", "episodic_memory"]
    fixed = {"working_memory": 1.0, "workflow_memory": 1.2, "semantic_memory": 2.0, "user_context_memory": 1.5, "episodic_memory": 1.8}
    chosen: list[str] = []
    spend = 0.0
    for layer in order:
        if layer not in layers:
            continue
        cost = fixed.get(layer, 1.5)
        if spend + cost <= budget_units:
            chosen.append(layer)
            spend += cost
    return {
        "included_memory_layers": chosen,
        "spent_budget_units": round(spend, 3),
        "dropped": [x for x in layers if x not in chosen],
    }


def compress_bundle(mode: str, payload: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    extra = extra or {}
    if mode == "context":
        return summarize_context(payload)
    if mode == "trajectory":
        steps = extra.get("steps") if isinstance(extra.get("steps"), list) else payload.splitlines()
        steps = [str(x) for x in steps]
        if not steps:
            steps = ["(empty_trajectory)"]
        return compress_trajectory(steps)
    if mode == "memory":
        mt = str(extra.get("memory_type", "working_memory"))
        return compress_memory(mt, payload)
    raise ValueError(f"unknown compress mode: {mode}")
