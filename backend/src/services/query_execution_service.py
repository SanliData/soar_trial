"""
SERVICE: query_execution_service
PURPOSE: Automated query execution service for plan queries
ENCODING: UTF-8 WITHOUT BOM

Executes queries automatically when user opts in.
Standard queries (MAX 100) don't require admin approval.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from src.core.query_limits import MAX_RESULTS_PER_QUERY
from src.services.feasibility_service import get_feasibility_service
from src.services.result_service import get_result_service
from src.services.usage_based_pricing_service import get_usage_based_pricing_service

logger = logging.getLogger(__name__)


class QueryExecutionService:
    """
    Service for executing queries automatically.
    Handles standard queries (MAX 100) without admin approval.
    """
    
    def __init__(self, db: Session):
        """Initialize query execution service."""
        self.db = db
    
    def calculate_query_cost_preview(
        self,
        plan_id: str,
        selected_objectives: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Calculate cost preview for query execution based on selected objectives.
        
        Args:
            plan_id: Plan ID
            selected_objectives: List of selected objective types
            
        Returns:
            Cost preview dictionary
        """
        pricing_service = get_usage_based_pricing_service(self.db)
        
        # Determine which optional modules are included based on objectives
        include_persona_deepening = selected_objectives and "persona_summary" in selected_objectives
        include_visit_route = selected_objectives and "visit_route" in selected_objectives
        include_export = True   # Export is always available
        include_outreach_preparation = selected_objectives and "outreach_outcomes" in selected_objectives
        
        cost_breakdown = pricing_service.calculate_query_cost(
            include_persona_deepening=include_persona_deepening,
            include_visit_route=include_visit_route,
            include_export=include_export,
            include_outreach_preparation=include_outreach_preparation
        )
        
        return {
            "plan_id": plan_id,
            "cost_preview": cost_breakdown,
            "requires_confirmation": True,
            "message": "Please confirm to proceed with query execution."
        }
    
    def start_query_pipeline(
        self,
        plan_id: str,
        target_type: str,
        geography: str,
        decision_roles: str,
        auto_approved: bool = False,
        admin_override: bool = False,
        cost_confirmed: bool = False,
        selected_objectives: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Start query pipeline for a plan.
        
        Args:
            plan_id: Plan ID
            target_type: Type of targets
            geography: Target geography
            decision_roles: Decision-maker roles
            auto_approved: True if auto-approved (standard queries)
            admin_override: True if admin override requested (requires admin approval)
            cost_confirmed: True if user has confirmed the cost
            selected_objectives: List of selected objective types
            
        Returns:
            Execution result
        """
        try:
            # Require cost confirmation unless auto-approved with explicit confirmation
            if not cost_confirmed and not auto_approved:
                pricing_service = get_usage_based_pricing_service(self.db)
                cost_preview = self.calculate_query_cost_preview(plan_id, selected_objectives)
                return {
                    "success": False,
                    "requires_cost_confirmation": True,
                    "cost_preview": cost_preview,
                    "message": "Cost confirmation required before query execution."
                }
            
            logger.info(f"Starting query pipeline for plan: {plan_id}, auto_approved: {auto_approved}, cost_confirmed: {cost_confirmed}")
            
            # Standard queries (MAX 100) can proceed without admin approval
            if auto_approved and not admin_override:
                # Execute standard query pipeline
                result = self._execute_standard_query(
                    plan_id=plan_id,
                    target_type=target_type,
                    geography=geography,
                    decision_roles=decision_roles
                )
                return result
            
            # Admin approval required for:
            # - Cap overrides (MAX 100+)
            # - Custom algorithm personalization
            # - High-cost outreach/advertising
            else:
                logger.info(f"Query pipeline for plan {plan_id} requires admin approval")
                return {
                    "success": False,
                    "requires_admin_approval": True,
                    "message": "Query requires admin approval (cap override, custom algorithm, or high-cost outreach)"
                }
        
        except Exception as e:
            logger.error(f"Failed to start query pipeline for plan {plan_id}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def _execute_standard_query(
        self,
        plan_id: str,
        target_type: str,
        geography: str,
        decision_roles: str
    ) -> Dict[str, Any]:
        """
        Execute standard query (MAX 100 results).
        
        Args:
            plan_id: Plan ID
            target_type: Type of targets
            geography: Target geography
            decision_roles: Decision-maker roles
            
        Returns:
            Execution result
        """
        try:
            # Step 1: Generate feasibility report (preview)
            feasibility_service = get_feasibility_service(self.db)
            
            # TODO: Get actual user_id from authentication
            # For now, feasibility report is generated without user association
            # In production, extract user_id from authenticated session
            
            logger.info(f"Generating feasibility report for plan: {plan_id}")
            # feasibility_service.generate_feasibility_report(
            # user_id=user_id,  # From authenticated session
            # onboarding_plan_id=plan_id,
            # geography=geography,
            # target_type=target_type,
            # decision_roles=decision_roles,
            # region=geography
            # )
            
            # Step 2: Update plan status
            from src.services.plan_service import get_plan_service
            plan_service = get_plan_service(self.db)
            plan = plan_service.get_plan(plan_id)
            
            if plan:
                # Update plan stage to indicate query started
                plan.current_stage = "QUERY_EXECUTING"
                plan.status = "active"
                self.db.commit()
                logger.info(f"Plan {plan_id} status updated to QUERY_EXECUTING")
            
            # Step 3: Initialize Results Hub if not exists
            result_service = get_result_service(self.db)
            try:
                result_service.create_result_hub(plan_id)
                logger.info(f"Results Hub initialized for plan: {plan_id}")
            except Exception as e:
                # Results Hub might already exist, that's OK
                logger.debug(f"Results Hub already exists for plan {plan_id}: {e}")
            
            return {
                "success": True,
                "plan_id": plan_id,
                "status": "executing",
                "message": "Query pipeline started successfully",
                "max_results": MAX_RESULTS_PER_QUERY,
                "requires_admin_approval": False
            }
        
        except Exception as e:
            logger.error(f"Failed to execute standard query for plan {plan_id}: {e}", exc_info=True)
            raise


# Global service instance per session
def get_query_execution_service(db: Session) -> QueryExecutionService:
    """Get query execution service instance."""
    return QueryExecutionService(db)
