"""
MODULE: local_inference_service
PURPOSE: Local-first inference abstraction — metadata only (H-037)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_LOCAL_METADATA: dict[str, Any] = {
    "offline_reasoning_supported": True,
    "local_model_slots": [
        {"slot_id": "ollama-default", "family": "ollama", "execution_mode": "loopback"},
        {"slot_id": "gguf-bundle", "family": "local_llm", "execution_mode": "sandboxed_process"},
    ],
    "restricted_execution_modes": ["loopback", "sandboxed_process"],
    "privacy_aware_routing": True,
    "provider_lock_in_avoidance": "abstraction_metadata_only",
}


def export_local_inference_metadata() -> dict[str, Any]:
    return {
        "local_inference": dict(_LOCAL_METADATA),
        "not_a_runtime_deployer": True,
        "deterministic_manifest": True,
    }
