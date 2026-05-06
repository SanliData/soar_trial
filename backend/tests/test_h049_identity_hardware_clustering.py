from __future__ import annotations


def test_identity_registry_deterministic():
    from src.agentic_identity.agent_identity_registry import export_identity_registry

    a = export_identity_registry(limit=50)
    b = export_identity_registry(limit=50)
    assert a == b
    assert a["identities"][0]["identity_lineage"]["issued_by"]


def test_shadow_agent_detection_deterministic():
    from src.agentic_identity.shadow_agent_detection import export_shadow_agent_detection

    a = export_shadow_agent_detection()
    b = export_shadow_agent_detection()
    assert a == b
    assert a["detection_only"] is True


def test_mcp_governance_deterministic_and_restricted():
    from src.agentic_identity.mcp_endpoint_governance import export_mcp_endpoint_governance

    a = export_mcp_endpoint_governance()
    b = export_mcp_endpoint_governance()
    assert a == b
    assert a["mcp_endpoints"][0]["unrestricted_mcp_endpoint_exposure"] is False


def test_hardware_routing_deterministic():
    from src.hardware_aware_runtime.runtime_hardware_router import export_hardware_routing, route_workload

    a = export_hardware_routing()
    b = export_hardware_routing()
    assert a == b
    r = route_workload(workload="retrieval")
    assert r["recommendation_only"] is True


def test_hardware_costs_deterministic():
    from src.hardware_aware_runtime.hardware_cost_service import export_hardware_costs

    a = export_hardware_costs()
    b = export_hardware_costs()
    assert a == b
    assert "token_per_cost_efficiency" in a["hardware_costs"][0]


def test_cluster_utility_and_variance_deterministic():
    from src.adaptive_clustering.cluster_utility_service import export_cluster_utility
    from src.adaptive_clustering.cluster_variance_service import export_cluster_variance

    a = export_cluster_utility()
    b = export_cluster_utility()
    assert a == b
    v1 = export_cluster_variance()
    v2 = export_cluster_variance()
    assert v1 == v2

