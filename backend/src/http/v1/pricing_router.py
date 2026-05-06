"""
ROUTER: pricing_router
PURPOSE: Usage-based pricing API endpoints
ENCODING: UTF-8 WITHOUT BOM
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.services.usage_based_pricing_service import get_usage_based_pricing_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.get("/model")
async def get_pricing_model(db: Session = Depends(get_db)):
    """
    Get complete usage-based pricing model.
    Public endpoint - no authentication required.
    """
    pricing_service = get_usage_based_pricing_service(db)
    return pricing_service.get_pricing_model()


@router.get("/calculate")
async def calculate_query_cost(
    include_persona_deepening: bool = Query(False, description="Include persona deepening"),
    include_visit_route: bool = Query(False, description="Include visit route"),
    include_export: bool = Query(False, description="Include export"),
    include_outreach_preparation: bool = Query(False, description="Include outreach preparation"),
    db: Session = Depends(get_db)
):
    """
    Calculate cost for a single query execution.
    Public endpoint - no authentication required.
    """
    pricing_service = get_usage_based_pricing_service(db)
    return pricing_service.calculate_query_cost(
        include_persona_deepening=include_persona_deepening,
        include_visit_route=include_visit_route,
        include_export=include_export,
        include_outreach_preparation=include_outreach_preparation
    )


@router.get("/estimate")
async def estimate_monthly_cost(
    queries_per_month: int = Query(..., description="Estimated queries per month"),
    avg_modules: Optional[str] = Query(None, description="Comma-separated list of average modules used (e.g., 'persona_deepening,export')"),
    db: Session = Depends(get_db)
):
    """
    Estimate monthly cost based on expected usage.
    Public endpoint - no authentication required.
    """
    pricing_service = get_usage_based_pricing_service(db)
    
    avg_optional_modules = []
    if avg_modules:
        avg_optional_modules = [m.strip() for m in avg_modules.split(",") if m.strip()]
    
    return pricing_service.estimate_monthly_cost(
        estimated_queries_per_month=queries_per_month,
        avg_optional_modules=avg_optional_modules if avg_optional_modules else None
    )


@router.get("/activation")
async def get_activation_cost(db: Session = Depends(get_db)):
    """
    Get account activation fee information.
    Public endpoint - no authentication required.
    """
    pricing_service = get_usage_based_pricing_service(db)
    return pricing_service.get_account_activation_cost()
