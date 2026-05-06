"""
MODEL: industry_performance
PURPOSE: Sales knowledge memory — industry-level aggregates for learning
"""
from sqlalchemy import Column, Integer, String, Float, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, Date

from src.db.base import Base


class IndustryPerformance(Base):
    """Industry (and optional location) performance aggregates."""

    __tablename__ = "industry_performance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    industry = Column(String(256), nullable=False, index=True)
    location = Column(String(256), nullable=True, index=True)
    emails_sent = Column(Integer, nullable=False, default=0)
    emails_opened = Column(Integer, nullable=False, default=0)
    replies_received = Column(Integer, nullable=False, default=0)
    positive_responses = Column(Integer, nullable=False, default=0)
    open_rate = Column(Float, nullable=True)
    reply_rate = Column(Float, nullable=True)
    period_start = Column(Date, nullable=True, index=True)
    period_end = Column(Date, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (Index("ix_industry_performance_industry_location", "industry", "location"),)
