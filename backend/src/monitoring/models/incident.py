"""
MONITORING: Incident model
PURPOSE: Store grouped incidents — title, root_cause, severity, status, occurrence_count
"""
from sqlalchemy import Column, Integer, String, Text, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from src.db.base import Base


class Incident(Base):
    __tablename__ = "monitoring_incidents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    incident_id = Column(String(64), nullable=False, unique=True, index=True)
    title = Column(String(512), nullable=False)
    root_cause = Column(Text, nullable=True)
    severity = Column(String(8), nullable=False, index=True)   # S1, S2, S3, S4
    status = Column(String(32), nullable=False, default="open", index=True)   # open, acknowledged, resolved
    first_seen_at = Column(DateTime(timezone=True), nullable=False, index=True)
    last_seen_at = Column(DateTime(timezone=True), nullable=False, index=True)
    affected_components = Column(JSON, nullable=True)   # list of strings
    occurrence_count = Column(Integer, nullable=False, default=1)
    summary = Column(Text, nullable=True)
    error_type = Column(String(128), nullable=True, index=True)
    cluster_id = Column(String(64), nullable=True, index=True)
    technical_summary = Column(Text, nullable=True)
    suggested_next_step = Column(Text, nullable=True)
    likely_files = Column(JSON, nullable=True)
    affected_endpoint = Column(String(512), nullable=True, index=True)
    affected_workflow = Column(String(256), nullable=True, index=True)
    request_ids = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)

    __table_args__ = (Index("ix_monitoring_incidents_status_severity", "status", "severity"),)
