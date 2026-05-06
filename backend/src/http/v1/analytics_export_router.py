"""
ROUTER: analytics_export_router
PURPOSE: API endpoints for BigQuery and Google Sheets export
ENCODING: UTF-8 WITHOUT BOM
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from src.services.bigquery_service import get_bigquery_service
from src.services.sheets_service import get_sheets_service
from src.services.background_tasks import get_background_task_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics-export"])


class ExportToBigQueryRequest(BaseModel):
    records: List[Dict[str, Any]]


class ExportToSheetsRequest(BaseModel):
    records: List[Dict[str, Any]]
    title: Optional[str] = None


@router.post("/export-to-bigquery")
async def export_to_bigquery(request: ExportToBigQueryRequest):
    """
    Export discovery records to Google BigQuery.
    """
    bigquery_service = get_bigquery_service()
    
    if not bigquery_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="BigQuery is not available. Please configure GOOGLE_CLOUD_PROJECT_ID."
        )
    
    result = bigquery_service.batch_export_records(request.records)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Export failed")
        )
    
    return {
        "success": True,
        "exported": result.get("exported", 0),
        "failed": result.get("failed", 0)
    }


@router.post("/export-to-sheets")
async def export_to_sheets(request: ExportToSheetsRequest):
    """
    Export discovery records to Google Sheets and return the link.
    Creates a new spreadsheet and writes all records.
    """
    sheets_service = get_sheets_service()
    
    if not sheets_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="Google Sheets API is not available. Please configure credentials."
        )
    
    try:
        result = sheets_service.create_and_write_records(
            records=request.records,
            title=request.title
        )
        
        if not result.get("success"):
            error = result.get("error", "Export failed")
            
            # Check for permission errors (403)
            if "permission" in error.lower() or "403" in error or "forbidden" in error.lower():
                raise HTTPException(
                    status_code=403,
                    detail="Permission denied. Please check Google Sheets API credentials and permissions."
                )
            
            # Other errors: log and return 500
            logger.error(f"Google Sheets export failed: {error}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Export failed: {error}"
            )
        
        return {
            "success": True,
            "spreadsheet_url": result.get("spreadsheet_url"),
            "spreadsheet_id": result.get("spreadsheet_id"),
            "title": result.get("title"),
            "rows_written": result.get("rows_written", 0)
        }
    except HTTPException:
        # Re-raise HTTP exceptions (503, 403, etc.)
        raise
    except Exception as e:
        # Unexpected errors: log and return 500
        logger.error(f"Unexpected error in Google Sheets export: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error during export"
        )


@router.post("/queue-bigquery-export")
async def queue_bigquery_export(request: ExportToBigQueryRequest):
    """
    Queue records for async export to BigQuery (background task).
    """
    background_manager = get_background_task_manager()
    background_manager.export_records_async(request.records)
    
    return {
        "success": True,
        "message": "Records queued for background export to BigQuery",
        "count": len(request.records)
    }


@router.get("/health")
def health():
    """Check health status of analytics export services."""
    bigquery_service = get_bigquery_service()
    sheets_service = get_sheets_service()
    
    return {
        "status": "ok",
        "domain": "analytics-export",
        "bigquery_available": bigquery_service.is_available(),
        "sheets_available": sheets_service.is_available()
    }


