"""
MODEL: error_log
PURPOSE: Error logging model for production debugging
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.orm import relationship
from src.db.base import Base


class ErrorLog(Base):
    """
    Error Log model for storing application errors and exceptions.
    Used for debugging and monitoring in production.
    """
    
    __tablename__ = "error_logs"
    
    ***REMOVED*** Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    ***REMOVED*** Foreign key to User (optional, for user-specific errors)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    ***REMOVED*** Error information
    error_type = Column(String(255), nullable=False)  ***REMOVED*** Exception class name
    error_message = Column(Text, nullable=False)  ***REMOVED*** Error message
    error_traceback = Column(Text, nullable=True)  ***REMOVED*** Full traceback
    
    ***REMOVED*** Context information
    service_name = Column(String(100), nullable=True)  ***REMOVED*** Which service failed (auth, ads, calendar, etc.)
    endpoint = Column(String(255), nullable=True)  ***REMOVED*** API endpoint if applicable
    http_method = Column(String(10), nullable=True)  ***REMOVED*** GET, POST, etc.
    
    ***REMOVED*** Request information
    request_data = Column(JSON, nullable=True)  ***REMOVED*** Request payload/parameters
    request_headers = Column(JSON, nullable=True)  ***REMOVED*** Request headers (sanitized)
    
    ***REMOVED*** Error severity
    severity = Column(String(20), default="error", nullable=False)  ***REMOVED*** "info", "warning", "error", "critical"
    
    ***REMOVED*** Resolution status
    is_resolved = Column(Boolean, default=False, nullable=False, index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    ***REMOVED*** Additional metadata
    error_metadata = Column(JSON, nullable=True)  ***REMOVED*** Additional context
    
    ***REMOVED*** Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    ***REMOVED*** Relationship to User
    user = relationship("User", backref="error_logs")
    
    ***REMOVED*** Indexes for performance
    __table_args__ = (
        Index('idx_error_log_user_id', 'user_id'),
        Index('idx_error_log_service', 'service_name'),
        Index('idx_error_log_severity', 'severity'),
        Index('idx_error_log_created_at', 'created_at'),
        Index('idx_error_log_unresolved', 'is_resolved', 'severity'),
    )
    
    def __repr__(self):
        return f"<ErrorLog(id={self.id}, error_type='{self.error_type}', service='{self.service_name}', severity='{self.severity}')>"
    
    def to_dict(self):
        """
        Convert error log to dictionary.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "error_traceback": self.error_traceback,
            "service_name": self.service_name,
            "endpoint": self.endpoint,
            "http_method": self.http_method,
            "request_data": self.request_data,
            "request_headers": self.request_headers,
            "severity": self.severity,
            "is_resolved": self.is_resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolution_notes": self.resolution_notes,
            "metadata": self.error_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

