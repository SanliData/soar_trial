"""
ROUTER: explainer_router
PURPOSE: API endpoints for "Why this account?" explainability traces
ENCODING: UTF-8 WITHOUT BOM
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.models.user import User
from src.db.base import get_db
from src.services.auth_service import get_current_user_dependency
from src.services.explainer_service import ExplainerService
from src.models.target_trace import TargetTrace

router = APIRouter(prefix="/targets", tags=["explainer"])


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class WhyThisAccountResponse(BaseModel):
    """Response model for "Why this account?" trace"""
    target_id: str
    target_type: str
    overall_score: float
    explanation: dict
    confidence_level: Optional[str]
    created_at: str
    updated_at: str


# ============================================================================
# EXPLAINER ENDPOINTS
# ============================================================================

@router.get("/{target_id}/why", response_model=WhyThisAccountResponse)
async def get_why_this_account(
    target_id: str = Path(..., description="Target ID (company ID or persona ID)"),
    target_type: str = Query(..., description="Target type: 'company' or 'persona'"),
    persona_id: Optional[int] = Query(None, description="Persona ID (if matching from persona perspective)"),
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Get "Why this account?" trace for a target.
    
    Returns full explainability data:
    - Signals used
    - Weights applied
    - Exclusions applied
    - Location affinity score
    - Confidence levels
    
    This is the core explainability endpoint that powers the trace panel in the UI.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if target_type not in ["company", "persona"]:
        raise HTTPException(status_code=400, detail="target_type must be 'company' or 'persona'")
    
    # Check if trace exists
    trace = db.query(TargetTrace).filter(
        TargetTrace.user_id == user.id,
        TargetTrace.target_id == target_id,
        TargetTrace.target_type == target_type,
        TargetTrace.persona_id == persona_id
    ).first()
    
    if not trace:
        # Generate trace on-the-fly
        service = ExplainerService(db)
        try:
            trace = service.generate_trace(
                user_id=user.id,
                target_id=target_id,
                target_type=target_type,
                persona_id=persona_id
            )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    
    # Build explanation object
    explanation = {
        "signals_used": trace.signals_used or [],
        "location_affinity": {
            "score": trace.location_affinity_score,
            "details": trace.location_affinity_details
        } if trace.location_affinity_score is not None else None,
        "exclusions_applied": trace.signal_exclusions or [],
        "confidence_breakdown": trace.confidence_breakdown or {}
    }
    
    return WhyThisAccountResponse(
        target_id=trace.target_id,
        target_type=trace.target_type,
        overall_score=trace.overall_score,
        explanation=explanation,
        confidence_level=trace.confidence_level,
        created_at=trace.created_at.isoformat() if trace.created_at else "",
        updated_at=trace.updated_at.isoformat() if trace.updated_at else ""
    )


@router.post("/{target_id}/why", response_model=WhyThisAccountResponse)
async def generate_why_this_account(
    target_id: str = Path(..., description="Target ID (company ID or persona ID)"),
    target_type: str = Query(..., description="Target type: 'company' or 'persona'"),
    persona_id: Optional[int] = Query(None, description="Persona ID (if matching from persona perspective)"),
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Generate or regenerate "Why this account?" trace for a target.
    
    This endpoint forces regeneration of the trace, useful when:
    - Signal weights have changed
    - Exclusions have been updated
    - Location affinity has been modified
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if target_type not in ["company", "persona"]:
        raise HTTPException(status_code=400, detail="target_type must be 'company' or 'persona'")
    
    service = ExplainerService(db)
    
    try:
        trace = service.generate_trace(
            user_id=user.id,
            target_id=target_id,
            target_type=target_type,
            persona_id=persona_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # Build explanation object
    explanation = {
        "signals_used": trace.signals_used or [],
        "location_affinity": {
            "score": trace.location_affinity_score,
            "details": trace.location_affinity_details
        } if trace.location_affinity_score is not None else None,
        "exclusions_applied": trace.signal_exclusions or [],
        "confidence_breakdown": trace.confidence_breakdown or {}
    }
    
    return WhyThisAccountResponse(
        target_id=trace.target_id,
        target_type=trace.target_type,
        overall_score=trace.overall_score,
        explanation=explanation,
        confidence_level=trace.confidence_level,
        created_at=trace.created_at.isoformat() if trace.created_at else "",
        updated_at=trace.updated_at.isoformat() if trace.updated_at else ""
    )


@router.get("/traces")
async def list_target_traces(
    target_type: Optional[str] = Query(None, description="Filter by target type: 'company' or 'persona'"),
    persona_id: Optional[int] = Query(None, description="Filter by persona ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    List all target traces for the authenticated user.
    Useful for batch explainability analysis.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    query = db.query(TargetTrace).filter(TargetTrace.user_id == user.id)
    
    if target_type:
        if target_type not in ["company", "persona"]:
            raise HTTPException(status_code=400, detail="target_type must be 'company' or 'persona'")
        query = query.filter(TargetTrace.target_type == target_type)
    
    if persona_id:
        query = query.filter(TargetTrace.persona_id == persona_id)
    
    traces = query.order_by(TargetTrace.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "traces": [trace.to_dict() for trace in traces],
        "total": query.count(),
        "limit": limit,
        "offset": offset
    }
