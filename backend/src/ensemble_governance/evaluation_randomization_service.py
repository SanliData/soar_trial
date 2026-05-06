"""
MODULE: evaluation_randomization_service
PURPOSE: Seeded deterministic evaluator rotation — auditable (H-043)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import hashlib

from typing import Any


def deterministic_evaluator_order(evaluator_ids: tuple[str, ...], *, seed: str) -> list[str]:
    keyed = [(hashlib.sha256(f"{seed}:{eid}".encode("utf-8")).hexdigest(), eid) for eid in evaluator_ids]
    return [eid for _, eid in sorted(keyed)]


def export_evaluation_randomization_manifest() -> dict[str, Any]:
    order = deterministic_evaluator_order(("ev-policy", "ev-structure", "ev-safety"), seed="h043-replay-seed-v1")
    return {
        "rotation_strategy": "subset_deterministic_hash_order",
        "seed_claim": "h043-replay-seed-v1",
        "example_order": order,
        "replay_safe": True,
        "controlled_operational_randomness": True,
        "deterministic": True,
    }
