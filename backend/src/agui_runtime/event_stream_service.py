"""
MODULE: event_stream_service
PURPOSE: AG-UI style event stream metadata (foundation) (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.agui_runtime.stream_validation_service import validate_event
from src.agui_runtime.workflow_event_bus import BUS_EPOCH
from src.agentic_identity.cryptographic_identity_service import export_cryptographic_identities
from src.hardware_aware_runtime.runtime_hardware_router import route_workload
from src.adaptive_clustering.runtime_cluster_optimizer import export_runtime_optimization
from src.agentic_identity.mcp_endpoint_governance import export_mcp_endpoint_governance
from src.prompt_cache_governance.cache_breakpoint_service import export_cache_breakpoints
from src.prompt_cache_governance.cache_efficiency_service import export_cache_efficiency
from src.prompt_cache_governance.cache_safe_compression_service import export_cache_safe_compression
from src.prompt_cache_governance.tool_schema_stability_service import export_tool_schema_stability
from src.prompt_cache_governance.model_session_stability_service import export_model_session_stability


def _wrap(*, workflow_id: str, base: dict[str, Any]) -> dict[str, Any]:
    ev = dict(base)
    ev["workflow_lineage"] = {"workflow_id": workflow_id, "sequence": base.get("event_sequence")}
    ev.setdefault("hidden_execution", False)
    ev.setdefault("unrestricted_live_execution", False)
    validate_event(ev)
    return ev


def export_event_stream(*, workflow_id: str = "wf-demo-001") -> dict[str, Any]:
    wid = (workflow_id or "").strip() or "wf-demo-001"
    # Deterministic foundation: do not mutate global bus; emit stable event sequences.
    started = {"workflow_id": wid, "event_sequence": 1, "event_timestamp": BUS_EPOCH, "source_service": "event_stream_service", "risk_level": "low", "metadata_only": True, "deterministic": True}
    retrieval = {"workflow_id": wid, "event_sequence": 2, "event_timestamp": BUS_EPOCH, "source_service": "federated_retrieval", "risk_level": "low", "metadata_only": True, "deterministic": True}
    finished = {"workflow_id": wid, "event_sequence": 3, "event_timestamp": BUS_EPOCH, "source_service": "event_stream_service", "risk_level": "low", "metadata_only": True, "deterministic": True}

    events = [
        _wrap(workflow_id=wid, base={"event_type": "RUN_STARTED", **started}),
        _wrap(workflow_id=wid, base={"event_type": "RETRIEVAL_STARTED", **retrieval}),
        _wrap(workflow_id=wid, base={"event_type": "RUN_FINISHED", **finished}),
    ]
    identity = export_cryptographic_identities()["cryptographic_identities"][0]
    hw = route_workload(workload="retrieval")
    clustering = export_runtime_optimization()
    mcp = export_mcp_endpoint_governance()
    cache_bp = export_cache_breakpoints(session_id="sess-demo-001")["breakpoints"][0]
    cache_eff = export_cache_efficiency()["cache_efficiency"]
    tool_stab = export_tool_schema_stability(session_id="sess-demo-001")
    model_stab = export_model_session_stability(session_id="sess-demo-001")
    compression = export_cache_safe_compression(session_id="sess-demo-001")
    return {
        "workflow_id": wid,
        "events": events,
        "identity_attribution": {"identity_id": identity["identity_id"], "fingerprint": identity["identity_fingerprint"], "deterministic": True},
        "hardware_metadata": hw,
        "cluster_optimization_events": clustering["runtime_optimization"],
        "mcp_governance_events": mcp["mcp_endpoints"],
        "cache_events": [
            {"event_type": "cache_created", "static_prefix_hash": cache_bp["static_prefix_hash"], "deterministic": True},
            {"event_type": "cache_read", "cache_efficiency_ratio": cache_eff["cache_efficiency_ratio"], "deterministic": True},
            {
                "event_type": "cache_invalidated",
                "cache_valid": cache_bp["cache_valid"],
                "invalidation_reason": cache_bp["invalidation_reason"],
                "deterministic": True,
            },
            {"event_type": "cache_safe_compression_started", "static_prefix_preserved": compression["static_prefix_preserved"], "deterministic": True},
            {"event_type": "tool_schema_stability_warning", "cache_reset_warning": tool_stab["cache_reset_warning"], "deterministic": True},
            {"event_type": "model_session_reset_warning", "model_switch_requires_reset": model_stab["model_switch_requires_reset"], "deterministic": True},
        ],
        "deterministic": True,
        "auditable": True,
    }

