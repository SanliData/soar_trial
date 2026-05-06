"""
MODEL: acquisition_job
PURPOSE: Web acquisition job tracking for async acquisition worker
ENCODING: UTF-8 WITHOUT BOM

Web acquisition jobs are async, must respect caps, and store results for download.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.orm import relationship
from src.db.base import Base


class AcquisitionJob(Base):
    """
    Web acquisition job for async web scraping/enrichment.
    Uses Browserbase Stagehand (optional, feature-flagged).
    """
    
    __tablename__ = "acquisition_jobs"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Job identifier (UUID for public access)
    job_id = Column(String(255), nullable=False, unique=True, index=True)
    
    # Foreign key to PlanLifecycle
    plan_id = Column(String(255), ForeignKey("plan_lifecycles.plan_id"), nullable=False, index=True)
    
    # Job configuration
    target_type = Column(String(50), nullable=False)   # "businesses", "contacts", "both"
    geography = Column(Text, nullable=True)   # JSON: {"region": "...", "city": "...", etc.}
    sources_policy = Column(String(50), default="official_only", nullable=False)   # "official_only", "public_web"
    max_results = Column(Integer, nullable=False, default=100)   # Capped to 100 (or admin override)
    
    # Job status
    status = Column(String(50), default="queued", nullable=False, index=True)   # queued, running, ready, failed
    
    # Result summary (coverage report)
    coverage_report = Column(JSON, nullable=True)   # {"businesses_found": 0, "contacts_found": 0, "emails": 0, "phones": 0, "websites": 0}
    
    # Error information (if failed)
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    plan = relationship("PlanLifecycle", backref="acquisition_jobs")
    results = relationship("AcquisitionResult", back_populates="job", cascade="all, delete-orphan")
    evidence_sources = relationship("EvidenceSource", back_populates="job", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_acquisition_job_job_id', 'job_id'),
        Index('idx_acquisition_job_plan_id', 'plan_id'),
        Index('idx_acquisition_job_status', 'status'),
    )


class AcquisitionResult(Base):
    """
    Individual acquisition result (business or contact).
    Links to a job and stores acquired data.
    """
    
    __tablename__ = "acquisition_results"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to AcquisitionJob
    job_id = Column(Integer, ForeignKey("acquisition_jobs.id"), nullable=False, index=True)
    
    # Result type
    result_type = Column(String(50), nullable=False, index=True)   # "business", "contact"
    
    # Business data (if result_type == "business")
    business_name = Column(String(255), nullable=True)
    business_address = Column(Text, nullable=True)
    business_website = Column(String(512), nullable=True)
    business_phone = Column(String(50), nullable=True)
    business_industry = Column(String(255), nullable=True)
    business_metadata = Column(JSON, nullable=True)   # Additional business data
    
    # Contact data (if result_type == "contact")
    contact_name = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    contact_job_title = Column(String(255), nullable=True)
    contact_department = Column(String(255), nullable=True)
    contact_seniority = Column(String(100), nullable=True)   # "C-Level", "Director", "Manager", etc.
    contact_metadata = Column(JSON, nullable=True)   # Additional contact data
    
    # Professional B2B level only (no personal/sensitive data)
    # contact_metadata enforces: role/department/seniority/buying_committee
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationship
    job = relationship("AcquisitionJob", back_populates="results")
    
    # Indexes
    __table_args__ = (
        Index('idx_acquisition_result_job_id', 'job_id'),
        Index('idx_acquisition_result_type', 'result_type'),
    )


class EvidenceSource(Base):
    """
    Source tracking for acquired data.
    Tracks which domain/URL provided which evidence.
    """
    
    __tablename__ = "evidence_sources"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to AcquisitionJob
    job_id = Column(Integer, ForeignKey("acquisition_jobs.id"), nullable=False, index=True)
    
    # Source information
    domain = Column(String(255), nullable=False, index=True)
    url = Column(String(1024), nullable=True)
    source_type = Column(String(50), nullable=False)   # "government", "municipality", "chamber", "company_website", "public_directory"
    
    # Evidence count
    businesses_found = Column(Integer, default=0, nullable=False)
    contacts_found = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationship
    job = relationship("AcquisitionJob", back_populates="evidence_sources")
    
    # Indexes
    __table_args__ = (
        Index('idx_evidence_source_job_id', 'job_id'),
        Index('idx_evidence_source_domain', 'domain'),
    )
