"""
LEARNING: learning_event model
PURPOSE: Observability — learning_run_id, campaign_id, analysis_time, insight_results
"""
from sqlalchemy import Column, Integer, String, Text, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from src.db.base import Base


class LearningEvent(Base):
    """Log of learning/analysis runs for observability."""

    __tablename__ = "learning_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    learning_run_id = Column(String(64), nullable=False, index=True)
    campaign_id = Column(String(64), nullable=True, index=True)
    event_type = Column(String(64), nullable=False, index=True)  ***REMOVED*** e.g. analyze_campaign, get_recommendations
    analysis_time_ms = Column(Integer, nullable=True)
    insight_results = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (Index("ix_learning_events_run_created", "learning_run_id", "created_at"),)
