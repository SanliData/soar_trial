"""
ROUTER: persona_signal_router
PURPOSE: API endpoints for managing signal weights and exclusions (Living Persona Engine)
ENCODING: UTF-8 WITHOUT BOM
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.models.user import User
from src.db.base import get_db
from src.services.auth_service import get_current_user_dependency, get_current_user_impl
from src.services.persona_signal_service import PersonaSignalService

router = APIRouter(prefix="/personas", tags=["persona-signals"])


***REMOVED*** ============================================================================
***REMOVED*** DEPENDENCIES
***REMOVED*** ============================================================================

def get_current_user_from_header(
    authorization: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Helper to inject authorization header into get_current_user_dependency"""
    if authorization:
        return get_current_user_impl(authorization=authorization, db=db)
    return None


***REMOVED*** ============================================================================
***REMOVED*** REQUEST/RESPONSE MODELS
***REMOVED*** ============================================================================

class SignalWeightRequest(BaseModel):
    signal_type: str = Field(..., description="Signal type (e.g., 'location', 'industry', 'job_title')")
    weight: float = Field(..., ge=0.0, le=10.0, description="Weight value (0.0 to 10.0)")
    description: Optional[str] = Field(None, description="Optional description")


class SignalWeightResponse(BaseModel):
    id: int
    user_id: int
    persona_id: Optional[int]
    signal_type: str
    weight: float
    description: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str


class SignalExclusionRequest(BaseModel):
    signal_type: str = Field(..., description="Signal type (e.g., 'location', 'industry')")
    signal_value: str = Field(..., description="Signal value to exclude (e.g., 'Retail', 'Istanbul')")
    exclusion_reason: Optional[str] = Field(None, description="Optional reason for exclusion")


class SignalExclusionResponse(BaseModel):
    id: int
    user_id: int
    persona_id: Optional[int]
    signal_type: str
    signal_value: str
    exclusion_reason: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str


class SignalConfigResponse(BaseModel):
    weights: Dict[str, Dict[str, Any]]
    exclusions: List[Dict[str, Any]]


***REMOVED*** ============================================================================
***REMOVED*** SIGNAL WEIGHT ENDPOINTS
***REMOVED*** ============================================================================

