"""
MODEL: email_performance
PURPOSE: Sales knowledge memory — per-email performance and judge rankings
"""
from sqlalchemy import Column, Integer, String, Text, Float, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from src.db.base import Base


class EmailPerformance(Base):
    """Per-email or per-variant performance for learning."""

    __tablename__ = "email_performance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(String(64), nullable=False, index=True)
    email_variant_index = Column(Integer, nullable=True)
    subject = Column(String(512), nullable=True)
    opened = Column(Integer, nullable=False, default=0)
    replied = Column(Integer, nullable=False, default=0)
    positive = Column(Integer, nullable=False, default=0)
    judge_score = Column(Float, nullable=True)
    judge_reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (Index("ix_email_performance_campaign", "campaign_id", "created_at"),)
