"""
ROUTER: acquisition_router
PURPOSE: Web acquisition API endpoints
ENCODING: UTF-8 WITHOUT BOM
"""

import csv
import json
import logging
from typing import Optional
from io import StringIO
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request, Query, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional

from src.db.base import get_db
from src.services.web_acquisition import (
    AcquisitionJobRequest,
    get_acquisition_service
)
from src.services.web_acquisition.interfaces import AcquisitionJobResult
from src.http.v1.b2b_api_router import validate_api_key
from src.http.v1.admin_router import _admin_emails
from src.core.query_limits import MAX_RESULTS_PER_QUERY

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/b2b/acquisition", tags=["acquisition"])


def _is_admin_from_bearer(authorization: Optional[str] = Header(None)) -> bool:
    """True if Authorization Bearer JWT belongs to an admin email (e.g. isanli058@gmail.com)."""
    if not authorization or not authorization.strip().lower().startswith("bearer "):
        return False
    token = authorization[7:].strip()
    if not token:
        return False
    admin_emails = _admin_emails()
    if not admin_emails:
        return False
    from src.services.auth_service import get_auth_service
    auth_service = get_auth_service()
    result = auth_service.verify_jwt_token(token)
    if not result.get("success") or not result.get("payload"):
        return False
    email = (result.get("payload") or {}).get("email")
    return bool(email and isinstance(email, str) and email.strip().lower() in admin_emails)


