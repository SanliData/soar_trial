"""
MODULE: cluster_validation_service
PURPOSE: Validate clustering / batching governance (H-042)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def validate_clustering_config(cfg: dict[str, Any]) -> None:
    if cfg.get("unbounded_cluster_growth") is True:
        raise ValueError("unbounded cluster growth rejected")
    k = cfg.get("k_target")
    if k is not None and (not isinstance(k, int) or k < 1 or k > 10_000):
        raise ValueError("invalid k_target")


def validate_semantic_batch(batch: dict[str, Any]) -> None:
    mx = batch.get("max_items")
    if not isinstance(mx, int) or mx < 1 or mx > 1024:
        raise ValueError("invalid semantic batch size")
