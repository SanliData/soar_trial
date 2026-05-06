"""
MONITORING: IncidentEvent model
PURPOSE: Individual events linked to an incident
"""
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from src.db.base import Base


class IncidentEvent(Base):
    __tablename__ = "monitoring_incident_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    incident_id = Column(String(64), nullable=False, index=True)   # FK to Incident.incident_id
    event_message = Column(Text, nullable=True)
    module = Column(String(256), nullable=True, index=True)
    endpoint = Column(String(512), nullable=True)
    request_id = Column(String(64), nullable=True, index=True)
    raw_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (Index("ix_monitoring_incident_events_incident_created", "incident_id", "created_at"),)
