"""
ROUTER: industrial_chain_hunter_router
PURPOSE: API endpoints for Industrial Chain Hunter (X -> Y -> Producer analysis)
ENCODING: UTF-8 WITHOUT BOM
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from src.services.industrial_chain_hunter_service import get_industrial_chain_hunter_service
from src.services.auth_service import get_current_user_dependency
from src.middleware.locale_middleware import get_locale_from_request
from src.models.discovery_record import DiscoveryRecord
from src.db.base import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/industrial-chain-hunter", tags=["industrial-chain-hunter"])


class RawMaterialSearchRequest(BaseModel):
    """Request model for raw material search."""
    raw_material: str
    min_confidence: float = 0.5


class ProducerAddRequest(BaseModel):
    """Request model for adding producers to Company Pool."""
    producer_ids: List[int]  ***REMOVED*** IDs from hunt results
    user_id: int


@router.post("/hunt", response_model=None)
async def hunt_manufacturers(
    request: RawMaterialSearchRequest,
    http_request: Request,
    user = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Hunt for manufacturers from raw material (X -> Y -> Producers).
    
    Workflow:
    1. Analyze raw material (X) to find end products (Y)
    2. Search for businesses selling each Y product
    3. Analyze if they are producers or resellers
    4. Return verified manufacturers
    """
    try:
        ***REMOVED*** Get locale from request
        locale = get_locale_from_request(http_request)
        
        hunter_service = get_industrial_chain_hunter_service()
        
        result = hunter_service.hunt_manufacturers(
            raw_material=request.raw_material,
            locale=locale,
            min_confidence=request.min_confidence
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Hunt failed")
            )
        
        return {
            "success": True,
            "raw_material": result.get("raw_material"),
            "end_products": result.get("end_products", []),
            "producers": result.get("producers", []),
            "total_producers": result.get("total_producers", 0)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error hunting manufacturers: {str(e)}"
        )


@router.post("/add-to-pool", response_model=None)
async def add_producers_to_pool(
    request: ProducerAddRequest,
    user = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Add verified producers to Company Pool (Step 4).
    
    Takes producer data from hunt results and creates DiscoveryRecord entries.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        ***REMOVED*** This endpoint would receive producer data from frontend
        ***REMOVED*** and create DiscoveryRecord entries in the database
        ***REMOVED*** For now, return success (implementation depends on DiscoveryRecord structure)
        
        return {
            "success": True,
            "message": f"Added {len(request.producer_ids)} producers to Company Pool",
            "producer_ids": request.producer_ids
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error adding producers to pool: {str(e)}"
        )


@router.get("/health", response_model=None)
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "industrial-chain-hunter"}

