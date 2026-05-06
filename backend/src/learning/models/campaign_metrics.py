"""
LEARNING: campaign_metrics model
PURPOSE: PostgreSQL model for per-campaign performance (open_rate, reply_rate, positive_interest_rate, meeting_rate)
"""
from sqlalchemy import Column, Integer, String, Numeric, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from src.db.base import Base


class CampaignMetrics(Base):
    """Per-campaign performance metrics for learning and optimization."""

    __tablename__ = "campaign_metrics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(String(64), nullable=False, index=True)
    emails_sent = Column(Integer, nullable=False, default=0)
    emails_opened = Column(Integer, nullable=False, default=0)
    replies_received = Column(Integer, nullable=False, default=0)
    positive_responses = Column(Integer, nullable=False, default=0)
    meetings_booked = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)

    # Optional context for analysis (industry, roles, etc.)
    industry = Column(String(256), nullable=True, index=True)
    location = Column(String(256), nullable=True, index=True)
    roles_snapshot = Column(String(512), nullable=True)   # JSON array as string or comma-separated

    __table_args__ = (Index("ix_campaign_metrics_campaign_id_created", "campaign_id", "created_at"),)
