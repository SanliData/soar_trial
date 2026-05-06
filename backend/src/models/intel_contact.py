"""
MODEL: intel_contact
PURPOSE: Contact in Intelligence Graph — name, role, linkedin_url, email, company_id
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship

from src.db.base import Base


class IntelContact(Base):
    """Contact linked to an intel company."""

    __tablename__ = "intel_contacts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("intel_companies.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(256), nullable=False)
    role = Column(String(128), nullable=True, index=True)
    linkedin_url = Column(String(512), nullable=True)
    email = Column(String(256), nullable=True, index=True)
    outreach_subject = Column(String(512), nullable=True)
    outreach_body = Column(Text, nullable=True)
    agent_run_id = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (Index("ix_intel_contacts_company_role", "company_id", "role"),)
