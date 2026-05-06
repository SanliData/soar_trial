"""
MODULE: runtime_anomaly_alignment_service
PURPOSE: H-039 + H-041 alignment — runtime anomaly detection signals (detection only)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_runtime_anomaly_alignment_manifest() -> dict[str, Any]:
    """
    Firewall-aligned patterns for inference instability. No autonomous blocking here.
    """
    return {
        "h041_inference_runtime_alignment": True,
        "h043_private_runtime_exposure_alignment": True,
        "firewall_aware_detections": [
            {
                "id": "token_explosion",
                "description": "Sustained input token rate or context size beyond governed budgets.",
                "signal_source": "inference_runtime.telemetry",
                "autonomous_blocking": False,
            },
            {
                "id": "retry_storm",
                "description": "Windowed retry counts exceed collapse detection thresholds.",
                "signal_source": "inference_runtime.collapse_risk",
                "autonomous_blocking": False,
            },
            {
                "id": "orchestration_flood",
                "description": "Invocation rate exceeds governed RPS hints for depth-limited orchestration.",
                "signal_source": "inference_runtime.collapse_risk",
                "autonomous_blocking": False,
            },
            {
                "id": "unsafe_parallelism_spike",
                "description": "Active parallel workflows/tokens exceed parallelism governance caps.",
                "signal_source": "inference_runtime.parallelism",
                "autonomous_blocking": False,
            },
            {
                "id": "unsafe_public_runtime_exposure",
                "description": "Runtime listeners or routes suggest public AI runtime or inference bind.",
                "signal_source": "private_runtime_security.network_exposure",
                "autonomous_blocking": False,
            },
            {
                "id": "unrestricted_ingress_path",
                "description": "Operational mesh allows unrestricted ingress inconsistent with private runtime policy.",
                "signal_source": "private_runtime_security.private_mesh",
                "autonomous_blocking": False,
            },
            {
                "id": "external_execution_escalation",
                "description": "Tooling or gateways indicate external execution escalation surfaces.",
                "signal_source": "private_runtime_security.execution_boundary",
                "autonomous_blocking": False,
            },
            {
                "id": "insecure_mesh_access",
                "description": "Overlay trust posture fails trusted-path requirements.",
                "signal_source": "private_runtime_security.tailscale_policy",
                "autonomous_blocking": False,
            },
        ],
        "detection_only": True,
        "policy_enforcement_remains_explicit": True,
        "deterministic": True,
    }
