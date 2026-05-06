"""
MODULE: duplicate_context_detector
PURPOSE: Deterministic duplicate/redundancy detector for context (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from src.context_orchestration.context_validation_service import validate_context_item


def _norm(s: str) -> str:
    return " ".join((s or "").strip().lower().split())


def _fingerprint(text: str) -> str:
    payload = _norm(text).encode("utf-8", errors="strict")
    return hashlib.sha256(payload).hexdigest()[:20]


def detect_duplicates(items: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Detects duplicates across context content_summary only.

    Rules:
    - recommendations only
    - no automatic deletion
    """
    validated = [dict(x) for x in items]
    for it in validated:
        validate_context_item(it)

    # stable order
    validated.sort(key=lambda x: (x["workflow_scope"], x["context_type"], x["context_id"]))

    buckets: dict[str, list[dict[str, Any]]] = {}
    for it in validated:
        fp = _fingerprint(str(it.get("content_summary") or ""))
        buckets.setdefault(fp, []).append(it)

    groups = []
    token_waste = 0
    recommended = []

    for fp in sorted(buckets.keys()):
        rows = buckets[fp]
        if len(rows) < 2:
            continue
        rows_sorted = sorted(rows, key=lambda r: (-(int(r.get("priority") or 0)), r["context_id"]))
        keep = rows_sorted[0]
        dups = rows_sorted[1:]
        waste = sum(int(d.get("token_estimate") or 0) for d in dups)
        token_waste += waste
        groups.append(
            {
                "fingerprint": fp,
                "kept_context_id": keep["context_id"],
                "duplicates": [
                    {"context_id": d["context_id"], "context_type": d["context_type"], "workflow_scope": d["workflow_scope"]}
                    for d in dups
                ],
                "estimated_token_waste": waste,
            }
        )
        recommended.extend([d["context_id"] for d in dups])

    # Make deterministic list
    recommended_sorted = sorted(set(recommended))
    return {
        "duplicate_groups": groups,
        "estimated_token_waste": int(token_waste),
        "recommended_removals": recommended_sorted,
        "automatic_deletion": False,
        "deterministic": True,
        "digest": hashlib.sha256(json.dumps(groups, sort_keys=True).encode("utf-8")).hexdigest()[:16],
    }

