"""
MODEL: export_job
PURPOSE: Export job tracking for async result exports
ENCODING: UTF-8 WITHOUT BOM

Exports must be async, traceable, audit-logged, and accessible only by owner/admin.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from src.db.base import Base


class ExportJob(Base):
    """
    Export job for async result exports.
    Supports CSV, XLSX, JSON, ZIP formats.
    """
    
    __tablename__ = "export_jobs"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Export identifier (UUID for public access)
    export_id = Column(String(255), nullable=False, unique=True, index=True)
    
    # Foreign key to PlanResult
    plan_result_id = Column(Integer, ForeignKey("plan_results.id"), nullable=False, index=True)
    
    # Export configuration
    format = Column(String(20), nullable=False)   # csv, xlsx, json, zip
    modules = Column(Text, nullable=True)   # JSON array of module types to export
    
    # Export status
    status = Column(String(50), default="pending", nullable=False, index=True)   # pending, processing, ready, failed
    
    # File information
    file_path = Column(String(512), nullable=True)   # Path to generated export file
    file_size_bytes = Column(Integer, nullable=True)   # File size in bytes
    mime_type = Column(String(100), nullable=True)   # MIME type for download
    
    # Error information (if failed)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship
    plan_result = relationship("PlanResult", backref="export_jobs")
    
    # Indexes
    __table_args__ = (
        Index('idx_export_job_export_id', 'export_id'),
        Index('idx_export_job_result_id', 'plan_result_id'),
        Index('idx_export_job_status', 'status'),
    )
