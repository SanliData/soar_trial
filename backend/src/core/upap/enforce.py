"""
CORE: upap/enforce
PURPOSE: Hard filter enforcement at discovery, enrichment, export. Drop on violation + audit.
ENCODING: UTF-8 WITHOUT BOM
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from src.core.upap.policy import get_limits_from_plan
from src.core.upap.audit import emit_upap_gate_event
from src.core.upap_limits import _parse_company_size_max

DROP_REASON_SIZE = "company_size_exceeds_max"
DROP_REASON_REGION = "region_filter"
DROP_REASON_CAP = "capped_by_company_limit"


def _passes_region(
    lead: Dict[str, Any],
    allow_list: List[str],
    deny_list: List[str],
) -> bool:
    """True if lead passes region filter. Empty lists = no filter (pass)."""
    if not allow_list and not deny_list:
        return True
    region = (lead.get("country") or lead.get("Country") or lead.get("region") or "").strip().upper()
    if not region:
        return True
    if deny_list and region in [r.upper() for r in deny_list]:
        return False
    if allow_list and region not in [r.upper() for r in allow_list]:
        return False
    return True


def enforce(
    leads: List[Dict[str, Any]],
    trace_id: str,
    run_id: str,
    plan_id: str,
    plan_params: Dict[str, Any],
    stage: str,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, int], Dict[str, Any]]:
    """
    Apply UPAP hard filters. Re-validate at any stage (discovery, enrichment, export).
    Returns (kept_leads, dropped_leads, drop_reasons_histogram, audit_info).
    Kept leads get applied_filters, evidence_sources (if any), verification_status.
    Dropped leads get dropped_reason. No claims without evidence -> verified=false when no evidence_sources.
    """
    limits = get_limits_from_plan(plan_params)
    company_size_max = limits["company_size_max"]
    company_limit = limits["company_limit"]
    allow_list = limits.get("region_allow_list") or []
    deny_list = limits.get("region_deny_list") or []

    drop_histogram: Dict[str, int] = {}
    kept: List[Dict[str, Any]] = []
    dropped: List[Dict[str, Any]] = []

    for lead in leads:
        lead_copy = dict(lead)
        raw_size = lead_copy.get("company_size") or lead_copy.get("Company Size") or ""
        size_val = _parse_company_size_max(raw_size)

        if size_val is not None and size_val > company_size_max:
            lead_copy["dropped_reason"] = DROP_REASON_SIZE
            lead_copy["applied_filters"] = []
            lead_copy["verification_status"] = "dropped"
            lead_copy["evidence_sources"] = lead_copy.get("evidence_sources") or []
            dropped.append(lead_copy)
            drop_histogram[DROP_REASON_SIZE] = drop_histogram.get(DROP_REASON_SIZE, 0) + 1
            continue

        if not _passes_region(lead_copy, allow_list, deny_list):
            lead_copy["dropped_reason"] = DROP_REASON_REGION
            lead_copy["applied_filters"] = []
            lead_copy["verification_status"] = "dropped"
            lead_copy["evidence_sources"] = lead_copy.get("evidence_sources") or []
            dropped.append(lead_copy)
            drop_histogram[DROP_REASON_REGION] = drop_histogram.get(DROP_REASON_REGION, 0) + 1
            continue

        evidence_sources = lead_copy.get("evidence_sources") or []
        lead_copy["applied_filters"] = ["company_size_max", "company_limit", "region"]
        lead_copy["evidence_sources"] = evidence_sources
        lead_copy["verification_status"] = "verified" if evidence_sources else "unverified"
        lead_copy["dropped_reason"] = None
        kept.append(lead_copy)

    ***REMOVED*** Cap at company_limit
    if len(kept) > company_limit:
        excess = kept[company_limit:]
        kept = kept[:company_limit]
        for ex in excess:
            ex["dropped_reason"] = DROP_REASON_CAP
            ex["verification_status"] = "dropped"
            dropped.append(ex)
        drop_histogram[DROP_REASON_CAP] = drop_histogram.get(DROP_REASON_CAP, 0) + len(excess)

    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    audit_info = {
        "trace_id": trace_id,
        "run_id": run_id,
        "plan_id": plan_id,
        "stage": stage,
        "timestamp": ts,
        "limits": limits,
        "totals_scanned": len(leads),
        "totals_kept": len(kept),
        "totals_dropped": len(dropped),
        "drop_reasons": drop_histogram,
    }
    if dropped:
        emit_upap_gate_event(
            "upap_gate_pass",
            "enforce",
            trace_id, run_id, plan_id,
            status="PASS",
            reason="enforced_drops" if dropped else "ok",
            limits=limits,
            timestamp=ts,
        )
    return kept, dropped, drop_histogram, audit_info
