"""
MODEL: skill_execution_log
PURPOSE: Log skill runs — skill_name, execution_time, token_usage, errors (PostgreSQL)
"""
from sqlalchemy import Column, Integer, String, Text, Index, JSON
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from src.db.base import Base


class SkillExecutionLog(Base):
    """Per-skill execution log for observability."""

    __tablename__ = "skill_execution_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    workflow_id = Column(String(64), nullable=True, index=True)
    run_id = Column(String(64), nullable=False, index=True)
    skill_name = Column(String(128), nullable=False, index=True)
    execution_time_ms = Column(Integer, nullable=True)
    token_usage = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (Index("ix_skill_execution_logs_run_skill", "run_id", "skill_name"),)
