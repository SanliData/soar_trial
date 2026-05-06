"""
ROUTER: result_router
PURPOSE: Result delivery and export endpoints
ENCODING: UTF-8 WITHOUT BOM

Users MUST be able to download their results.
Formats: CSV, XLSX, JSON, ZIP
"""

import logging
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.http.v1.b2b_api_router import validate_api_key
from src.services.result_service import get_result_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["results"])


***REMOVED*** Request Models
class ExportRequest(BaseModel):
    format: str = Field(..., description="Export format: csv, xlsx, json, zip")
    modules: Optional[List[str]] = Field(None, description="List of module types to export")


***REMOVED*** Response Models
class PreviewReportResponse(BaseModel):
    plan_id: str
    target_region: str
    businesses_found: int
    relevant_departments: int
    target_personas: int
    reachability: dict
    status: str
    note: str


class ExportJobResponse(BaseModel):
    export_id: str
    status: str
    format: str
    created_at: str


***REMOVED*** Endpoints
@router.get("/plan/{plan_id}/preview", response_model=PreviewReportResponse)
async def get_preview_report(
    plan_id: str,
    api_key: str = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """
    Get non-sensitive preview report (before purchase).
    Shows aggregated counts only, no PII.
    """
    try:
        result_service = get_result_service(db)
        preview = result_service.get_preview_report(plan_id)
        return PreviewReportResponse(**preview)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting preview: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get preview")


@router.get("/plans/{plan_id}/results")
async def get_results_hub(
    plan_id: str,
    api_key: str = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """
    Get Results Hub for a plan.
    Shows what the user requested, what is completed, what is downloadable.
    Returns empty state if Results Hub not created yet.
    """
    try:
        result_service = get_result_service(db)
        results = result_service.get_results(plan_id)
        return results
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting results: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get results")


@router.post("/plans/{plan_id}/export", response_model=ExportJobResponse)
async def create_export(
    plan_id: str,
    export_request: ExportRequest,
    api_key: str = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """
    Create async export job.
    Returns export_id for status tracking.
    """
    try:
        result_service = get_result_service(db)
        export_job = result_service.create_export_job(
            plan_id=plan_id,
            format=export_request.format,
            modules=export_request.modules
        )
        
        return ExportJobResponse(
            export_id=export_job.export_id,
            status=export_job.status,
            format=export_job.format,
            created_at=export_job.created_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating export: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create export")


@router.get("/exports/{export_id}/status")
async def get_export_status(
    export_id: str,
    api_key: str = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """
    Get export job status.
    Returns: pending, processing, ready, failed
    """
    try:
        result_service = get_result_service(db)
        export_job = result_service.get_export_status(export_id)
        
        if not export_job:
            raise HTTPException(status_code=404, detail=f"Export {export_id} not found")
        
        return {
            "export_id": export_job.export_id,
            "status": export_job.status,
            "format": export_job.format,
            "file_size_bytes": export_job.file_size_bytes,
            "created_at": export_job.created_at.isoformat(),
            "updated_at": export_job.updated_at.isoformat(),
            "completed_at": export_job.completed_at.isoformat() if export_job.completed_at else None,
            "error_message": export_job.error_message
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting export status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get export status")


@router.get("/exports/{export_id}/download")
async def download_export(
    export_id: str,
    api_key: str = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """
    Download export file.
    Returns file if status is 'ready'.
    """
    try:
        result_service = get_result_service(db)
        file_path = result_service.get_export_file_path(export_id)
        
        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail="Export file not found or not ready")
        
        export_job = result_service.get_export_status(export_id)
        
        ***REMOVED*** Determine MIME type
        mime_types = {
            "csv": "text/csv",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "json": "application/json",
            "zip": "application/zip"
        }
        mime_type = mime_types.get(export_job.format, "application/octet-stream")
        
        return FileResponse(
            path=str(file_path),
            media_type=mime_type,
            filename=f"soar_export_{export_id}.{export_job.format}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading export: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to download export")
