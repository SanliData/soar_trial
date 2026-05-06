"""
SERVICE: feasibility_service
PURPOSE: Access feasibility preview service (aggregated counts only, no personal data)
ENCODING: UTF-8 WITHOUT BOM
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.models.feasibility_report import FeasibilityReport
from src.models.access_gate import AccessGate

logger = logging.getLogger(__name__)


class FeasibilityService:
    """Service for generating and managing feasibility reports (preview data only)"""
    
    def __init__(self, db: Session):
        """Initialize Feasibility Service with database session"""
        self.db = db
    
    def generate_feasibility_report(
        self,
        user_id: int,
        onboarding_plan_id: Optional[str] = None,
        geography: Optional[str] = None,
        target_type: Optional[str] = None,
        decision_roles: Optional[str] = None,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate aggregated feasibility report (preview only).
        Contains only counts - NO personal data or company names.
        
        Args:
            user_id: User ID
            onboarding_plan_id: Onboarding plan UUID (optional)
            geography: Geographic region (e.g., "USA")
            target_type: Target type (e.g., "B2B")
            decision_roles: Target roles (e.g., "CEO, CTO")
            region: Region description
        
        Returns:
            Dictionary with feasibility report data (counts only)
        """
        try:
            # Check if report already exists
            existing_report = self.db.query(FeasibilityReport).filter(
                and_(
                    FeasibilityReport.user_id == user_id,
                    FeasibilityReport.onboarding_plan_id == onboarding_plan_id if onboarding_plan_id else True
                )
            ).first()
            
            if existing_report:
                logger.info(f"Feasibility report already exists: {existing_report.id} (user_id: {user_id})")
                return {
                    "success": True,
                    "report": existing_report.to_dict(include_unlocked=False),   # Preview only
                    "message": "Feasibility report retrieved"
                }
            
            # TODO: Implement actual aggregation logic from company/persona data
            # For now, generate sample aggregated counts
            # In production, this would query Company/Persona tables with filters
            # and return ONLY aggregated counts, never individual records
            
            # Sample aggregated data (replace with real aggregation)
            total_businesses = 1250   # Aggregate count
            corporate_email_count = 890   # Count with corporate emails
            phone_contact_count = 1100   # Count with phone availability
            linkedin_profile_count = 980   # Count with LinkedIn profiles
            ad_only_reachable_count = 150   # Count reachable only via ads
            
            # Create feasibility report (locked by default)
            report = FeasibilityReport(
                user_id=user_id,
                onboarding_plan_id=onboarding_plan_id,
                geography=geography,
                region=region,
                target_type=target_type,
                decision_roles=decision_roles,
                total_businesses=total_businesses,
                target_department_size="50-200 employees",   # Example
                corporate_email_count=corporate_email_count,
                phone_contact_count=phone_contact_count,
                linkedin_profile_count=linkedin_profile_count,
                ad_only_reachable_count=ad_only_reachable_count,
                industry_distribution={"Technology": 350, "Manufacturing": 450, "Services": 450},
                company_size_distribution={"Small": 400, "Medium": 600, "Large": 250},
                is_unlocked=0   # Locked - preview only
            )
            
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            
            logger.info(f"Feasibility report created: {report.id} (user_id: {user_id}, total_businesses: {total_businesses})")
            
            # Create access gate for this module
            access_gate = AccessGate(
                user_id=user_id,
                feasibility_report_id=report.id,
                module_type="feasibility",
                is_unlocked=False,   # Locked until purchase
                access_count=0
            )
            self.db.add(access_gate)
            self.db.commit()
            
            return {
                "success": True,
                "report": report.to_dict(include_unlocked=False),   # Preview only - no personal data
                "message": "Feasibility report generated (preview mode)"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error generating feasibility report: {str(e)}")
            return {
                "success": False,
                "error": f"Error generating feasibility report: {str(e)}"
            }
    
    def get_feasibility_report(
        self,
        user_id: int,
        report_id: Optional[int] = None,
        onboarding_plan_id: Optional[str] = None,
        include_unlocked_data: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Get feasibility report.
        By default, returns preview data only (counts, no personal identifiers).
        
        Args:
            user_id: User ID
            report_id: Report ID (optional)
            onboarding_plan_id: Onboarding plan ID (optional)
            include_unlocked_data: If True, includes unlocked data if access gate is open
        
        Returns:
            Report dictionary or None
        """
        try:
            query = self.db.query(FeasibilityReport).filter(FeasibilityReport.user_id == user_id)
            
            if report_id:
                query = query.filter(FeasibilityReport.id == report_id)
            elif onboarding_plan_id:
                query = query.filter(FeasibilityReport.onboarding_plan_id == onboarding_plan_id)
            
            report = query.first()
            
            if not report:
                return None
            
            # Check access gate
            if include_unlocked_data:
                access_gate = self.db.query(AccessGate).filter(
                    and_(
                        AccessGate.user_id == user_id,
                        AccessGate.feasibility_report_id == report.id,
                        AccessGate.module_type == "feasibility"
                    )
                ).first()
                
                if access_gate and access_gate.is_unlocked:
                    # Update access count
                    access_gate.access_count += 1
                    access_gate.last_accessed_at = datetime.utcnow()
                    self.db.commit()
                    
                    return report.to_dict(include_unlocked=True)
            
            # Return preview data only (counts, no personal data)
            return report.to_dict(include_unlocked=False)
            
        except Exception as e:
            logger.error(f"Error getting feasibility report: {str(e)}")
            return None
    
    def unlock_feasibility_report(
        self,
        user_id: int,
        report_id: int,
        purchase_id: str
    ) -> Dict[str, Any]:
        """
        Unlock feasibility report after purchase.
        This grants access to underlying data (still aggregated, but more detailed).
        
        Args:
            user_id: User ID
            report_id: Report ID
            purchase_id: Purchase/subscription ID
        
        Returns:
            Dictionary with unlock result
        """
        try:
            report = self.db.query(FeasibilityReport).filter(
                and_(
                    FeasibilityReport.id == report_id,
                    FeasibilityReport.user_id == user_id
                )
            ).first()
            
            if not report:
                return {
                    "success": False,
                    "error": "Feasibility report not found"
                }
            
            # Update report
            report.is_unlocked = 1
            report.unlocked_at = datetime.utcnow()
            
            # Update access gate
            access_gate = self.db.query(AccessGate).filter(
                and_(
                    AccessGate.user_id == user_id,
                    AccessGate.feasibility_report_id == report_id,
                    AccessGate.module_type == "feasibility"
                )
            ).first()
            
            if access_gate:
                access_gate.is_unlocked = True
                access_gate.purchase_id = purchase_id
                access_gate.purchase_timestamp = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(report)
            
            logger.info(f"Feasibility report unlocked: {report_id} (user_id: {user_id}, purchase_id: {purchase_id})")
            
            return {
                "success": True,
                "report": report.to_dict(include_unlocked=True),
                "message": "Feasibility report unlocked"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error unlocking feasibility report: {str(e)}")
            return {
                "success": False,
                "error": f"Error unlocking feasibility report: {str(e)}"
            }


def get_feasibility_service(db: Session) -> FeasibilityService:
    """Get FeasibilityService instance with database session"""
    return FeasibilityService(db)
