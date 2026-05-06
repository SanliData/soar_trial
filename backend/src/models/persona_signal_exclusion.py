"""
MODEL: persona_signal_exclusion
PURPOSE: Signal exclusion model for Living Persona Engine
ENCODING: UTF-8 WITHOUT BOM

Allows users to exclude specific signal values from persona matching.
Supports both global (user-level) and persona-specific exclusions.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Index, Text
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from src.db.base import Base


class PersonaSignalExclusion(Base):
    """
    Signal exclusion model for Living Persona Engine.
    Allows exclusion of specific signal values from persona matching.
    
    - user_id + persona_id = persona-specific exclusion
    - user_id + persona_id=None = global (user-level) exclusion
    """
    
    __tablename__ = "persona_signal_exclusions"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=True, index=True)   # None = global exclusion
    
    # Exclusion configuration
    signal_type = Column(String(100), nullable=False)   # "location", "industry", "job_title", etc.
    signal_value = Column(String(500), nullable=False)   # Specific value to exclude (e.g., "Retail", "Istanbul")
    
    # Metadata
    exclusion_reason = Column(Text, nullable=True)   # Optional reason for exclusion
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", backref="persona_signal_exclusions")
    persona = relationship("Persona", backref="signal_exclusions")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_signal_exclusion_user_id', 'user_id'),
        Index('idx_signal_exclusion_persona_id', 'persona_id'),
        Index('idx_signal_exclusion_type', 'signal_type'),
        Index('idx_signal_exclusion_value', 'signal_value'),
        Index('idx_signal_exclusion_user_type_value', 'user_id', 'signal_type', 'signal_value'),   # For lookups
    )
    
    def __repr__(self):
        scope = f"persona_{self.persona_id}" if self.persona_id else "global"
        return f"<PersonaSignalExclusion(id={self.id}, user_id={self.user_id}, scope={scope}, signal_type='{self.signal_type}', signal_value='{self.signal_value}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "persona_id": self.persona_id,
            "signal_type": self.signal_type,
            "signal_value": self.signal_value,
            "exclusion_reason": self.exclusion_reason,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
