"""
SERVICE: plan_service
PURPOSE: Plan lifecycle and objective management service
ENCODING: UTF-8 WITHOUT BOM
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.models.plan_lifecycle import PlanLifecycle, PlanStage
from src.models.plan_objective import PlanObjective
from src.models.plan_result import PlanResult

logger = logging.getLogger(__name__)


class PlanService:
    """Service for managing plan lifecycle and objectives"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_plan_lifecycle(
        self,
        plan_id: str,
        onboarding_data: Dict[str, Any],
        created_by_user_id: Optional[int] = None,
    ) -> PlanLifecycle:
        """Create a new plan lifecycle from onboarding data. Ensures hs_code (gümrük) is set (user or AI)."""
        from src.services.hs_code_service import ensure_hs_code_in_onboarding
        onboarding_data = ensure_hs_code_in_onboarding(dict(onboarding_data) if onboarding_data else {})
        plan = PlanLifecycle(
            plan_id=plan_id,
            onboarding_data=onboarding_data,
            current_stage="CREATED",
            status="active",
            created_by_user_id=created_by_user_id,
        )
        self.db.add(plan)
        
        # Create default timeline stages
        default_stages = [
            {"name": "market_scan", "order": 1, "description": "Your target geography and industry are analyzed. Relevant companies are identified."},
            {"name": "persona_mapping", "order": 2, "description": "Decision-making roles and departments are mapped. Authority and relevance levels are classified."},
            {"name": "reachability_assessment", "order": 3, "description": "Available access channels are evaluated (email, professional networks, exposure feasibility)."},
            {"name": "activation_options", "order": 4, "description": "You review available paths and estimated impact: Lead discovery, Exposure, Conversion, Direct outreach (optional)."},
            {"name": "activation", "order": 5, "description": "Selected modules are activated. You start receiving measurable outputs."}
        ]
        
        for stage_data in default_stages:
            stage = PlanStage(
                plan_id=plan_id,
                stage_name=stage_data["name"],
                stage_order=stage_data["order"],
                description=stage_data["description"],
                status="pending"
            )
            self.db.add(stage)
        
        self.db.commit()
        self.db.refresh(plan)
        
        # Create Results Hub
        try:
            from src.services.result_service import get_result_service
            result_service = get_result_service(self.db)
            result_service.create_result_hub(plan_id)
            logger.info(f"Results Hub created for plan: {plan_id}")
        except Exception as e:
            # Don't fail plan creation if result hub creation fails
            logger.warning(f"Results Hub creation skipped: {str(e)}")
        
        return plan
    
    def get_plan(self, plan_id: str) -> Optional[PlanLifecycle]:
        """Get plan by plan_id"""
        return self.db.query(PlanLifecycle).filter(PlanLifecycle.plan_id == plan_id).first()
    
    def save_objectives(
        self,
        plan_id: str,
        objective_types: List[str]
    ) -> List[PlanObjective]:
        """Save user-selected objectives for a plan"""
        plan = self.get_plan(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
        
        # Delete existing objectives
        self.db.query(PlanObjective).filter(PlanObjective.plan_id == plan_id).delete()
        
        # Create new objectives
        objectives = []
        for obj_type in objective_types:
            objective = PlanObjective(
                plan_id=plan_id,
                objective_type=obj_type,
                status="pending"
            )
            self.db.add(objective)
            objectives.append(objective)
        
        # Update plan
        plan.selected_objectives = objective_types
        plan.objectives_selected_at = datetime.utcnow()
        
        # Auto-advance to ANALYSIS_READY stage
        if plan.current_stage == "CREATED":
            plan.current_stage = "ANALYSIS_READY"
            plan.analysis_ready_at = datetime.utcnow()
            # Start market_scan stage
            market_scan = self.db.query(PlanStage).filter(
                and_(PlanStage.plan_id == plan_id, PlanStage.stage_name == "market_scan")
            ).first()
            if market_scan:
                market_scan.status = "in_progress"
                market_scan.started_at = datetime.utcnow()
        
        self.db.commit()
        
        for obj in objectives:
            self.db.refresh(obj)
        
        return objectives
    
    def get_timeline(self, plan_id: str) -> Dict[str, Any]:
        """Get process timeline with all stages"""
        plan = self.get_plan(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
        
        stages = self.db.query(PlanStage).filter(
            PlanStage.plan_id == plan_id
        ).order_by(PlanStage.stage_order).all()
        
        # Determine if activation is possible
        can_activate = (
            plan.current_stage in ["EXPOSURE_READY", "PERSONA_REVIEW"] and
            any(obj.status == "approved" for obj in plan.objectives)
        )
        
        return {
            "plan_id": plan_id,
            "current_stage": plan.current_stage,
            "stages": [
                {
                    "name": stage.stage_name,
                    "order": stage.stage_order,
                    "description": stage.description,
                    "status": stage.status,
                    "started_at": stage.started_at.isoformat() if stage.started_at else None,
                    "completed_at": stage.completed_at.isoformat() if stage.completed_at else None,
                    "admin_note": stage.admin_note
                }
                for stage in stages
            ],
            "admin_note": plan.admin_note,
            "can_activate": can_activate
        }
    
    def activate_module(
        self,
        plan_id: str,
        module_type: str
    ) -> PlanObjective:
        """Activate a module with explicit approval"""
        plan = self.get_plan(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
        
        # Find objective
        objective = self.db.query(PlanObjective).filter(
            and_(
                PlanObjective.plan_id == plan_id,
                PlanObjective.objective_type == module_type
            )
        ).first()
        
        if not objective:
            raise ValueError(f"Objective {module_type} not found for plan {plan_id}")
        
        if objective.status != "approved":
            raise ValueError(f"Objective {module_type} must be approved before activation")
        
        # Activate
        objective.status = "active"
        objective.activated_at = datetime.utcnow()
        
        # Update plan stage if needed
        if plan.current_stage == "EXPOSURE_READY":
            plan.current_stage = "EXPOSURE_RUNNING"
            plan.exposure_running_at = datetime.utcnow()
        
        # Update activation stage
        activation_stage = self.db.query(PlanStage).filter(
            and_(PlanStage.plan_id == plan_id, PlanStage.stage_name == "activation")
        ).first()
        if activation_stage:
            activation_stage.status = "in_progress"
            if not activation_stage.started_at:
                activation_stage.started_at = datetime.utcnow()
        
        plan.activation_approved_at = datetime.utcnow()
        if not plan.modules_activated:
            plan.modules_activated = []
        if module_type not in plan.modules_activated:
            plan.modules_activated.append(module_type)
        
        self.db.commit()
        self.db.refresh(objective)
        return objective


def get_plan_service(db: Session) -> PlanService:
    """Get plan service instance"""
    return PlanService(db)
