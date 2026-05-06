"""
ROUTER: monitoring_router (AI DevOps Monitoring Agent)
PURPOSE: GET /monitoring/incidents, GET /monitoring/incidents/{id}, POST /monitoring/run, GET /monitoring/runs
"""
import asyncio
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.monitoring.monitoring_agent import run_monitoring_agent
from src.monitoring.incident_registry import list_incidents, get_incident

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


# ---------- POST /monitoring/run response example ----------
# {
# "monitoring_run_id": "run_001",
# "events_ingested": 243,
# "clusters_created": 7,
# "new_incidents": 2,
# "alerts_sent": 1
# }


class RunMonitoringResponse(BaseModel):
    monitoring_run_id: str
    events_ingested: int = 0
    clusters_created: int = 0
    new_incidents: int = 0
    alerts_sent: int = 0
    analysis_duration_ms: Optional[int] = None
    failures_in_monitoring_pipeline: Optional[int] = None


@router.get("/incidents")
async def get_incidents_list(status: Optional[str] = None, limit: int = 50):
    """List incidents (optional filter by status)."""
    try:
        items = await list_incidents(limit=limit, status=status)
        return {"incidents": items}
    except Exception as e:
        logger.warning("get_incidents_list failed: %s", e)
        raise HTTPException(status_code=503, detail="Incident storage unavailable")


@router.get("/incidents/{incident_id}")
async def get_incident_by_id(incident_id: str):
    """Get one incident with events."""
    inc = await get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc


@router.post("/run", response_model=RunMonitoringResponse)
async def post_run_monitoring():
    """
    Run the monitoring agent manually (ingest -> cluster -> analyze -> notify -> store).
    Does not block; runs in background and returns immediately with run_id.
    For synchronous run, call run_monitoring_agent() and await; here we trigger async and return.
    """
    try:
        # Run in background so request returns quickly
        result = await run_monitoring_agent()
        return RunMonitoringResponse(
            monitoring_run_id=result.get("monitoring_run_id", ""),
            events_ingested=result.get("events_ingested", 0),
            clusters_created=result.get("clusters_created", 0),
            new_incidents=result.get("new_incidents", 0),
            alerts_sent=result.get("alerts_sent", 0),
            analysis_duration_ms=result.get("analysis_duration_ms"),
            failures_in_monitoring_pipeline=result.get("failures_in_monitoring_pipeline"),
        )
    except Exception as e:
        logger.exception("post_run_monitoring failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/runs")
async def get_monitoring_runs(limit: int = 20):
    """List recent monitoring runs."""
    try:
        from src.monitoring.models.monitoring_run import MonitoringRun
        from src.db.base import SessionLocal
        db = SessionLocal()
        try:
            rows = db.query(MonitoringRun).order_by(MonitoringRun.created_at.desc()).limit(limit).all()
            return {
                "runs": [
                    {
                        "monitoring_run_id": r.monitoring_run_id,
                        "events_ingested": r.events_ingested,
                        "clusters_created": r.clusters_created,
                        "new_incidents": r.new_incidents,
                        "alerts_sent": r.alerts_sent,
                        "analysis_duration_ms": r.analysis_duration_ms,
                        "failures_in_monitoring_pipeline": r.failures_in_monitoring_pipeline,
                        "created_at": r.created_at.isoformat() if r.created_at else None,
                    }
                    for r in rows
                ]
            }
        finally:
            db.close()
    except Exception as e:
        logger.warning("get_monitoring_runs failed: %s", e)
        raise HTTPException(status_code=503, detail="Run storage unavailable")
