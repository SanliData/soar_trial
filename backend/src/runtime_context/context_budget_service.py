"""
MODULE: context_budget_service
PURPOSE: Deterministic token/char budgeting — explicit truncation markers (H-030)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def estimate_context_cost(char_count: int, layers: list[str]) -> dict[str, Any]:
    """Rough token estimate (chars/4) — deterministic heuristic."""
    base = max(0, char_count)
    layer_weight = 1.0 + 0.05 * len(set(layers))
    est_tokens = round(base / 4.0 * layer_weight, 2)
    return {
        "estimated_chars": base,
        "estimated_tokens": est_tokens,
        "heuristic": "chars_over_four_times_layer_weight_v1",
    }


def prioritize_context(layers: list[str], budget_tokens: float) -> dict[str, Any]:
    """Fixed priority order; returns layers that fit budget (simulated per-layer cost)."""
    priority = [
        "metadata",
        "capabilities",
        "topology",
        "hints",
        "traces",
        "full_capability_payload",
    ]
    fixed_cost = {"metadata": 120.0, "capabilities": 220.0, "topology": 90.0, "hints": 80.0, "traces": 60.0, "full_capability_payload": 400.0}
    ordered = [x for x in priority if x in layers]
    chosen: list[str] = []
    spend = 0.0
    for layer in ordered:
        c = fixed_cost.get(layer, 100.0)
        if spend + c <= budget_tokens:
            chosen.append(layer)
            spend += c
    return {"included_layers": chosen, "spent_tokens_estimate": round(spend, 2), "dropped_layers": [x for x in ordered if x not in chosen]}


def compress_metadata(payload: dict[str, Any], max_keys: int = 24) -> dict[str, Any]:
    """Deterministic key caps — shallow truncation with manifest."""
    keys = sorted(payload.keys())[:max_keys]
    out = {k: payload[k] for k in keys}
    out["_compression"] = {"keys_included": keys, "truncated": len(payload) > len(keys)}
    return out


def summarize_large_context(text: str, max_chars: int = 4000) -> dict[str, Any]:
    """Head/tail truncation with visible marker — no silent drop."""
    if len(text) <= max_chars:
        return {"summary": text, "truncated": False, "original_chars": len(text)}
    head = max_chars // 2 - 40
    tail = max_chars // 2 - 40
    body = text[:head] + "\n...[CONTEXT_TRUNCATED]...\n" + text[-tail:]
    return {"summary": body, "truncated": True, "original_chars": len(text), "max_chars": max_chars}


def apply_context_budget(
    estimated_chars: int,
    requested_layers: list[str],
    large_text_sample: str,
) -> dict[str, Any]:
    cost = estimate_context_cost(estimated_chars, requested_layers)
    budget_tokens = min(2000.0, max(200.0, cost["estimated_tokens"]))
    prioritized = prioritize_context(requested_layers or ["metadata", "capabilities"], budget_tokens)
    summary = summarize_large_context(large_text_sample, max_chars=3500) if large_text_sample else {"summary": "", "truncated": False}
    digest = hashlib.sha256(json.dumps(requested_layers, sort_keys=True).encode()).hexdigest()[:16]
    return {
        "cost_estimate": cost,
        "prioritization": prioritized,
        "large_text_handling": summary,
        "budget_digest": digest,
    }
