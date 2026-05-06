"""
MODEL: exposure_conversion
PURPOSE: Soft conversion tracking (impressions, clicks, views - no lead labeling)
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.orm import relationship
from src.db.base import Base


class ExposureConversion(Base):
    """
    Exposure conversion tracking model.
    Tracks ad impressions, clicks, and content views WITHOUT labeling as "leads".
    Soft conversion metrics only - no personal identification at this stage.
    """
    
    __tablename__ = "exposure_conversions"
    
    ***REMOVED*** Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    ***REMOVED*** Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    precision_exposure_id = Column(Integer, ForeignKey("precision_exposures.id"), nullable=False, index=True)
    
    ***REMOVED*** Conversion event type
    event_type = Column(String(50), nullable=False, index=True)  ***REMOVED*** "impression", "click", "content_view"
    
    ***REMOVED*** Event context (anonymized, contextual only)
    event_context = Column(JSON, nullable=True)  ***REMOVED*** Contextual data: location, device, time, etc. (NO PII)
    
    ***REMOVED*** Aggregated metrics
    impression_count = Column(Integer, default=0, nullable=False)  ***REMOVED*** Total impressions
    click_count = Column(Integer, default=0, nullable=False)  ***REMOVED*** Total clicks
    content_view_count = Column(Integer, default=0, nullable=False)  ***REMOVED*** Total content views
    
    ***REMOVED*** Interest signals (soft conversion indicators)
    interest_score = Column(Integer, default=0, nullable=False)  ***REMOVED*** 0-100 interest score (aggregated)
    
    ***REMOVED*** Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_event_at = Column(DateTime(timezone=True), nullable=True)  ***REMOVED*** Last event timestamp
    
    ***REMOVED*** Relationships
    user = relationship("User", backref="exposure_conversions")
    precision_exposure = relationship("PrecisionExposure", backref="conversions")
    
    ***REMOVED*** Indexes for performance
    __table_args__ = (
        Index('idx_conversion_user_id', 'user_id'),
        Index('idx_conversion_exposure_id', 'precision_exposure_id'),
        Index('idx_conversion_event_type', 'event_type'),
        Index('idx_conversion_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<ExposureConversion(id={self.id}, event_type='{self.event_type}', impressions={self.impression_count})>"
    
    def to_dict(self):
        """Convert conversion tracking to dictionary (no personal identifiers)"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "precision_exposure_id": self.precision_exposure_id,
            "event_type": self.event_type,
            "event_context": self.event_context,
            "impression_count": self.impression_count,
            "click_count": self.click_count,
            "content_view_count": self.content_view_count,
            "interest_score": self.interest_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_event_at": self.last_event_at.isoformat() if self.last_event_at else None
        }
