"""
MODEL: intel_company
PURPOSE: Company Intelligence Graph — company_name, website, industry, location, technologies, description, embedding
"""
from sqlalchemy import Column, Integer, String, Text, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from src.db.base import Base


class IntelCompany(Base):
    """Company in the intelligence graph (for similarity search and agent storage)."""

    __tablename__ = "intel_companies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_name = Column(String(512), nullable=False, index=True)
    website = Column(String(512), nullable=True)
    industry = Column(String(256), nullable=True, index=True)
    location = Column(String(256), nullable=True, index=True)
    technologies = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    embedding = Column(JSON, nullable=True)
    agent_run_id = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (Index("ix_intel_companies_industry_location", "industry", "location"),)
