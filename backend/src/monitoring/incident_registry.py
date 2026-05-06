"""
MONITORING: incident_registry
PURPOSE: Store incidents in PostgreSQL; avoid duplicate alerts; update occurrence counts; mark resolved
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _get_db():
    from src.db.base import SessionLocal
    return SessionLocal()


async def register_incident(
    cluster_id: str,
    title: str,
    root_cause: str,
    severity: str,
    affected_components: List[str],
    occurrence_count: int,
    summary: str,
    error_type: str,
    technical_summary: Optional[str] = None,
    suggested_next_step: Optional[str] = None,
    likely_files: Optional[List[str]] = None,
    sample_events: Optional[List[Dict[str, Any]]] = None,
    affected_endpoint: Optional[str] = None,
    affected_workflow: Optional[str] = None,
    request_ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Create or update incident. Returns incident dict with incident_id, is_new, existing.
    """
    db = _get_db()
    try:
        from src.monitoring.models.incident import Incident
        from src.monitoring.models.incident_event import IncidentEvent
        now = datetime.now(timezone.utc)
        ***REMOVED*** Find existing open incident for same cluster/signature
        existing = db.query(Incident).filter(
            Incident.cluster_id == cluster_id,
            Incident.status.in_(["open", "acknowledged"]),
        ).first()
        if existing:
            existing.last_seen_at = now
            existing.occurrence_count = (existing.occurrence_count or 0) + occurrence_count
            existing.updated_at = now
            if severity and severity != existing.severity:
                existing.severity = severity
            if affected_endpoint:
                existing.affected_endpoint = affected_endpoint
            if affected_workflow:
                existing.affected_workflow = affected_workflow
            if request_ids:
                existing.request_ids = ((existing.request_ids or []) + request_ids)[:20]
            db.commit()
            db.refresh(existing)
            ev = existing
            out = {
                "incident_id": ev.incident_id,
                "title": ev.title,
                "severity": ev.severity,
                "status": ev.status,
                "occurrence_count": ev.occurrence_count,
                "is_new": False,
                "existing": True,
            }
            if sample_events:
                for se in sample_events[:3]:
                    db.add(IncidentEvent(
                        incident_id=ev.incident_id,
                        event_message=se.get("error_message"),
                        module=se.get("module"),
                        endpoint=se.get("endpoint"),
                        request_id=se.get("request_id"),
                        raw_payload=se,
                    ))
                db.commit()
            return out
        incident_id = f"inc_{uuid.uuid4().hex[:12]}"
        db.add(Incident(
            incident_id=incident_id,
            title=title,
            root_cause=root_cause,
            severity=severity,
            status="open",
            first_seen_at=now,
            last_seen_at=now,
            affected_components=affected_components,
            occurrence_count=occurrence_count,
            summary=summary,
            error_type=error_type,
            cluster_id=cluster_id,
            technical_summary=technical_summary,
            suggested_next_step=suggested_next_step,
            likely_files=likely_files,
            affected_endpoint=affected_endpoint,
            affected_workflow=affected_workflow,
            request_ids=request_ids[:20] if request_ids else None,
        ))
        db.commit()
        if sample_events:
            for se in sample_events[:5]:
                db.add(IncidentEvent(
                    incident_id=incident_id,
                    event_message=se.get("error_message"),
                    module=se.get("module"),
                    endpoint=se.get("endpoint"),
                    request_id=se.get("request_id"),
                    raw_payload=se,
                ))
            db.commit()
        return {"incident_id": incident_id, "title": title, "severity": severity, "status": "open", "occurrence_count": occurrence_count, "is_new": True, "existing": False}
    except Exception as e:
        logger.exception("register_incident failed: %s", e)
        db.rollback()
        return {"incident_id": None, "is_new": False, "existing": False, "error": str(e)}
    finally:
        db.close()


async def get_incident_by_cluster(cluster_id: str) -> Optional[Dict[str, Any]]:
    """Return existing open/acknowledged incident for cluster if any."""
    db = _get_db()
    try:
        from src.monitoring.models.incident import Incident
        inc = db.query(Incident).filter(Incident.cluster_id == cluster_id, Incident.status.in_(["open", "acknowledged"])).first()
        if not inc:
            return None
        return {
            "incident_id": inc.incident_id,
            "severity": inc.severity,
            "status": inc.status,
            "occurrence_count": inc.occurrence_count,
            "first_seen_at": inc.first_seen_at.isoformat() if inc.first_seen_at else None,
            "last_seen_at": inc.last_seen_at.isoformat() if inc.last_seen_at else None,
        }
    finally:
        db.close()


async def list_incidents(limit: int = 50, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """List incidents from DB."""
    db = _get_db()
    try:
        from src.monitoring.models.incident import Incident
        q = db.query(Incident).order_by(Incident.last_seen_at.desc()).limit(limit)
        if status:
            q = q.filter(Incident.status == status)
        rows = q.all()
        return [
            {
                "incident_id": r.incident_id,
                "title": r.title,
                "root_cause": r.root_cause,
                "severity": r.severity,
                "status": r.status,
                "first_seen_at": r.first_seen_at.isoformat() if r.first_seen_at else None,
                "last_seen_at": r.last_seen_at.isoformat() if r.last_seen_at else None,
                "affected_components": r.affected_components,
                "occurrence_count": r.occurrence_count,
                "error_type": r.error_type,
                "affected_endpoint": getattr(r, "affected_endpoint", None),
                "affected_workflow": getattr(r, "affected_workflow", None),
            }
            for r in rows
        ]
    finally:
        db.close()


async def get_incident(incident_id: str) -> Optional[Dict[str, Any]]:
    """Get one incident by incident_id."""
    db = _get_db()
    try:
        from src.monitoring.models.incident import Incident
        from src.monitoring.models.incident_event import IncidentEvent
        inc = db.query(Incident).filter(Incident.incident_id == incident_id).first()
        if not inc:
            return None
        events = db.query(IncidentEvent).filter(IncidentEvent.incident_id == incident_id).order_by(IncidentEvent.created_at.desc()).limit(20).all()
        return {
            "incident_id": inc.incident_id,
            "title": inc.title,
            "root_cause": inc.root_cause,
            "severity": inc.severity,
            "status": inc.status,
            "first_seen_at": inc.first_seen_at.isoformat() if inc.first_seen_at else None,
            "last_seen_at": inc.last_seen_at.isoformat() if inc.last_seen_at else None,
            "affected_components": inc.affected_components,
            "occurrence_count": inc.occurrence_count,
            "summary": inc.summary,
            "error_type": inc.error_type,
            "technical_summary": inc.technical_summary,
            "suggested_next_step": inc.suggested_next_step,
            "likely_files": inc.likely_files,
            "affected_endpoint": getattr(inc, "affected_endpoint", None),
            "affected_workflow": getattr(inc, "affected_workflow", None),
            "request_ids": getattr(inc, "request_ids", None),
            "events": [{"event_message": e.event_message, "module": e.module, "endpoint": e.endpoint, "request_id": e.request_id, "created_at": e.created_at.isoformat() if e.created_at else None} for e in events],
        }
    finally:
        db.close()
