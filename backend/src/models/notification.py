"""
MODEL: notification
PURPOSE: Notification model for user notifications
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.orm import relationship
from src.db.base import Base


class Notification(Base):
    """
    Notification model for storing user notifications.
    Supports browser notifications and email notifications.
    """
    
    __tablename__ = "notifications"
    
    ***REMOVED*** Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    ***REMOVED*** Foreign key to User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    ***REMOVED*** Notification information
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  ***REMOVED*** "appointment", "lead", "campaign", "system"
    
    ***REMOVED*** Notification channels
    browser_notification_sent = Column(Boolean, default=False, nullable=False)
    email_notification_sent = Column(Boolean, default=False, nullable=False)
    
    ***REMOVED*** Status
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    is_archived = Column(Boolean, default=False, nullable=False, index=True)
    
    ***REMOVED*** Additional data
    notification_metadata = Column(JSON, nullable=True)  ***REMOVED*** Related entity IDs, links, etc.
    action_url = Column(String(512), nullable=True)  ***REMOVED*** URL to navigate when clicked
    
    ***REMOVED*** Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    ***REMOVED*** Relationship to User
    user = relationship("User", backref="notifications")
    
    ***REMOVED*** Indexes for performance
    __table_args__ = (
        Index('idx_notification_user_id', 'user_id'),
        Index('idx_notification_type', 'notification_type'),
        Index('idx_notification_created_at', 'created_at'),
        Index('idx_notification_unread', 'user_id', 'is_read'),
    )
    
    def __repr__(self):
        return f"<Notification(id={self.id}, title='{self.title}', user_id={self.user_id}, is_read={self.is_read})>"
    
    def to_dict(self):
        """
        Convert notification to dictionary.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "notification_type": self.notification_type,
            "browser_notification_sent": self.browser_notification_sent,
            "email_notification_sent": self.email_notification_sent,
            "is_read": self.is_read,
            "is_archived": self.is_archived,
            "metadata": self.notification_metadata,
            "action_url": self.action_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "read_at": self.read_at.isoformat() if self.read_at else None
        }

