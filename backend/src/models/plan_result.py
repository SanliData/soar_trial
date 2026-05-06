"""
MODEL: plan_result
PURPOSE: Result delivery and module tracking for SOAR B2B
ENCODING: UTF-8 WITHOUT BOM

Each plan MUST generate a Results Hub with downloadable outputs.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index, Boolean
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.orm import relationship
from src.db.base import Base


class PlanResult(Base):
    """
    Main result container for a plan.
    Represents the Results Hub.
    """
    
    __tablename__ = "plan_results"
    
    ***REMOVED*** Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    ***REMOVED*** Foreign key to PlanLifecycle
    plan_id = Column(String(255), ForeignKey("plan_lifecycles.plan_id"), nullable=False, unique=True, index=True)
    
    ***REMOVED*** Result status
    status = Column(String(50), default="pending", nullable=False, index=True)  ***REMOVED*** pending, processing, ready, completed
    
    ***REMOVED*** UPAP verification (set after export verification gate)
    verification_status = Column(String(50), nullable=True, index=True)  ***REMOVED*** PASS, FAIL, null
    verification_report_path = Column(String(512), nullable=True)  ***REMOVED*** path to export_verification_{plan_id}_{run_id}.json
    
    ***REMOVED*** Overall result summary
    summary = Column(JSON, nullable=True)  ***REMOVED*** High-level stats (businesses, personas, reachability counts)
    
    ***REMOVED*** Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    ***REMOVED*** Relationships
    plan = relationship("PlanLifecycle", backref="result", uselist=False)
    modules = relationship("ResultModule", back_populates="plan_result", cascade="all, delete-orphan")
    
    ***REMOVED*** Indexes
    __table_args__ = (
        Index('idx_plan_result_plan_id', 'plan_id'),
        Index('idx_plan_result_status', 'status'),
    )


class ResultModule(Base):
    """
    Individual result module within a plan result.
    Each module is independent and optional.
    """
    
    __tablename__ = "result_modules"
    
    ***REMOVED*** Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    ***REMOVED*** Foreign key to PlanResult
    plan_result_id = Column(Integer, ForeignKey("plan_results.id"), nullable=False, index=True)
    
    ***REMOVED*** Module type
    module_type = Column(String(100), nullable=False, index=True)  ***REMOVED*** business_discovery, persona_summary, reachability_report, precision_exposure, soft_conversion, outreach_outcomes
    
    ***REMOVED*** Module status
    status = Column(String(50), default="pending", nullable=False, index=True)  ***REMOVED*** pending, processing, ready, failed
    
    ***REMOVED*** Preview data (non-sensitive, aggregated)
    preview_data = Column(JSON, nullable=True)  ***REMOVED*** Aggregated counts, ratios (no PII)
    
    ***REMOVED*** Result data (full, accessible only after purchase/approval)
    result_data = Column(JSON, nullable=True)  ***REMOVED*** Full results (can be large)
    
    ***REMOVED*** File references (if exported)
    export_file_path = Column(String(512), nullable=True)  ***REMOVED*** Path to exported file
    
    ***REMOVED*** Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    ready_at = Column(DateTime(timezone=True), nullable=True)
    
    ***REMOVED*** Relationship
    plan_result = relationship("PlanResult", back_populates="modules")
    
    ***REMOVED*** Indexes
    __table_args__ = (
        Index('idx_result_module_result_id', 'plan_result_id'),
        Index('idx_result_module_type', 'module_type'),
        Index('idx_result_module_status', 'status'),
    )
