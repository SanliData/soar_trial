"""
MODEL: campaign_history
PURPOSE: Sales knowledge memory — campaign runs for learning engine
"""
from sqlalchemy import Column, Integer, String, Text, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from src.db.base import Base


class CampaignHistory(Base):
    """History of campaign runs for self-learning."""

    __tablename__ = "campaign_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(String(64), nullable=False, index=True)
    workflow_id = Column(String(64), nullable=True, index=True)
    industry = Column(String(256), nullable=True, index=True)
    location = Column(String(256), nullable=True, index=True)
    goal = Column(String(512), nullable=True)
    status = Column(String(32), nullable=False, default="completed", index=True)
    companies_count = Column(Integer, nullable=True)
    contacts_count = Column(Integer, nullable=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (Index("ix_campaign_history_industry_created", "industry", "created_at"),)
