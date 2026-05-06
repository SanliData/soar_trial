"""
MODULE: runtime_access_policy
PURPOSE: Least-privilege access policy metadata (fail-closed) (H-049)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def build_access_policy(*, identity_id: str, workflow_scope: str, capability_scope: list[str]) -> dict[str, Any]:
    """
    Foundation policy metadata only. Fail-closed: unknown scopes should not be treated as allowed.
    """
    iid = (identity_id or "").strip()
    wf = (workflow_scope or "").strip()
    caps = sorted([c.strip() for c in (capability_scope or []) if c and str(c).strip()])
    return {
        "identity_id": iid,
        "connector_access": {"allowed": ["uploaded_documents", "procurement_feed"], "deterministic": True},
        "workflow_access": {"allowed": [wf], "default": "deny", "deterministic": True},
        "retrieval_limits": {"max_results": 10, "max_connectors": 3, "deterministic": True},
        "runtime_budget_limits": {"max_tokens": 24000, "max_retries": 2, "deterministic": True},
        "mcp_endpoint_access": {"allowed": ["mcp-gw-projection-only"], "unrestricted": False, "deterministic": True},
        "escalation_permissions": {"allowed": ["request_human_review"], "self_authorize": False, "deterministic": True},
        "capability_scope": caps,
        "least_privilege": True,
        "fail_closed": True,
        "deterministic": True,
    }


def export_runtime_access_policies() -> dict[str, Any]:
    return {"policies": [build_access_policy(identity_id="id-001", workflow_scope="procurement_analysis", capability_scope=["results.opportunities"])], "deterministic": True}

