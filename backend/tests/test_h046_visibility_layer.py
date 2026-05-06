from __future__ import annotations


def test_runtime_pressure_deterministic():
    from src.system_visibility.runtime_pressure_service import export_runtime_pressure

    a = export_runtime_pressure()
    b = export_runtime_pressure()
    assert a == b
    assert a["overall"]["level"] in {"healthy", "elevated", "high", "critical"}


def test_connector_freshness_deterministic():
    from src.system_visibility.connector_freshness_service import export_connector_freshness

    a = export_connector_freshness()
    b = export_connector_freshness()
    assert a == b
    assert all(c["status"] in {"healthy", "stale", "degraded", "disconnected"} for c in a["connectors"])


def test_workflow_audit_deterministic():
    from src.system_visibility.workflow_audit_service import export_workflow_audit

    a = export_workflow_audit(workflow_scope="procurement_analysis")
    b = export_workflow_audit(workflow_scope="procurement_analysis")
    assert a == b
    assert a["retrieval_lineage_visible"] is True

