"""
CORE: upap/gates
PURPOSE: Single entry point for all UPAP gates. Fail-fast on any gate FAIL.
ENCODING: UTF-8 WITHOUT BOM

run_upap_gates(stage, trace_id, run_id, query_id, query_params, leads)
  -> (leads_filtered, upap_evidence, gate_status)

Acontext: Observability + replay layer. Gate decisions sent to Acontext after each decision.
PII redacted before sending. UPAP gates remain authoritative; Acontext is secondary.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

from src.core.upap.regulated import is_regulated_domain, require_simulation_mode
from src.core.upap.decision_maker import infer_role, infer_decision_maker_persona, ALLOWED_ROLES
from src.core.upap.cross_channel import recommend, ALLOWED_CHANNELS
from src.core.upap.audit import emit_upap_gate_event
from src.core.upap.evidence import write_upap_evidence, EVIDENCE_BASE_DIR
from src.core.upap.policy import get_limits_from_plan
from src.core.upap.enforce import enforce
from src.core.upap.verify import run_verification_gate
from src.core.upap_limits import COMPANY_LIMIT, COMPANY_SIZE_MAX

Stage = Literal["INGEST", "ENRICH", "EXPORT"]


def _emit_acontext_gate(
    trace_id: str,
    run_id: str,
    query_id: str,
    gate_name: str,
    status: Literal["PASS", "FAIL"],
    reason: Optional[str],
    limits: Optional[Dict[str, Any]],
    timestamp: str,
    evidence: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Emit gate result to Acontext (observability). Fire-and-forget, best-effort.
    If FAIL: store full structured evidence but redact PII before sending.
    """
    try:
        from src.integrations.acontext_client import get_session_id_from_trace, store_event_sync
        from src.security.context_guard import extract_tenant_from_context
        from src.security.pii_redactor import redact_payload

        tenant_id = extract_tenant_from_context(query_id=query_id)
        session_id = get_session_id_from_trace(trace_id, run_id)
        payload: Dict[str, Any] = {
            "gate_name": gate_name,
            "status": status,
            "reason": reason or "ok",
            "trace_id": trace_id,
            "run_id": run_id,
            "query_id": query_id,
            "timestamp": timestamp,
            "limits": limits or {},
        }
        if status == "FAIL" and evidence:
            payload["evidence"] = redact_payload(evidence)
        store_event_sync(
            session_id=session_id,
            tenant_id=tenant_id,
            event_type="UPAP_GATE_RESULT",
            payload=payload,
            lead_id=None,
        )
    except Exception:   # noqa: BLE001 - best-effort, do not break gates
        pass


