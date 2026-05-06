"""
MODEL: persona_signal_weight
PURPOSE: Signal weighting model for Living Persona Engine
ENCODING: UTF-8 WITHOUT BOM

Allows users to manually set weights for different signal types in persona matching.
Supports both global (user-level) and persona-specific weights.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Index, Text
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from src.db.base import Base


class PersonaSignalWeight(Base):
    """
    Signal weighting model for Living Persona Engine.
    Allows manual weighting of signals for persona matching.
    
    - user_id + persona_id = persona-specific weight
    - user_id + persona_id=None = global (user-level) weight
    """
    
    __tablename__ = "persona_signal_weights"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=True, index=True)   # None = global weight
    
    # Signal configuration
    signal_type = Column(String(100), nullable=False)   # "location", "industry", "job_title", "department", etc.
    weight = Column(Float, default=1.0, nullable=False)   # 0.0 to 10.0
    
    # Metadata
    description = Column(Text, nullable=True)   # Optional description of why this weight was set
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", backref="persona_signal_weights")
    persona = relationship("Persona", backref="signal_weights")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_signal_weight_user_id', 'user_id'),
        Index('idx_signal_weight_persona_id', 'persona_id'),
        Index('idx_signal_weight_type', 'signal_type'),
        Index('idx_signal_weight_user_type', 'user_id', 'signal_type'),   # For global weight lookups
        Index('idx_signal_weight_persona_type', 'persona_id', 'signal_type'),   # For persona-specific lookups
    )
    
    def __repr__(self):
        scope = f"persona_{self.persona_id}" if self.persona_id else "global"
        return f"<PersonaSignalWeight(id={self.id}, user_id={self.user_id}, scope={scope}, signal_type='{self.signal_type}', weight={self.weight})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "persona_id": self.persona_id,
            "signal_type": self.signal_type,
            "weight": self.weight,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
