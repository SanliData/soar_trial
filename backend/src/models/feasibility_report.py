"""
MODEL: feasibility_report
PURPOSE: Aggregated feasibility report model (preview only, no personal data)
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.orm import relationship
from src.db.base import Base


class FeasibilityReport(Base):
    """
    Feasibility report model for aggregated, anonymous preview data.
    Contains only counts - no personal identifiers or company names.
    Generated after onboarding, locked until purchase.
    """
    
    __tablename__ = "feasibility_reports"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to User (and optionally onboarding plan)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    onboarding_plan_id = Column(String(255), nullable=True, index=True)   # UUID from onboarding
    
    # Geographic filters (context only)
    geography = Column(String(255), nullable=True)   # "USA", "Turkey", etc.
    region = Column(Text, nullable=True)   # Geographic region description
    
    # Target type filters
    target_type = Column(String(100), nullable=True)   # "B2B", "B2C", etc.
    decision_roles = Column(String(500), nullable=True)   # "CEO, CTO" (roles, not names)
    
    # Aggregated counts (NO PERSONAL DATA)
    total_businesses = Column(Integer, default=0, nullable=False)   # Total businesses in region
    target_department_size = Column(String(100), nullable=True)   # "50-200 employees"
    
    # Contact availability counts
    corporate_email_count = Column(Integer, default=0, nullable=False)   # Count of businesses with corporate emails
    phone_contact_count = Column(Integer, default=0, nullable=False)   # Count with phone availability
    linkedin_profile_count = Column(Integer, default=0, nullable=False)   # Count with LinkedIn profiles (corporate)
    ad_only_reachable_count = Column(Integer, default=0, nullable=False)   # Count reachable only via ads
    
    # Additional aggregated metadata (anonymized)
    industry_distribution = Column(JSON, nullable=True)   # {"Technology": 150, "Manufacturing": 200}
    company_size_distribution = Column(JSON, nullable=True)   # {"Small": 100, "Medium": 150, "Large": 50}
    
    # Access control
    is_unlocked = Column(Integer, default=0, nullable=False)   # 0 = locked (preview), 1 = unlocked (purchased)
    unlocked_at = Column(DateTime(timezone=True), nullable=True)   # When access was purchased
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship to User
    user = relationship("User", backref="feasibility_reports")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_feasibility_user_id', 'user_id'),
        Index('idx_feasibility_plan_id', 'onboarding_plan_id'),
        Index('idx_feasibility_unlocked', 'is_unlocked'),
    )
    
    def __repr__(self):
        return f"<FeasibilityReport(id={self.id}, user_id={self.user_id}, total_businesses={self.total_businesses})>"
    
    def to_dict(self, include_unlocked: bool = False):
        """
        Convert report to dictionary.
        By default, only returns preview data (counts only).
        
        Args:
            include_unlocked: If True and is_unlocked=1, includes additional unlocked fields
        """
        result = {
            "id": self.id,
            "user_id": self.user_id,
            "onboarding_plan_id": self.onboarding_plan_id,
            "geography": self.geography,
            "region": self.region,
            "target_type": self.target_type,
            "decision_roles": self.decision_roles,
            "total_businesses": self.total_businesses,
            "target_department_size": self.target_department_size,
            "corporate_email_count": self.corporate_email_count,
            "phone_contact_count": self.phone_contact_count,
            "linkedin_profile_count": self.linkedin_profile_count,
            "ad_only_reachable_count": self.ad_only_reachable_count,
            "industry_distribution": self.industry_distribution,
            "company_size_distribution": self.company_size_distribution,
            "is_unlocked": bool(self.is_unlocked),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Only include unlocked timestamp if unlocked
        if self.is_unlocked and include_unlocked:
            result["unlocked_at"] = self.unlocked_at.isoformat() if self.unlocked_at else None
        
        return result
