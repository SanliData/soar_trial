"""
MONITORING: MonitoringRun model
PURPOSE: Track each monitoring agent run — ingestion_count, cluster_count, alerts_sent
"""
from sqlalchemy import Column, Integer, String, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from src.db.base import Base


class MonitoringRun(Base):
    __tablename__ = "monitoring_runs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    monitoring_run_id = Column(String(64), nullable=False, unique=True, index=True)
    events_ingested = Column(Integer, nullable=False, default=0)
    clusters_created = Column(Integer, nullable=False, default=0)
    new_incidents = Column(Integer, nullable=False, default=0)
    alerts_sent = Column(Integer, nullable=False, default=0)
    analysis_duration_ms = Column(Integer, nullable=True)
    failures_in_monitoring_pipeline = Column(Integer, nullable=False, default=0)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (Index("ix_monitoring_runs_created", "created_at"),)
