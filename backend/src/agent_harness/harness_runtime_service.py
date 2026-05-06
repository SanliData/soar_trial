"""
MODULE: harness_runtime_service
PURPOSE: Modular harness runtime aggregation — deterministic only (H-031)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.agent_harness.evaluation_router import list_routes
from src.agent_harness.memory_registry import MEMORY_TYPES, export_memory_manifest
from src.agent_harness.protocol_registry import PROTOCOL_TYPES, export_protocols_manifest
from src.agent_harness.skill_registry import SKILL_REGISTRY, export_skills_manifest


def get_active_skills() -> dict[str, Any]:
    return export_skills_manifest()


def get_protocols() -> dict[str, Any]:
    return export_protocols_manifest()


def get_runtime_memory() -> dict[str, Any]:
    return export_memory_manifest()


def generate_runtime_summary() -> dict[str, Any]:
    return {
        "memory_types": sorted(MEMORY_TYPES),
        "skill_ids": sorted(SKILL_REGISTRY.keys()),
        "protocol_types": sorted(PROTOCOL_TYPES),
        "evaluation_routes": list_routes().get("routes"),
        "modular_layers": ["memory", "skills", "protocols", "evaluation_routing", "compression"],
        "orchestration_mode": "harness_foundation_v1",
    }
