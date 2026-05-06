"""
ROUTER: reachability_router
PURPOSE: Reachability escalation API endpoints (optional, disabled by default)
ENCODING: UTF-8 WITHOUT BOM
"""

import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.models.reachability_escalation import ReachabilityEscalation
from src.models.access_gate import AccessGate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reachability", tags=["reachability"])


class EscalationRequest(BaseModel):
    """Request model for creating reachability escalation"""
    precision_exposure_id: Optional[int] = None
    escalation_type: str = Field("appointment", description="appointment, callback, referral")
    title: Optional[str] = None
    description: Optional[str] = None
    contact_preference: Optional[str] = Field(None, description="email, phone, linkedin, call_center")
    escalation_context: Optional[dict] = None   # Contextual data only (no PII)
    scheduled_at: Optional[str] = None   # ISO datetime string


class EnableEscalationRequest(BaseModel):
    """Request model for enabling escalation module"""
    enable: bool = Field(..., description="Enable or disable escalation module")


@router.post("/escalation")
async def create_escalation(
    request: EscalationRequest,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Create reachability escalation (appointment/escalation).
    Optional module - must be enabled first.
    Prepares architecture for call center partnerships.
    """
    try:
        # Check if escalation module is enabled
        escalation_gate = db.query(AccessGate).filter(
            AccessGate.user_id == user_id,
            AccessGate.module_type == "outreach"
        ).first()
        
        if not escalation_gate or not escalation_gate.is_unlocked:
            raise HTTPException(
                status_code=403,
                detail="Reachability escalation module is disabled by default. Please enable it first."
            )
        
        # Parse scheduled_at if provided
        scheduled_at = None
        if request.scheduled_at:
            try:
                scheduled_at = datetime.fromisoformat(request.scheduled_at.replace('Z', '+00:00'))
            except Exception:
                pass
        
        # Create escalation
        escalation = ReachabilityEscalation(
            user_id=user_id,
            precision_exposure_id=request.precision_exposure_id,
            escalation_type=request.escalation_type,
            title=request.title or f"{request.escalation_type.capitalize()} Request",
            description=request.description,
            contact_preference=request.contact_preference,
            status="pending",
            is_enabled=True,
            escalation_context=request.escalation_context,
            scheduled_at=scheduled_at
        )
        
        db.add(escalation)
        db.commit()
        db.refresh(escalation)
        
        logger.info(f"Reachability escalation created: {escalation.id} (user_id: {user_id}, type: {request.escalation_type})")
        
        return {
            "success": True,
            "escalation": escalation.to_dict(),
            "message": f"{request.escalation_type.capitalize()} escalation created"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating escalation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating escalation: {str(e)}")


@router.post("/enable")
async def enable_escalation_module(
    request: EnableEscalationRequest,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Enable or disable reachability escalation module.
    Disabled by default - user must explicitly enable it.
    """
    try:
        # Get or create access gate for outreach module
        access_gate = db.query(AccessGate).filter(
            AccessGate.user_id == user_id,
            AccessGate.module_type == "outreach"
        ).first()
        
        if not access_gate:
            access_gate = AccessGate(
                user_id=user_id,
                module_type="outreach",
                is_unlocked=request.enable,
                access_count=0
            )
            db.add(access_gate)
        else:
            # Check if user has purchased access
            if request.enable and not access_gate.is_unlocked:
                # Require purchase to enable
                raise HTTPException(
                    status_code=403,
                    detail="Reachability escalation module requires purchase. Please unlock access first."
                )
            
            # Update all escalations for this user
            db.query(ReachabilityEscalation).filter(
                ReachabilityEscalation.user_id == user_id
            ).update({"is_enabled": request.enable})
        
        access_gate.is_unlocked = request.enable
        
        db.commit()
        db.refresh(access_gate)
        
        logger.info(f"Escalation module {'enabled' if request.enable else 'disabled'}: user_id={user_id}")
        
        return {
            "success": True,
            "enabled": request.enable,
            "message": f"Reachability escalation module {'enabled' if request.enable else 'disabled'}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error enabling/disabling escalation module: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error enabling/disabling escalation module: {str(e)}")


@router.get("/status")
async def get_escalation_status(
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Get reachability escalation module status.
    Shows if module is enabled and available.
    """
    try:
        access_gate = db.query(AccessGate).filter(
            AccessGate.user_id == user_id,
            AccessGate.module_type == "outreach"
        ).first()
        
        is_enabled = access_gate.is_unlocked if access_gate else False
        
        return {
            "success": True,
            "is_enabled": is_enabled,
            "module_type": "outreach",
            "message": "Reachability escalation module is optional - activate when ready",
            "requires_purchase": True if access_gate and not access_gate.is_unlocked else False
        }
        
    except Exception as e:
        logger.error(f"Error getting escalation status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting escalation status: {str(e)}")
