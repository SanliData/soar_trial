"""
MODULE: project_memory_service
PURPOSE: Scoped operational memory manifest — bounded, auditable, no unrestricted persistence (H-038)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_MAX_ENTRIES_PER_TYPE = 50

_PROJECT_MEMORY_ENTRIES: dict[str, list[dict[str, Any]]] = {
    "workflow_patterns": [
        {
            "entry_id": "wm-wf-001",
            "summary": "Validated opportunity ranking checklist (read-only catalogue).",
            "visibility": "workspace_scoped",
            "permission_gate": "execution_permissions_intersection",
        },
    ],
    "operational_notes": [
        {
            "entry_id": "wm-op-001",
            "summary": "Escalation path for ambiguous contractor identity signals.",
            "visibility": "project_lead_only",
            "permission_gate": "explicit_grant",
        },
    ],
    "orchestration_context": [
        {
            "entry_id": "wm-orch-001",
            "summary": "Last known capability graph shard ids for briefing (non-secret).",
            "visibility": "session_ttl",
            "permission_gate": "workspace_policy",
        },
    ],
    "evaluation_patterns": [
        {
            "entry_id": "wm-eval-001",
            "summary": "Fail-closed thresholds for acceptance checklist coverage.",
            "visibility": "workspace_scoped",
            "permission_gate": "evaluation_role",
        },
    ],
    "project_constraints": [
        {
            "entry_id": "wm-prj-001",
            "summary": "Hard cap: memory entries cannot replicate full document corpora.",
            "visibility": "workspace_scoped",
            "permission_gate": "architecture_contract",
        },
    ],
}


def export_project_memory_manifest() -> dict[str, Any]:
    sanitized: dict[str, list[dict[str, Any]]] = {}
    for k in sorted(_PROJECT_MEMORY_ENTRIES.keys()):
        slice_ = list(_PROJECT_MEMORY_ENTRIES[k][: _MAX_ENTRIES_PER_TYPE])
        sanitized[k] = slice_
    return {
        "memory_by_type": sanitized,
        "unrestricted_persistent_memory": False,
        "audit_required_default": True,
        "scoped_only": True,
        "cap_per_type": _MAX_ENTRIES_PER_TYPE,
    }
