"""
MODULE: hybrid_retrieval_service
PURPOSE: Retrieval policy modes metadata (deterministic) (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

RETRIEVAL_MODES = ("keyword", "semantic", "hybrid", "graph_assisted", "selective_context")


def export_hybrid_retrieval_policy() -> dict[str, Any]:
    return {
        "retrieval_modes": list(RETRIEVAL_MODES),
        "ranking_policy": "deterministic_weighted_linear_v1",
        "notes": [
            "semantic mode is metadata only in foundation (no vector DB rewrite).",
            "selective_context mode integrates with selective_context_runtime policies.",
        ],
        "deterministic": True,
    }


def validate_retrieval_mode(mode: str) -> None:
    m = (mode or "").strip()
    if m not in RETRIEVAL_MODES:
        raise ValueError("invalid retrieval mode")

