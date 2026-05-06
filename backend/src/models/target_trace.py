"""
MODEL: target_trace
PURPOSE: Target trace model for explainability - stores "Why this account?" scoring details
ENCODING: UTF-8 WITHOUT BOM

Every target (company or persona) has a trace that explains:
- Signals used
- Weights applied
- Exclusions applied
- Location affinity score
- Confidence levels
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.orm import relationship
from src.db.base import Base


class TargetTrace(Base):
    """
    Target trace model for storing explainability data.
    Every target (company or persona) has a trace that explains why it was matched.
    
    This enables the "Why this account?" trace panel in the UI.
    """
    
    __tablename__ = "target_traces"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Target identification
    target_id = Column(String(255), nullable=False, index=True)  # Company ID or Persona ID
    target_type = Column(String(50), nullable=False, index=True)  # "company" or "persona"
    
    # Foreign key to User (who owns this trace)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Persona ID (if this trace is for a persona matching targets)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=True, index=True)
    
    # Scoring details
    overall_score = Column(Float, nullable=False)  # Overall matching score (0.0 to 1.0)
    
    # Signals used (stored as JSON)
    signals_used = Column(JSON, nullable=True)  # List of signals with values, weights, contributions
    # Format: [
    # {
    # "signal_type": "location",
    # "signal_value": "Istanbul, Turkey",
    # "weight": 1.5,
    # "contribution": 0.25,
    # "confidence": "high"
    # },
    # ...
    # ]
    
    # Signal weights applied (stored as JSON)
    signal_weights = Column(JSON, nullable=True)   # Signal type -> weight mapping
    # Format: {
    # "location": 1.5,
    # "industry": 2.0,
    # "job_title": 1.0
    # }
    
    # Signal exclusions applied (stored as JSON)
    signal_exclusions = Column(JSON, nullable=True)   # List of exclusions that were checked
    # Format: [
    # {
    # "signal_type": "industry",
    # "signal_value": "Retail",
    # "excluded": false  # This value was NOT excluded, so target passed
    # },
    # ...
    # ]
    
    # Location affinity details
    location_affinity_score = Column(Float, nullable=True)   # 0.0 to 1.0
    location_affinity_details = Column(JSON, nullable=True)   # Detailed location affinity breakdown
    # Format: {
    # "score": 0.92,
    # "distance_km": 5.2,
    # "within_radius": true,
    # "within_polygon": false,
    # "signal_match": true,
    # "matching_signals": ["urban", "coastal"]
    # }
    
    # Confidence levels
    confidence_level = Column(String(50), nullable=True)   # "high", "medium", "low"
    confidence_breakdown = Column(JSON, nullable=True)   # Per-signal confidence
    # Format: {
    # "overall": "high",
    # "location": "high",
    # "industry": "high",
    # "job_title": "medium"
    # }
    
    # Additional metadata
    matching_metadata = Column(JSON, nullable=True)   # Additional matching context
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", backref="target_traces")
    persona = relationship("Persona", backref="target_traces")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_target_trace_user_id', 'user_id'),
        Index('idx_target_trace_target_id', 'target_id'),
        Index('idx_target_trace_target_type', 'target_type'),
        Index('idx_target_trace_persona_id', 'persona_id'),
        Index('idx_target_trace_user_target', 'user_id', 'target_id', 'target_type'),   # For lookups
    )
    
    def __repr__(self):
        return f"<TargetTrace(id={self.id}, target_id='{self.target_id}', target_type='{self.target_type}', score={self.overall_score})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "target_id": self.target_id,
            "target_type": self.target_type,
            "user_id": self.user_id,
            "persona_id": self.persona_id,
            "overall_score": self.overall_score,
            "signals_used": self.signals_used,
            "signal_weights": self.signal_weights,
            "signal_exclusions": self.signal_exclusions,
            "location_affinity_score": self.location_affinity_score,
            "location_affinity_details": self.location_affinity_details,
            "confidence_level": self.confidence_level,
            "confidence_breakdown": self.confidence_breakdown,
            "matching_metadata": self.matching_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
