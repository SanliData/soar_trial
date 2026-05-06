"""
MODULE: scheduled_execution_service
PURPOSE: Governed recurring workloads — bounded execution (H-042)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_SCHEDULES: list[dict[str, Any]] = [
    {
        "schedule_id": "sch-procurement-poll",
        "description": "Procurement catalog staleness polling",
        "cadence": "cron:0 */6 * * *",
        "max_runs_per_day": 4,
        "max_runtime_seconds_per_run": 300,
        "autonomous_infinite_execution": False,
        "explicit_boundary": "single_pass_then_exit",
        "examples_domain": "procurement",
    },
    {
        "schedule_id": "sch-permit-monitor",
        "description": "Permit status reconciliation",
        "cadence": "cron:30 */4 * * *",
        "max_runs_per_day": 6,
        "max_runtime_seconds_per_run": 420,
        "autonomous_infinite_execution": False,
        "explicit_boundary": "bounded_batch_pull",
        "examples_domain": "permits",
    },
    {
        "schedule_id": "sch-contractor-review",
        "description": "Contractor credential windows review",
        "cadence": "cron:15 8 * * 1",
        "max_runs_per_day": 1,
        "max_runtime_seconds_per_run": 900,
        "autonomous_infinite_execution": False,
        "explicit_boundary": "checkpoint_after_each_contractor_slice",
        "examples_domain": "contractors",
    },
    {
        "schedule_id": "sch-municipal-feed",
        "description": "Municipal bulletin delta ingest",
        "cadence": "cron:0 7,15 * * *",
        "max_runs_per_day": 2,
        "max_runtime_seconds_per_run": 600,
        "autonomous_infinite_execution": False,
        "explicit_boundary": "timeboxed_fetch",
        "examples_domain": "municipal",
    },
]


def export_scheduled_execution_manifest() -> dict[str, Any]:
    return {
        "schedules": [dict(s) for s in _SCHEDULES],
        "governed_scheduling_only": True,
        "deterministic": True,
    }
