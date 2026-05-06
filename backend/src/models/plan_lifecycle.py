"""
MODEL: plan_lifecycle
PURPOSE: Plan lifecycle and stage tracking for SOAR B2B
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.orm import relationship
from src.db.base import Base


class PlanLifecycle(Base):
    """
    Plan lifecycle model for tracking onboarding plans through stages.
    Every onboarding request becomes a first-class Plan object.
    """
    
    __tablename__ = "plan_lifecycles"
    
    ***REMOVED*** Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    ***REMOVED*** Plan identification (from onboarding)
    plan_id = Column(String(255), nullable=False, unique=True, index=True)
    
    ***REMOVED*** User who created the plan (optional; for "my archive" filtering)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    ***REMOVED*** Original onboarding data (read-only for admin)
    onboarding_data = Column(JSON, nullable=False)  ***REMOVED*** Full onboarding request
    
    ***REMOVED*** UPAP flags (can also be set via onboarding_data)
    simulation_mode = Column(Boolean, default=False, nullable=True)  ***REMOVED*** true => tag external claims as SIMULATED / NOT VERIFIED
    regulated_domain = Column(Boolean, default=False, nullable=True)  ***REMOVED*** true => Module 5 default off, export disclaimer
    
    ***REMOVED*** Current stage (lifecycle state)
    current_stage = Column(
        String(50), 
        default="CREATED", 
        nullable=False, 
        index=True
    )  ***REMOVED*** CREATED, ANALYSIS_READY, PERSONA_REVIEW, EXPOSURE_READY, EXPOSURE_RUNNING, SOFT_CONVERSION, DIRECT_OUTREACH, COMPLETED
    
    ***REMOVED*** Stage timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    analysis_ready_at = Column(DateTime(timezone=True), nullable=True)
    persona_review_at = Column(DateTime(timezone=True), nullable=True)
    exposure_ready_at = Column(DateTime(timezone=True), nullable=True)
    exposure_running_at = Column(DateTime(timezone=True), nullable=True)
    soft_conversion_at = Column(DateTime(timezone=True), nullable=True)
    direct_outreach_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    ***REMOVED*** Admin intervention flags
    admin_intervened = Column(Boolean, default=False, nullable=False)
    admin_note = Column(Text, nullable=True)  ***REMOVED*** "Custom strategy applied"
    admin_adjustments = Column(JSON, nullable=True)  ***REMOVED*** Persona boundaries, role strictness, exposure radius, channel mix
    
    ***REMOVED*** User selections (objectives)
    selected_objectives = Column(JSON, nullable=True)  ***REMOVED*** List of objective types user selected
    objectives_selected_at = Column(DateTime(timezone=True), nullable=True)
    
    ***REMOVED*** Activation status (explicit approval required)
    modules_activated = Column(JSON, nullable=True)  ***REMOVED*** List of activated module IDs
    activation_approved_at = Column(DateTime(timezone=True), nullable=True)
    
    ***REMOVED*** Status
    status = Column(String(50), default="active", nullable=False, index=True)  ***REMOVED*** active, paused, completed, cancelled
    
    ***REMOVED*** Timestamps
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    ***REMOVED*** Indexes
    __table_args__ = (
        Index('idx_plan_lifecycle_plan_id', 'plan_id'),
        Index('idx_plan_lifecycle_stage', 'current_stage'),
        Index('idx_plan_lifecycle_status', 'status'),
        Index('idx_plan_lifecycle_created_by', 'created_by_user_id'),
    )


class PlanStage(Base):
    """
    Individual stage tracking for detailed process timeline.
    User-visible steps only (no algorithms).
    """
    
    __tablename__ = "plan_stages"
    
    ***REMOVED*** Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    ***REMOVED*** Foreign key to PlanLifecycle
    plan_id = Column(String(255), ForeignKey("plan_lifecycles.plan_id"), nullable=False, index=True)
    
    ***REMOVED*** Stage identification
    stage_name = Column(String(100), nullable=False, index=True)  ***REMOVED*** market_scan, persona_mapping, reachability_assessment, etc.
    stage_order = Column(Integer, nullable=False)  ***REMOVED*** Order in timeline (1, 2, 3, ...)
    
    ***REMOVED*** Stage status
    status = Column(
        String(50), 
        default="pending", 
        nullable=False, 
        index=True
    )  ***REMOVED*** pending, in_progress, completed, paused, skipped
    
    ***REMOVED*** Plain-language description (user-visible, no algorithms)
    description = Column(Text, nullable=True)  ***REMOVED*** Plain language explanation
    
    ***REMOVED*** Estimated time (in days)
    estimated_days_min = Column(Integer, nullable=True)
    estimated_days_max = Column(Integer, nullable=True)
    
    ***REMOVED*** Actual timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    ***REMOVED*** Admin note (if intervention occurred)
    admin_note = Column(Text, nullable=True)  ***REMOVED*** "Custom strategy applied"
    
    ***REMOVED*** Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    ***REMOVED*** Relationship
    plan = relationship("PlanLifecycle", backref="stages")
    
    ***REMOVED*** Indexes
    __table_args__ = (
        Index('idx_plan_stage_plan_id', 'plan_id'),
        Index('idx_plan_stage_name', 'stage_name'),
        Index('idx_plan_stage_status', 'status'),
    )
