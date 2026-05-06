"""
MODEL: plan_objective
PURPOSE: User-selected objectives for a plan
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from src.db.base import Base


class PlanObjective(Base):
    """
    User-selected objectives for a plan.
    Users explicitly choose what they want to achieve.
    """
    
    __tablename__ = "plan_objectives"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to plan
    plan_id = Column(String(255), ForeignKey("plan_lifecycles.plan_id"), nullable=False, index=True)
    
    # Objective type
    objective_type = Column(String(100), nullable=False, index=True)   # market_intelligence, persona_discovery, reachability_report, precision_exposure, soft_conversion, direct_access
    
    # Status
    status = Column(String(50), default="pending", nullable=False, index=True)   # pending, approved, active, completed, cancelled
    
    # Timestamps
    selected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship
    plan = relationship("PlanLifecycle", backref="objectives")
    
    # Indexes
    __table_args__ = (
        Index('idx_plan_objective_plan_id', 'plan_id'),
        Index('idx_plan_objective_type', 'objective_type'),
        Index('idx_plan_objective_status', 'status'),
    )