@router.post("/{persona_id}/signal-weights", response_model=SignalWeightResponse)
async def set_persona_signal_weight(
    persona_id: int = Path(..., description="Persona ID"),
    request: SignalWeightRequest = ...,
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Set signal weight for a specific persona.
    Creates or updates existing weight.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = PersonaSignalService(db)
    
    try:
        weight = service.set_signal_weight(
            user_id=user.id,
            signal_type=request.signal_type,
            weight=request.weight,
            persona_id=persona_id,
            description=request.description
        )
        return SignalWeightResponse(**weight.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/signal-weights", response_model=SignalWeightResponse)
async def set_global_signal_weight(
    request: SignalWeightRequest = ...,
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Set global (user-level) signal weight.
    Applies to all personas unless overridden by persona-specific weight.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = PersonaSignalService(db)
    
    try:
        weight = service.set_signal_weight(
            user_id=user.id,
            signal_type=request.signal_type,
            weight=request.weight,
            persona_id=None,  ***REMOVED*** Global weight
            description=request.description
        )
        return SignalWeightResponse(**weight.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{persona_id}/signal-weights", response_model=List[SignalWeightResponse])
async def get_persona_signal_weights(
    persona_id: int = Path(..., description="Persona ID"),
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get all signal weights for a specific persona"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = PersonaSignalService(db)
    weights = service.get_all_weights(user.id, persona_id=persona_id)
    
    return [SignalWeightResponse(**w.to_dict()) for w in weights]


@router.get("/signal-weights", response_model=List[SignalWeightResponse])
async def get_global_signal_weights(
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get all global (user-level) signal weights"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = PersonaSignalService(db)
    weights = service.get_all_weights(user.id, persona_id=None)
    
    return [SignalWeightResponse(**w.to_dict()) for w in weights]


@router.put("/{persona_id}/signal-weights/{signal_type}", response_model=SignalWeightResponse)
async def update_persona_signal_weight(
    persona_id: int = Path(..., description="Persona ID"),
    signal_type: str = Path(..., description="Signal type"),
    request: SignalWeightRequest = ...,
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Update signal weight for a specific persona"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if request.signal_type != signal_type:
        raise HTTPException(status_code=400, detail="Signal type in path must match request body")
    
    service = PersonaSignalService(db)
    
    try:
        weight = service.set_signal_weight(
            user_id=user.id,
            signal_type=signal_type,
            weight=request.weight,
            persona_id=persona_id,
            description=request.description
        )
        return SignalWeightResponse(**weight.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{persona_id}/signal-weights/{weight_id}")
async def delete_persona_signal_weight(
    persona_id: int = Path(..., description="Persona ID"),
    weight_id: int = Path(..., description="Weight ID"),
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Delete (deactivate) a signal weight"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = PersonaSignalService(db)
    deleted = service.delete_signal_weight(user.id, weight_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Signal weight not found")
    
    return {"success": True, "message": "Signal weight deleted"}


***REMOVED*** ============================================================================
***REMOVED*** SIGNAL EXCLUSION ENDPOINTS
***REMOVED*** ============================================================================

@router.post("/{persona_id}/signal-exclusions", response_model=SignalExclusionResponse)
async def add_persona_signal_exclusion(
    persona_id: int = Path(..., description="Persona ID"),
    request: SignalExclusionRequest = ...,
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Add signal exclusion for a specific persona.
    Prevents matching personas with this signal value.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = PersonaSignalService(db)
    
    try:
        exclusion = service.add_signal_exclusion(
            user_id=user.id,
            signal_type=request.signal_type,
            signal_value=request.signal_value,
            persona_id=persona_id,
            exclusion_reason=request.exclusion_reason
        )
        return SignalExclusionResponse(**exclusion.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/signal-exclusions", response_model=SignalExclusionResponse)
async def add_global_signal_exclusion(
    request: SignalExclusionRequest = ...,
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Add global (user-level) signal exclusion.
    Applies to all personas unless overridden by persona-specific exclusion.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = PersonaSignalService(db)
    
    try:
        exclusion = service.add_signal_exclusion(
            user_id=user.id,
            signal_type=request.signal_type,
            signal_value=request.signal_value,
            persona_id=None,  ***REMOVED*** Global exclusion
            exclusion_reason=request.exclusion_reason
        )
        return SignalExclusionResponse(**exclusion.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{persona_id}/signal-exclusions", response_model=List[SignalExclusionResponse])
async def get_persona_signal_exclusions(
    persona_id: int = Path(..., description="Persona ID"),
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get all signal exclusions for a specific persona"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = PersonaSignalService(db)
    exclusions = service.get_all_exclusions(user.id, persona_id=persona_id)
    
    return [SignalExclusionResponse(**e.to_dict()) for e in exclusions]


@router.get("/signal-exclusions", response_model=List[SignalExclusionResponse])
async def get_global_signal_exclusions(
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get all global (user-level) signal exclusions"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = PersonaSignalService(db)
    exclusions = service.get_all_exclusions(user.id, persona_id=None)
    
    return [SignalExclusionResponse(**e.to_dict()) for e in exclusions]


@router.delete("/{persona_id}/signal-exclusions/{exclusion_id}")
async def remove_persona_signal_exclusion(
    persona_id: int = Path(..., description="Persona ID"),
    exclusion_id: int = Path(..., description="Exclusion ID"),
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Remove (deactivate) a signal exclusion"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = PersonaSignalService(db)
    deleted = service.remove_signal_exclusion(user.id, exclusion_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Signal exclusion not found")
    
    return {"success": True, "message": "Signal exclusion removed"}


***REMOVED*** ============================================================================
***REMOVED*** CONFIGURATION ENDPOINTS
***REMOVED*** ============================================================================

@router.get("/{persona_id}/signal-config", response_model=SignalConfigResponse)
async def get_persona_signal_config(
    persona_id: int = Path(..., description="Persona ID"),
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Get complete signal configuration (weights + exclusions) for a persona.
    Includes both persona-specific and global settings.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = PersonaSignalService(db)
    config = service.get_all_effective_config(user.id, persona_id=persona_id)
    
    return SignalConfigResponse(**config)


@router.get("/signal-config", response_model=SignalConfigResponse)
async def get_global_signal_config(
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Get global (user-level) signal configuration (weights + exclusions).
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = PersonaSignalService(db)
    config = service.get_all_effective_config(user.id, persona_id=None)
    
    return SignalConfigResponse(**config)