@router.post("/jobs")
async def create_acquisition_job(
    request: AcquisitionJobRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    api_key: str = Depends(validate_api_key),
    authorization: Optional[str] = Header(None),
):
    """
    Create a new web acquisition job.
    
    Returns job_id that can be used to check status and download results.
    Admin users (e.g. isanli058@gmail.com via Bearer JWT) get cap override (up to 1000 results).
    """
    ***REMOVED*** TODO: Check if user has permission for this plan_id
    ***REMOVED*** For now, allowing any authenticated user
    
    service = get_acquisition_service()
    
    ***REMOVED*** Admin (e.g. isanli058@gmail.com via Google login JWT) gets cap override
    is_admin = _is_admin_from_bearer(authorization)
    
    try:
        ***REMOVED*** Create job
        job = service.create_job(request, db, is_admin=is_admin)
        
        ***REMOVED*** Optionally start job execution in background (for local dev)
        ***REMOVED*** In production, use Cloud Run Job trigger
        run_async = True  ***REMOVED*** Can be controlled via env var or request param
        
        if run_async:
            ***REMOVED*** Background task for local dev (with warning)
            import warnings
            warnings.warn(
                "Using background task for acquisition job execution. "
                "In production, use Cloud Run Job trigger instead.",
                UserWarning
            )
            
            background_tasks.add_task(
                _execute_job_async,
                job.job_id,
                str(db.bind.url)  ***REMOVED*** Pass connection string, not session
            )
        
        return {
            "success": True,
            "job_id": job.job_id,
            "status": job.status,
            "message": "Acquisition job created. Use job_id to check status and download results."
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create acquisition job: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")


@router.get("/jobs")
async def list_acquisition_jobs(
    plan_id: Optional[str] = Query(None, description="Filter by plan ID"),
    status: Optional[str] = Query(None, description="Filter by status (queued, running, ready, failed)"),
    db: Session = Depends(get_db),
    api_key: str = Depends(validate_api_key)
):
    """
    List acquisition jobs, optionally filtered by plan_id and status.
    """
    from src.models.acquisition_job import AcquisitionJob
    
    query = db.query(AcquisitionJob)
    
    if plan_id:
        query = query.filter(AcquisitionJob.plan_id == plan_id)
    
    if status:
        query = query.filter(AcquisitionJob.status == status)
    
    jobs = query.order_by(AcquisitionJob.created_at.desc()).limit(100).all()
    
    return {
        "jobs": [
            {
                "job_id": job.job_id,
                "plan_id": job.plan_id,
                "status": job.status,
                "target_type": job.target_type,
                "coverage_report": job.coverage_report or {},
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None
            }
            for job in jobs
        ]
    }


@router.get("/jobs/{job_id}")
async def get_acquisition_job_status(
    job_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(validate_api_key)
):
    """
    Get acquisition job status and coverage report.
    """
    service = get_acquisition_service()
    
    job = service.get_job(job_id, db)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    
    ***REMOVED*** Parse geography if available
    geography = None
    if job.geography:
        try:
            geography = json.loads(job.geography)
        except:
            pass
    
    return {
        "job_id": job.job_id,
        "plan_id": job.plan_id,
        "status": job.status,
        "target_type": job.target_type,
        "geography": geography,
        "sources_policy": job.sources_policy,
        "max_results": job.max_results,
        "coverage_report": job.coverage_report or {},
        "error_message": job.error_message,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None
    }


@router.get("/jobs/{job_id}/export.csv")
async def export_acquisition_job_csv(
    job_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(validate_api_key)
):
    """
    Export acquisition job results as CSV.
    """
    service = get_acquisition_service()
    
    job = service.get_job(job_id, db)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    
    if job.status != "ready":
        raise HTTPException(
            status_code=400,
            detail=f"Job is not ready for export. Status: {job.status}"
        )
    
    ***REMOVED*** Get results
    results = service.get_job_results(job, db)
    
    ***REMOVED*** Generate CSV
    output = StringIO()
    writer = csv.writer(output)
    
    ***REMOVED*** Write header
    writer.writerow([
        "Type", "Name", "Email", "Phone", "Website", "Address", "Industry",
        "Job Title", "Department", "Seniority", "Company Name"
    ])
    
    ***REMOVED*** Write businesses
    for business in results.businesses:
        writer.writerow([
            "business",
            business.name,
            "",  ***REMOVED*** email
            business.phone or "",
            business.website or "",
            business.address or "",
            business.industry or "",
            "",  ***REMOVED*** job_title
            "",  ***REMOVED*** department
            "",  ***REMOVED*** seniority
            ""   ***REMOVED*** company_name
        ])
    
    ***REMOVED*** Write contacts
    for contact in results.contacts:
        writer.writerow([
            "contact",
            contact.name or "",
            contact.email or "",
            contact.phone or "",
            "",  ***REMOVED*** website
            "",  ***REMOVED*** address
            "",  ***REMOVED*** industry
            contact.job_title or "",
            contact.department or "",
            contact.seniority or "",
            contact.company_name or ""
        ])
    
    output.seek(0)
    
    ***REMOVED*** Generate filename
    filename = f"acquisition_job_{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.get("/jobs/{job_id}/export.json")
async def export_acquisition_job_json(
    job_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(validate_api_key)
):
    """
    Export acquisition job results as JSON.
    """
    service = get_acquisition_service()
    
    job = service.get_job(job_id, db)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    
    if job.status != "ready":
        raise HTTPException(
            status_code=400,
            detail=f"Job is not ready for export. Status: {job.status}"
        )
    
    ***REMOVED*** Get results
    results = service.get_job_results(job, db)
    
    ***REMOVED*** Build export data
    export_data = {
        "job_id": job.job_id,
        "plan_id": job.plan_id,
        "status": job.status,
        "coverage_report": results.coverage_report.dict(),
        "businesses": [b.dict() for b in results.businesses],
        "contacts": [c.dict() for c in results.contacts],
        "evidence": [e.dict() for e in results.evidence],
        "exported_at": datetime.utcnow().isoformat()
    }
    
    ***REMOVED*** Generate filename
    filename = f"acquisition_job_{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    return StreamingResponse(
        content=json.dumps(export_data, indent=2),
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


async def _execute_job_async(job_id: str, db_url: str):
    """
    Background task to execute acquisition job.
    WARNING: Only for local dev. Use Cloud Run Job in production.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    ***REMOVED*** Create new session for background task
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        service = get_acquisition_service()
        await service.execute_job(job_id, db)
    except Exception as e:
        logger.error(f"Background job execution failed for {job_id}: {e}", exc_info=True)
    finally:
        db.close()
