"""
MODEL: user
PURPOSE: User model for authentication and user management
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import Column, Integer, String, Boolean, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from src.db.base import Base


class User(Base):
    """
    User model for storing user information.
    Supports Google OAuth2 authentication with google_id.
    """
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Email - unique and indexed for fast lookups
    email = Column(String(255), unique=True, nullable=False, index=True)
    
    # Full name
    full_name = Column(String(255), nullable=True)
    
    # Google OAuth2 ID - unique, nullable (for non-Google users in future)
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    
    # Profile picture URL from Google
    profile_picture = Column(String(512), nullable=True)
    
    # Active status - for soft delete/account deactivation
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_google_id', 'google_id'),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', google_id={self.google_id})>"
    
    def to_dict(self):
        """
        Convert user model to dictionary.
        Excludes sensitive information.
        """
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "profile_picture": self.profile_picture,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