def run_upap_gates(
    stage: Stage,
    trace_id: str,
    run_id: str,
    query_id: str,
    query_params: Dict[str, Any],
    leads: List[Dict[str, Any]],
    evidence_dir: Optional[Path] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any], Literal["PASS", "FAIL"]]:
    """
    Run all UPAP gates for the given stage. Fail-fast on any FAIL.
    Returns (leads_filtered, upap_evidence, gate_status).
    """
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    limits = get_limits_from_plan(query_params)
    evidence: Dict[str, Any] = {
        "trace_id": trace_id,
        "run_id": run_id,
        "query_id": query_id,
        "timestamp": ts,
        "stage": stage,
        "regulated_domain": False,
        "simulation_mode": None,
        "blocked_reason": None,
        "limits": limits,
        "rows_before": len(leads),
        "rows_after": 0,
        "rejected_counts": {},
        "decision_maker_summary": {},
        "channel_summary": {},
        "status": "PASS",
        "reason": None,
    }
    current_leads = list(leads)

    # ----- A) Regulated / Simulation gate -----
    regulated = is_regulated_domain(query_params)
    simulation_mode = query_params.get("simulation_mode")
    if simulation_mode is not None and not isinstance(simulation_mode, bool):
        try:
            simulation_mode = bool(simulation_mode)
        except Exception:
            simulation_mode = None
    reg_result = require_simulation_mode(regulated, simulation_mode, current_leads)
    evidence["regulated_domain"] = reg_result.regulated_domain
    evidence["simulation_mode"] = reg_result.simulation_mode
    evidence["blocked_reason"] = reg_result.blocked_reason
    if reg_result.blocked_count:
        evidence["rejected_counts"]["regulated_real_company"] = reg_result.blocked_count

    if not reg_result.passed:
        evidence["status"] = "FAIL"
        evidence["reason"] = reg_result.reason
        evidence["rows_after"] = 0
        emit_upap_gate_event(
            "upap_gate_fail",
            "regulated_simulation",
            trace_id, run_id, query_id,
            status="FAIL",
            reason=reg_result.reason,
            limits=evidence["limits"],
            timestamp=ts,
        )
        _emit_acontext_gate(trace_id, run_id, query_id, "regulated_simulation", "FAIL", reg_result.reason, limits, ts, evidence)
        return (current_leads, evidence, "FAIL")

    emit_upap_gate_event(
        "upap_gate_pass",
        "regulated_simulation",
        trace_id, run_id, query_id,
        status="PASS",
        reason=reg_result.reason,
        limits=evidence["limits"],
        timestamp=ts,
    )
    _emit_acontext_gate(trace_id, run_id, query_id, "regulated_simulation", "PASS", reg_result.reason, limits, ts, None)

    # ----- C) Decision maker resolution (enrich each lead) -----
    keyword_intent = (query_params.get("product_service") or query_params.get("keyword_intent") or "").strip()
    geo_confidence = 0.5
    if query_params.get("geography") or query_params.get("address"):
        geo_confidence = 0.7

    for lead in current_leads:
        title = lead.get("persona_role") or lead.get("Persona Role") or lead.get("job_title") or ""
        dept = lead.get("department") or lead.get("dept") or ""
        persona = infer_decision_maker_persona(title=title, dept=dept, keyword_intent=keyword_intent)
        lead["decision_maker_role"] = persona["role"]
        lead["decision_confidence_score"] = persona["decision_maker_confidence"]
        lead["authority_level"] = persona["authority_level"]
        lead["department"] = persona["department"]
        lead["decision_type"] = persona["decision_type"]
        lead["accessibility_score"] = persona["accessibility_score"]
        lead["decision_maker_confidence"] = persona["decision_maker_confidence"]
        lead["is_decision_maker"] = persona["is_decision_maker"]

    # Check no lead missing role/confidence or invalid role/channel
    missing_role = [
        i for i, L in enumerate(current_leads)
        if not L.get("decision_maker_role")
        or L.get("decision_confidence_score") is None
        or L.get("decision_maker_role") not in ALLOWED_ROLES
    ]
    if missing_role:
        evidence["status"] = "FAIL"
        evidence["reason"] = "missing_decision_maker"
        evidence["rejected_counts"]["missing_role"] = len(missing_role)
        evidence["rows_after"] = 0
        emit_upap_gate_event(
            "upap_gate_fail",
            "decision_maker",
            trace_id, run_id, query_id,
            status="FAIL",
            reason="missing_decision_maker",
            limits=evidence["limits"],
            timestamp=ts,
        )
        _emit_acontext_gate(trace_id, run_id, query_id, "decision_maker", "FAIL", "missing_decision_maker", limits, ts, evidence)
        return (current_leads, evidence, "FAIL")

    roles_summary: Dict[str, int] = {}
    for L in current_leads:
        r = L.get("decision_maker_role") or "unknown"
        roles_summary[r] = roles_summary.get(r, 0) + 1
    evidence["decision_maker_summary"] = roles_summary
    emit_upap_gate_event(
        "upap_gate_pass",
        "decision_maker",
        trace_id, run_id, query_id,
        status="PASS",
        reason="ok",
        limits=evidence["limits"],
        timestamp=ts,
    )
    _emit_acontext_gate(trace_id, run_id, query_id, "decision_maker", "PASS", "ok", limits, ts, None)

    # ----- D) Cross-channel recommendation (enrich each lead) -----
    for lead in current_leads:
        role_score = lead.get("decision_confidence_score") or 0.5
        rec = recommend(keyword_intent=keyword_intent, geo_confidence=geo_confidence, role_score=role_score)
        lead["channel_recommendation"] = rec.get("channel_recommendation")
        lead["channel_rule_id"] = rec.get("rule_id")
        if rec.get("sequence"):
            lead["channel_sequence"] = rec["sequence"]

    missing_channel = [
        i for i, L in enumerate(current_leads)
        if not L.get("channel_recommendation")
        or not L.get("channel_rule_id")
        or L.get("channel_recommendation") not in ALLOWED_CHANNELS
    ]
    if missing_channel:
        evidence["status"] = "FAIL"
        evidence["reason"] = "missing_channel_recommendation"
        evidence["rejected_counts"]["missing_channel"] = len(missing_channel)
        evidence["rows_after"] = 0
        emit_upap_gate_event(
            "upap_gate_fail",
            "cross_channel",
            trace_id, run_id, query_id,
            status="FAIL",
            reason="missing_channel_recommendation",
            limits=evidence["limits"],
            timestamp=ts,
        )
        _emit_acontext_gate(trace_id, run_id, query_id, "cross_channel", "FAIL", "missing_channel_recommendation", limits, ts, evidence)
        return (current_leads, evidence, "FAIL")

    channel_summary: Dict[str, int] = {}
    for L in current_leads:
        ch = L.get("channel_recommendation") or "unknown"
        channel_summary[ch] = channel_summary.get(ch, 0) + 1
    evidence["channel_summary"] = channel_summary
    emit_upap_gate_event(
        "upap_gate_pass",
        "cross_channel",
        trace_id, run_id, query_id,
        status="PASS",
        reason="ok",
        limits=evidence["limits"],
        timestamp=ts,
    )
    _emit_acontext_gate(trace_id, run_id, query_id, "cross_channel", "PASS", "ok", limits, ts, None)

    # ----- B) Hard filters via enforce (EXPORT only); then verification gate -----
    if stage == "EXPORT":
        current_leads, dropped_leads, drop_histogram, audit_info = enforce(
            current_leads, trace_id, run_id, query_id, query_params, "EXPORT",
        )
        evidence["rows_after"] = len(current_leads)
        evidence["rejected_counts"].update(drop_histogram)
        evidence["totals_scanned"] = audit_info.get("totals_scanned", len(leads))
        evidence["totals_kept"] = len(current_leads)
        evidence["totals_dropped"] = len(dropped_leads)
        evidence["drop_reasons"] = drop_histogram

        if len(current_leads) == 0:
            evidence["status"] = "FAIL"
            evidence["reason"] = "no_rows_after_upap_filters"
            emit_upap_gate_event(
                "upap_gate_fail",
                "hard_filters",
                trace_id, run_id, query_id,
                status="FAIL",
                reason=evidence["reason"],
                limits=evidence["limits"],
                timestamp=ts,
            )
            _emit_acontext_gate(trace_id, run_id, query_id, "hard_filters", "FAIL", evidence["reason"], limits, ts, evidence)
            return (current_leads, evidence, "FAIL")

        # Verification gate: min_ready_leads
        v_status, v_report, v_path = run_verification_gate(
            query_id, run_id, current_leads, drop_histogram, query_params,
            totals_scanned=audit_info.get("totals_scanned", len(leads)),
            evidence_dir=evidence_dir or EVIDENCE_BASE_DIR,
        )
        if v_status == "FAIL":
            evidence["status"] = "FAIL"
            evidence["reason"] = v_report.get("reason") or "verification_gate_fail"
            evidence["verification_report"] = v_report
            emit_upap_gate_event(
                "upap_gate_fail",
                "verification_gate",
                trace_id, run_id, query_id,
                status="FAIL",
                reason=evidence["reason"],
                limits=evidence["limits"],
                timestamp=ts,
            )
            _emit_acontext_gate(trace_id, run_id, query_id, "verification_gate", "FAIL", evidence["reason"], limits, ts, evidence)
            return (current_leads, evidence, "FAIL")

        emit_upap_gate_event(
            "upap_gate_pass",
            "hard_filters",
            trace_id, run_id, query_id,
            status="PASS",
            reason="ok",
            limits=evidence["limits"],
            timestamp=ts,
        )
        _emit_acontext_gate(trace_id, run_id, query_id, "hard_filters", "PASS", "ok", limits, ts, None)

    if stage != "EXPORT":
        evidence["rows_after"] = len(current_leads)

    # ----- E) Write evidence file (EXPORT only) before success -----
    if stage == "EXPORT":
        write_upap_evidence(query_id, run_id, evidence, evidence_dir or EVIDENCE_BASE_DIR)

    return (current_leads, evidence, "PASS")
