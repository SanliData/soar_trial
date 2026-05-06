"""
MODULE: ensemble_validation_service
PURPOSE: Reject hidden weighting configs (H-043)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def validate_ensemble_config(cfg: dict[str, Any]) -> None:
    if cfg.get("hidden_evaluator_weights") is True:
        raise ValueError("hidden ensemble weighting rejected")
    if cfg.get("autonomous_swarm_evaluators") is True:
        raise ValueError("autonomous evaluator swarm rejected")
