"""
MODULE: graph_reasoning_service
PURPOSE: Read-only reasoning overlays — explainable (H-042)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_graph_reasoning_manifest() -> dict[str, Any]:
    return {
        "reasoning_patterns": [
            {
                "pattern_id": "rp-path-explain",
                "inputs": ["path_edge_list"],
                "outputs": ["natural_language_summary_template_id"],
                "mutates_graph": False,
            }
        ],
        "deterministic": True,
    }
