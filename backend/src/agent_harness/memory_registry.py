"""
MODULE: memory_registry
PURPOSE: Deterministic memory domain metadata — no live mutation API (H-031)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

MEMORY_TYPES: frozenset[str] = frozenset(
    {
        "working_memory",
        "semantic_memory",
        "episodic_memory",
        "user_context_memory",
        "workflow_memory",
    }
)

# Lifecycle / scope boundaries — documentation for orchestrators; no runtime store here.
MEMORY_REGISTRY: dict[str, dict[str, Any]] = {
    "working_memory": {
        "lifecycle": "request_scoped",
        "mutation_policy": "append_only_turns",
        "max_soft_units": 8000,
    },
    "semantic_memory": {
        "lifecycle": "curated_store",
        "mutation_policy": "governance_write_path_only",
        "max_soft_units": 32000,
    },
    "episodic_memory": {
        "lifecycle": "session_windowed",
        "mutation_policy": "structured_events_only",
        "max_soft_units": 16000,
    },
    "user_context_memory": {
        "lifecycle": "tenant_scoped",
        "mutation_policy": "explicit_user_updates_only",
        "max_soft_units": 12000,
    },
    "workflow_memory": {
        "lifecycle": "workflow_instance",
        "mutation_policy": "checkpoint_snapshots",
        "max_soft_units": 24000,
    },
}


def export_memory_manifest() -> dict[str, Any]:
    rows = []
    for k in sorted(MEMORY_REGISTRY.keys()):
        rows.append({"memory_type": k, **MEMORY_REGISTRY[k]})
    return {"memory_types": sorted(MEMORY_TYPES), "domains": rows}


def get_memory_domain(memory_type: str) -> dict[str, Any] | None:
    if memory_type not in MEMORY_TYPES:
        return None
    return dict(MEMORY_REGISTRY.get(memory_type, {}))
