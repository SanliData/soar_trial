"""
MODEL: intel_campaign
PURPOSE: Automation campaign — status, agent_run_id, payload; supports start/pause/status
"""
from sqlalchemy import Column, Integer, String, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from src.db.base import Base


class IntelCampaign(Base):
    """Campaign created by AI Sales Agent; automation engine runs it."""

    __tablename__ = "intel_campaigns"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(String(64), nullable=False, unique=True, index=True)
    agent_run_id = Column(String(64), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="active", index=True)
    goal = Column(String(512), nullable=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)
