"""
SERVICE: access_gate_service
PURPOSE: Access gate service for purchase gating logic
ENCODING: UTF-8 WITHOUT BOM
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.models.access_gate import AccessGate

logger = logging.getLogger(__name__)


class AccessGateService:
    """Service for managing access gates (purchase gating logic)"""
    
    def __init__(self, db: Session):
        """Initialize Access Gate Service with database session"""
        self.db = db
    
    def unlock_module(
        self,
        user_id: int,
        module_type: str,
        purchase_id: str,
        feasibility_report_id: Optional[int] = None,
        usage_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Unlock access gate for a module after purchase.
        Logs usage for billing.
        
        Args:
            user_id: User ID
            module_type: Module type ("feasibility", "exposure", "outreach", "contact_data")
            purchase_id: Purchase/subscription ID
            feasibility_report_id: Feasibility report ID (optional)
            usage_limit: Usage limit for this module (optional)
        
        Returns:
            Dictionary with unlock result
        """
        try:
            ***REMOVED*** Get or create access gate
            access_gate = self.db.query(AccessGate).filter(
                and_(
                    AccessGate.user_id == user_id,
                    AccessGate.module_type == module_type
                )
            ).first()
            
            if not access_gate:
                ***REMOVED*** Create new access gate
                access_gate = AccessGate(
                    user_id=user_id,
                    feasibility_report_id=feasibility_report_id,
                    module_type=module_type,
                    is_unlocked=False,
                    usage_limit=usage_limit,
                    access_count=0
                )
                self.db.add(access_gate)
            
            ***REMOVED*** Unlock access gate
            access_gate.is_unlocked = True
            access_gate.purchase_id = purchase_id
            access_gate.purchase_timestamp = datetime.utcnow()
            
            if usage_limit is not None:
                access_gate.usage_limit = usage_limit
            
            self.db.commit()
            self.db.refresh(access_gate)
            
            logger.info(f"Access gate unlocked: module={module_type}, user_id={user_id}, purchase_id={purchase_id}")
            
            return {
                "success": True,
                "access_gate": access_gate.to_dict(),
                "message": f"Module '{module_type}' unlocked"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error unlocking access gate: {str(e)}")
            return {
                "success": False,
                "error": f"Error unlocking access gate: {str(e)}"
            }
    
    def check_access(
        self,
        user_id: int,
        module_type: str
    ) -> Dict[str, Any]:
        """
        Check if user has access to a module.
        
        Args:
            user_id: User ID
            module_type: Module type
        
        Returns:
            Dictionary with access status
        """
        try:
            access_gate = self.db.query(AccessGate).filter(
                and_(
                    AccessGate.user_id == user_id,
                    AccessGate.module_type == module_type
                )
            ).first()
            
            if not access_gate:
                return {
                    "has_access": False,
                    "is_unlocked": False,
                    "message": f"Module '{module_type}' requires purchase"
                }
            
            ***REMOVED*** Check if unlocked
            has_access = access_gate.is_unlocked
            
            ***REMOVED*** Check usage limit if set
            usage_exceeded = False
            if access_gate.usage_limit and access_gate.access_count >= access_gate.usage_limit:
                usage_exceeded = True
                has_access = False
            
            return {
                "has_access": has_access and not usage_exceeded,
                "is_unlocked": access_gate.is_unlocked,
                "access_count": access_gate.access_count,
                "usage_limit": access_gate.usage_limit,
                "usage_exceeded": usage_exceeded,
                "message": "Access granted" if has_access and not usage_exceeded else "Access denied - purchase required"
            }
            
        except Exception as e:
            logger.error(f"Error checking access: {str(e)}")
            return {
                "has_access": False,
                "is_unlocked": False,
                "message": f"Error checking access: {str(e)}"
            }
    
    def log_access(
        self,
        user_id: int,
        module_type: str
    ) -> bool:
        """
        Log access for billing/usage tracking.
        
        Args:
            user_id: User ID
            module_type: Module type
        
        Returns:
            True if logged, False otherwise
        """
        try:
            access_gate = self.db.query(AccessGate).filter(
                and_(
                    AccessGate.user_id == user_id,
                    AccessGate.module_type == module_type
                )
            ).first()
            
            if access_gate and access_gate.is_unlocked:
                access_gate.access_count += 1
                access_gate.last_accessed_at = datetime.utcnow()
                self.db.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error logging access: {str(e)}")
            return False
    
    def get_user_access_gates(
        self,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get all access gates for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            List of access gate dictionaries
        """
        try:
            access_gates = self.db.query(AccessGate).filter(
                AccessGate.user_id == user_id
            ).all()
            
            return [gate.to_dict() for gate in access_gates]
            
        except Exception as e:
            logger.error(f"Error getting access gates: {str(e)}")
            return []


def get_access_gate_service(db: Session) -> AccessGateService:
    """Get AccessGateService instance with database session"""
    return AccessGateService(db)
