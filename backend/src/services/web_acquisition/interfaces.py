"""
SERVICE: web_acquisition.interfaces
PURPOSE: Data models and interfaces for web acquisition
ENCODING: UTF-8 WITHOUT BOM
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AcquisitionJobRequest(BaseModel):
    """
    Request model for creating an acquisition job.
    """
    plan_id: str = Field(..., description="Plan ID from PlanLifecycle")
    target_type: str = Field(..., description="Type of targets: 'businesses', 'contacts', or 'both'")
    geography: Optional[Dict[str, Any]] = Field(None, description="Geography filter (region, city, etc.)")
    sources_policy: str = Field(default="official_only", description="Sources policy: 'official_only' or 'public_web'")
    max_results: int = Field(default=100, description="Maximum results (capped to 100, or admin override)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "plan_id": "plan_abc123",
                "target_type": "both",
                "geography": {"region": "Istanbul", "country": "Turkey"},
                "sources_policy": "official_only",
                "max_results": 100
            }
        }


class BusinessAcquired(BaseModel):
    """
    Acquired business data.
    """
    name: str
    address: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    industry: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ContactAcquired(BaseModel):
    """
    Acquired contact data (professional B2B level only).
    """
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    seniority: Optional[str] = None  ***REMOVED*** "C-Level", "Director", "Manager", etc.
    company_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None  ***REMOVED*** role, department, seniority, buying_committee only


class EvidenceSourceInfo(BaseModel):
    """
    Evidence source information.
    """
    domain: str
    url: Optional[str] = None
    source_type: str  ***REMOVED*** "government", "municipality", "chamber", "company_website", "public_directory"
    businesses_found: int = 0
    contacts_found: int = 0


class CoverageReport(BaseModel):
    """
    Coverage report showing acquisition statistics.
    """
    businesses_found: int = Field(default=0, description="Total businesses found")
    contacts_found: int = Field(default=0, description="Total contacts found")
    emails: int = Field(default=0, description="Total email addresses found")
    phones: int = Field(default=0, description="Total phone numbers found")
    websites: int = Field(default=0, description="Total websites found")
    is_capped: bool = Field(default=False, description="True if results were capped at max_results")
    capped_at: Optional[int] = Field(None, description="The cap value that was applied")


class AcquisitionJobResult(BaseModel):
    """
    Result model for acquisition job.
    """
    businesses: List[BusinessAcquired] = Field(default_factory=list)
    contacts: List[ContactAcquired] = Field(default_factory=list)
    evidence: List[EvidenceSourceInfo] = Field(default_factory=list)
    coverage_report: CoverageReport = Field(default_factory=CoverageReport)
    
    class Config:
        json_schema_extra = {
            "example": {
                "businesses": [
                    {
                        "name": "Acme Corp",
                        "address": "123 Main St, Istanbul",
                        "website": "https://acme.com",
                        "phone": "+90 212 123 4567",
                        "industry": "Technology"
                    }
                ],
                "contacts": [
                    {
                        "name": "John Doe",
                        "email": "john@acme.com",
                        "job_title": "CTO",
                        "department": "Technology",
                        "seniority": "C-Level",
                        "company_name": "Acme Corp"
                    }
                ],
                "evidence": [
                    {
                        "domain": "acme.com",
                        "url": "https://acme.com/about",
                        "source_type": "company_website",
                        "businesses_found": 1,
                        "contacts_found": 1
                    }
                ],
                "coverage_report": {
                    "businesses_found": 1,
                    "contacts_found": 1,
                    "emails": 1,
                    "phones": 2,
                    "websites": 1,
                    "is_capped": False
                }
            }
        }
