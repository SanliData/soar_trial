"""
ROUTER: plan_router
PURPOSE: Plan lifecycle and objective management endpoints
ENCODING: UTF-8 WITHOUT BOM
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.services.plan_service import get_plan_service

# Import validate_api_key from b2b_api_router (no circular import since plan_router is included separately in app.py)
from src.http.v1.b2b_api_router import validate_api_key

logger = logging.getLogger(__name__)

router = APIRouter(tags=["plan"])


# Request Models
class PlanObjectivesRequest(BaseModel):
    plan_id: str = Field(..., description="Plan ID from onboarding")
    objectives: List[str] = Field(..., description="List of objective types selected by user")


class ActivationRequest(BaseModel):
    module_type: str = Field(..., description="Module type to activate")


class TimelineStepResponse(BaseModel):
    name: str
    order: int
    description: str
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    admin_note: Optional[str] = None


class TimelineResponse(BaseModel):
    plan_id: str
    current_stage: str
    stages: List[TimelineStepResponse]
    admin_note: Optional[str] = None
    can_activate: bool


class ObjectivesResponse(BaseModel):
    plan_id: str
    objectives: List[Dict[str, Any]]
    saved_at: str


# Endpoints
@router.post("/plan/objectives", response_model=ObjectivesResponse)
async def save_plan_objectives(
    request: PlanObjectivesRequest,
    api_key: str = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """
    Save user-selected objectives for a plan.
    Objectives are saved with status="pending" until admin approval or user activation.
    """
    try:
        plan_service = get_plan_service(db)
        
        # Validate plan exists
        plan = plan_service.get_plan(request.plan_id)
        if not plan:
            # Create plan lifecycle if onboarding created plan but lifecycle doesn't exist
            # This handles backward compatibility
            logger.warning(f"Plan {request.plan_id} lifecycle not found, creating from onboarding")
            # Try to load from onboarding_plans.jsonl
            from pathlib import Path
            import json
            plans_file = Path(__file__).parent.parent.parent.parent / "data" / "onboarding_plans.jsonl"
            onboarding_data = None
            if plans_file.exists():
                with open(plans_file, "r", encoding="utf-8") as f:
                    for line in f:
                        plan_data = json.loads(line.strip())
                        if plan_data.get("plan_id") == request.plan_id:
                            onboarding_data = plan_data
                            break
            
            if not onboarding_data:
                raise HTTPException(status_code=404, detail=f"Plan {request.plan_id} not found")
            
            plan = plan_service.create_plan_lifecycle(request.plan_id, onboarding_data)
        
        # Save objectives
        objectives = plan_service.save_objectives(request.plan_id, request.objectives)
        
        return ObjectivesResponse(
            plan_id=request.plan_id,
            objectives=[
                {
                    "type": obj.objective_type,
                    "status": obj.status,
                    "selected_at": obj.selected_at.isoformat()
                }
                for obj in objectives
            ],
            saved_at=datetime.utcnow().isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error saving objectives: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to save objectives")


@router.get("/plan/{plan_id}/timeline", response_model=TimelineResponse)
async def get_process_timeline(
    plan_id: str,
    api_key: str = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """
    Get process timeline with step statuses.
    Returns only business steps (no algorithms or technical logic).
    """
    try:
        plan_service = get_plan_service(db)
        timeline = plan_service.get_timeline(plan_id)
        
        return TimelineResponse(**timeline)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting timeline: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get timeline")


@router.post("/plan/{plan_id}/activate")
async def activate_module(
    plan_id: str,
    activation: ActivationRequest,
    api_key: str = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """
    Activate a specific module with explicit approval.
    Requires objective to be approved first.
    """
    try:
        plan_service = get_plan_service(db)
        objective = plan_service.activate_module(plan_id, activation.module_type)
        
        return {
            "success": True,
            "plan_id": plan_id,
            "module_type": activation.module_type,
            "status": objective.status,
            "activated_at": objective.activated_at.isoformat() if objective.activated_at else None
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error activating module: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to activate module")
