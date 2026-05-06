"""
MONITORING: monitoring_agent orchestrator
PURPOSE: Ingest -> cluster -> root cause -> severity -> check registry -> notify -> store run
"""
import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from src.monitoring.log_ingestor import ingest_logs
from src.monitoring.error_clusterer import cluster_errors
from src.monitoring.severity_classifier import classify_severity
from src.monitoring.root_cause_analyzer import analyze_root_cause
from src.monitoring.github_context_finder import find_likely_files
from src.monitoring.incident_registry import register_incident, get_incident_by_cluster
from src.monitoring.notification_service import send_alert, should_notify

logger = logging.getLogger(__name__)


async def run_monitoring_agent(
    log_paths: Optional[List[str]] = None,
    max_events: int = 1000,
    use_openai_root_cause: bool = False,
) -> Dict[str, Any]:
    """
    Full pipeline: ingest logs -> cluster -> for each cluster: root cause, severity,
    check registry -> register incident -> notify if new or escalation -> store monitoring run.
    Returns monitoring_run_id, events_ingested, clusters_created, new_incidents, alerts_sent.
    """
    run_id = f"run_{uuid.uuid4().hex[:12]}"
    t0 = time.perf_counter()
    events_ingested = 0
    clusters_created = 0
    new_incidents = 0
    alerts_sent = 0
    failures = 0

    try:
        # 1. Ingest
        events = await ingest_logs(log_paths=log_paths, max_events=max_events)
        events_ingested = len(events)
        if not events:
            duration_ms = int((time.perf_counter() - t0) * 1000)
            await _save_monitoring_run(run_id, events_ingested, 0, 0, 0, duration_ms, failures, {})
            return {
                "monitoring_run_id": run_id,
                "events_ingested": events_ingested,
                "clusters_created": 0,
                "new_incidents": 0,
                "alerts_sent": 0,
                "analysis_duration_ms": duration_ms,
            }

        # 2. Cluster
        clusters = await cluster_errors(events)
        clusters_created = len(clusters)

        for cluster in clusters:
            try:
                # 3. Root cause
                rca = await analyze_root_cause(cluster, use_openai=use_openai_root_cause)
                # 4. Severity
                sev = await classify_severity(cluster, clusters)
                # 5. Likely files
                files = find_likely_files(cluster, cluster.get("sample_errors"))
                likely_files = files.get("likely_files", [])
                # 6. Check registry
                existing = await get_incident_by_cluster(cluster["cluster_id"])
                title = f"{cluster.get('error_type', 'error')} affecting {', '.join((cluster.get('affected_components') or [])[:3])}"
                if not title.strip():
                    title = cluster.get("error_type", "Unknown incident")
                request_ids = list({e.get("request_id") for e in (cluster.get("sample_errors") or []) if e.get("request_id")})[:10]
                affected_endpoint = cluster.get("affected_endpoint")
                affected_workflow = cluster.get("affected_workflow")
                first_ts = None
                last_ts = None
                for e in cluster.get("sample_errors") or []:
                    t = e.get("timestamp")
                    if t:
                        first_ts = min(first_ts, t) if first_ts else t
                        last_ts = max(last_ts, t) if last_ts else t
                # 7. Register
                reg = await register_incident(
                    cluster_id=cluster["cluster_id"],
                    title=title,
                    root_cause=rca.get("root_cause", ""),
                    severity=sev.get("severity", "S3"),
                    affected_components=cluster.get("affected_components", []),
                    occurrence_count=cluster.get("count", 0),
                    summary=rca.get("technical_summary", ""),
                    error_type=cluster.get("error_type", "unknown"),
                    technical_summary=rca.get("technical_summary"),
                    suggested_next_step=rca.get("suggested_next_step"),
                    likely_files=likely_files,
                    sample_events=cluster.get("sample_errors"),
                    affected_endpoint=affected_endpoint,
                    affected_workflow=affected_workflow,
                    request_ids=request_ids or None,
                )
                if reg.get("is_new"):
                    new_incidents += 1
                alert_status = "new" if reg.get("is_new") else ("escalated" if existing and sev.get("severity") != (existing.get("severity")) else "recurring")
                incident_payload = {
                    "incident_id": reg.get("incident_id"),
                    "title": title,
                    "severity": sev.get("severity"),
                    "root_cause": rca.get("root_cause"),
                    "suggested_next_step": rca.get("suggested_next_step"),
                    "affected_components": cluster.get("affected_components"),
                    "occurrence_count": cluster.get("count"),
                    "affected_endpoint": affected_endpoint,
                    "affected_workflow": affected_workflow,
                    "first_seen_at": existing.get("first_seen_at") if existing else (first_ts.isoformat() if hasattr(first_ts, "isoformat") else str(first_ts) if first_ts else None),
                    "last_seen_at": existing.get("last_seen_at") if existing else (last_ts.isoformat() if hasattr(last_ts, "isoformat") else str(last_ts) if last_ts else None),
                    "alert_status": alert_status,
                }
                # 8. Notify if new or escalation
                if await should_notify(reg.get("incident_id", ""), sev.get("severity", "S3"), existing):
                    alert_result = await send_alert(
                        incident_payload,
                        likely_files=likely_files,
                        suppress_duplicate=not reg.get("is_new"),
                        previous_severity=existing.get("severity") if existing else None,
                    )
                    if alert_result.get("sent"):
                        alerts_sent += 1
            except Exception as e:
                failures += 1
                logger.warning("monitoring_agent cluster processing failed: %s", e)

        duration_ms = int((time.perf_counter() - t0) * 1000)
        await _save_monitoring_run(
            run_id,
            events_ingested,
            clusters_created,
            new_incidents,
            alerts_sent,
            duration_ms,
            failures,
            {"log_paths": log_paths},
        )
        return {
            "monitoring_run_id": run_id,
            "events_ingested": events_ingested,
            "clusters_created": clusters_created,
            "new_incidents": new_incidents,
            "alerts_sent": alerts_sent,
            "analysis_duration_ms": duration_ms,
            "failures_in_monitoring_pipeline": failures,
        }
    except Exception as e:
        failures += 1
        logger.exception("monitoring_agent run failed: %s", e)
        duration_ms = int((time.perf_counter() - t0) * 1000)
        await _save_monitoring_run(run_id, events_ingested, clusters_created, new_incidents, alerts_sent, duration_ms, failures, {"error": str(e)})
        return {
            "monitoring_run_id": run_id,
            "events_ingested": events_ingested,
            "clusters_created": clusters_created,
            "new_incidents": new_incidents,
            "alerts_sent": alerts_sent,
            "analysis_duration_ms": duration_ms,
            "failures_in_monitoring_pipeline": failures,
            "error": str(e),
        }


async def _save_monitoring_run(
    monitoring_run_id: str,
    events_ingested: int,
    clusters_created: int,
    new_incidents: int,
    alerts_sent: int,
    analysis_duration_ms: int,
    failures: int,
    payload: Dict[str, Any],
) -> None:
    try:
        from src.monitoring.models.monitoring_run import MonitoringRun
        from src.db.base import SessionLocal
        db = SessionLocal()
        try:
            db.add(MonitoringRun(
                monitoring_run_id=monitoring_run_id,
                events_ingested=events_ingested,
                clusters_created=clusters_created,
                new_incidents=new_incidents,
                alerts_sent=alerts_sent,
                analysis_duration_ms=analysis_duration_ms,
                failures_in_monitoring_pipeline=failures,
                payload=payload,
            ))
            db.commit()
        finally:
            db.close()
    except Exception as e:
        logger.debug("_save_monitoring_run: %s", e)
