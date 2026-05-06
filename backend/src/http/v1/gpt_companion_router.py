"""
ROUTER: gpt_companion_router
PURPOSE: API endpoints for GPT Companion (guide/explainer mode)
ENCODING: UTF-8 WITHOUT BOM

GPT Companion endpoints. CRITICAL: GPT never executes, only explains.
All execution happens in SOAR backend.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.models.user import User
from src.db.base import get_db
from src.services.auth_service import get_current_user_dependency
from src.services.gpt_companion_service import GPTCompanionService

router = APIRouter(prefix="/gpt-companion", tags=["gpt-companion"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class GuideRequest(BaseModel):
    query: str = Field(..., description="User question or request for guidance")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context (current page, features used, etc.)")


class ExplainRequest(BaseModel):
    target_id: str = Field(..., description="Target ID (company or persona)")
    target_type: str = Field(..., description="Target type: 'company' or 'persona'")
    persona_id: Optional[int] = Field(None, description="Persona ID (if matching from persona perspective)")


class StrategyRequest(BaseModel):
    market_context: Dict[str, Any] = Field(..., description="Market exploration context")


class GPTCompanionResponse(BaseModel):
    mode: str
    response: Optional[str] = None
    explanation: Optional[str] = None
    strategies: Optional[list] = None
    suggested_actions: Optional[list] = None
    execution_required: bool = Field(default=False, description="Always False - GPT never executes")
    execution_note: Optional[str] = None


# ============================================================================
# GPT COMPANION ENDPOINTS
# ============================================================================

@router.post("/guide", response_model=GPTCompanionResponse)
async def get_guidance(
    request: GuideRequest,
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Get guidance from GPT Companion.
    
    Mode: GUIDE
    Purpose: Explains features, suggests next steps
    
    CRITICAL: GPT never executes. Only explains and guides.
    All execution happens in SOAR B2B backend.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = GPTCompanionService()
    result = service.get_guidance(request.query, request.context)
    
    return GPTCompanionResponse(**result)


@router.post("/explain", response_model=GPTCompanionResponse)
async def explain_target(
    request: ExplainRequest,
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Explain "Why this account?" in natural language.
    
    Mode: EXPLAINER
    Purpose: Converts trace data into human-readable explanation
    
    CRITICAL: GPT explains EXISTING trace data only.
    GPT never executes or modifies anything.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if request.target_type not in ["company", "persona"]:
        raise HTTPException(status_code=400, detail="target_type must be 'company' or 'persona'")
    
    # Get trace data from explainer service
    from src.services.explainer_service import ExplainerService
    explainer_service = ExplainerService(db)
    
    try:
        trace = explainer_service.generate_trace(
            user_id=user.id,
            target_id=request.target_id,
            target_type=request.target_type,
            persona_id=request.persona_id
        )
        
        # Convert trace to dict for GPT
        trace_dict = {
            "target_id": trace.target_id,
            "target_type": trace.target_type,
            "overall_score": trace.overall_score,
            "explanation": {
                "signals_used": trace.signals_used or [],
                "location_affinity": {
                    "score": trace.location_affinity_score,
                    "details": trace.location_affinity_details
                } if trace.location_affinity_score else None,
                "confidence_breakdown": trace.confidence_breakdown or {}
            },
            "confidence_level": trace.confidence_level
        }
        
        service = GPTCompanionService()
        result = service.explain_target(trace_dict)
        
        return GPTCompanionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/strategy", response_model=GPTCompanionResponse)
async def suggest_strategy(
    request: StrategyRequest,
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Suggest market exploration strategies.
    
    Mode: STRATEGY
    Purpose: Suggests strategies based on market context
    
    CRITICAL: GPT suggests only. Execution happens in SOAR backend.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = GPTCompanionService()
    result = service.suggest_strategy(request.market_context)
    
    return GPTCompanionResponse(**result)
