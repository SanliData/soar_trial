"""
MODEL: agent_run_log
PURPOSE: Store agent workflow step logs (agent_run_id, workflow_step, token_usage, latency, errors)
"""
from sqlalchemy import Column, Integer, String, Text, Index, JSON
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from src.db.base import Base


class AgentRun(Base):
    """Agent run metadata (sales_engine, etc.)."""

    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    agent_run_id = Column(String(64), nullable=False, unique=True, index=True)
    workflow_type = Column(String(64), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="running")
    input_payload = Column(JSON, nullable=True)
    output_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)


class AgentRunLog(Base):
    """Per-step log for observability (workflow_step, token_usage, latency, errors)."""

    __tablename__ = "agent_run_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    agent_run_id = Column(String(64), nullable=False, index=True)
    workflow_step = Column(String(128), nullable=False, index=True)
    token_usage = Column(JSON, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (Index("ix_agent_run_logs_run_step", "agent_run_id", "workflow_step"),)
