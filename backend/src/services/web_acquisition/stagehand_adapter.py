"""
SERVICE: web_acquisition.stagehand_adapter
PURPOSE: Browserbase Stagehand adapter for web acquisition
ENCODING: UTF-8 WITHOUT BOM

Optional integration with Browserbase Stagehand.
Controlled by SOAR_ENABLE_STAGEHAND feature flag.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from src.services.web_acquisition.interfaces import (
    BusinessAcquired,
    ContactAcquired,
    EvidenceSourceInfo,
    AcquisitionJobResult,
    CoverageReport
)
from src.services.web_acquisition.compliance import (
    SourcesPolicy,
    get_rate_limiter
)

logger = logging.getLogger(__name__)

***REMOVED*** Feature flag
STAGEHAND_ENABLED = os.getenv("SOAR_ENABLE_STAGEHAND", "false").lower() == "true"
STAGEHAND_API_KEY = os.getenv("BROWSERBASE_API_KEY", "")
STAGEHAND_API_URL = os.getenv("BROWSERBASE_API_URL", "https://www.browserbase.com/v1")


class StagehandAdapter:
    """
    Adapter for Browserbase Stagehand API.
    Provides dry-run mode when disabled.
    """
    
    def __init__(self):
        """Initialize Stagehand adapter."""
        self.enabled = STAGEHAND_ENABLED and bool(STAGEHAND_API_KEY)
        self.api_key = STAGEHAND_API_KEY if self.enabled else None
        self.api_url = STAGEHAND_API_URL
        self.rate_limiter = get_rate_limiter()
    
    def is_enabled(self) -> bool:
        """Check if Stagehand is enabled."""
        return self.enabled
    
    async def acquire_data(
        self,
        target_type: str,
        geography: Optional[Dict[str, Any]],
        sources_policy: str,
        max_results: int,
        plan_id: str
    ) -> AcquisitionJobResult:
        """
        Acquire data using Stagehand (or return mocked results in dry-run).
        
        Args:
            target_type: Type of targets ("businesses", "contacts", "both")
            geography: Geography filter
            sources_policy: Sources policy ("official_only" or "public_web")
            max_results: Maximum results (capped to 100)
            plan_id: Plan ID for tracking
            
        Returns:
            AcquisitionJobResult with acquired data
        """
        if not self.enabled:
            ***REMOVED*** Dry-run mode: return mocked results
            return self._mock_acquisition(target_type, geography, sources_policy, max_results)
        
        ***REMOVED*** Real Stagehand integration would go here
        ***REMOVED*** For now, return mocked results as placeholder
        logger.warning("Stagehand enabled but not yet implemented - returning mocked results")
        return self._mock_acquisition(target_type, geography, sources_policy, max_results)
    
    def _mock_acquisition(
        self,
        target_type: str,
        geography: Optional[Dict[str, Any]],
        sources_policy: str,
        max_results: int
    ) -> AcquisitionJobResult:
        """
        Generate mocked acquisition results for testing/dry-run.
        
        Args:
            target_type: Type of targets
            geography: Geography filter
            sources_policy: Sources policy
            max_results: Maximum results
            
        Returns:
            Mocked AcquisitionJobResult
        """
        businesses: List[BusinessAcquired] = []
        contacts: List[ContactAcquired] = []
        evidence: List[EvidenceSourceInfo] = []
        
        ***REMOVED*** Mock official sources
        if SourcesPolicy.validate_sources_policy(sources_policy):
            ***REMOVED*** Generate mock businesses
            if target_type in ["businesses", "both"]:
                mock_businesses = min(5, max_results)  ***REMOVED*** Max 5 for mock
                for i in range(mock_businesses):
                    businesses.append(BusinessAcquired(
                        name=f"Mock Company {i+1}",
                        address=f"{geography.get('region', 'Istanbul') if geography else 'Istanbul'}",
                        website=f"https://mockcompany{i+1}.com",
                        phone=f"+90 212 {100+i} {2000+i}",
                        industry="Technology",
                        metadata={"source": "mock", "policy": sources_policy}
                    ))
                
                evidence.append(EvidenceSourceInfo(
                    domain="mockcompany1.com",
                    url="https://mockcompany1.com",
                    source_type="company_website",
                    businesses_found=mock_businesses,
                    contacts_found=0
                ))
            
            ***REMOVED*** Generate mock contacts
            if target_type in ["contacts", "both"]:
                mock_contacts = min(3, max_results - len(businesses))
                for i in range(mock_contacts):
                    contacts.append(ContactAcquired(
                        name=f"Mock Contact {i+1}",
                        email=f"contact{i+1}@mockcompany1.com",
                        phone=f"+90 212 {300+i} {4000+i}",
                        job_title=["CTO", "Director", "Manager"][i % 3],
                        department="Technology",
                        seniority=["C-Level", "Director", "Manager"][i % 3],
                        company_name=f"Mock Company {i+1}",
                        metadata={
                            "source": "mock",
                            "policy": sources_policy,
                            "buying_committee": True
                        }
                    ))
                
                if evidence:
                    evidence[0].contacts_found = mock_contacts
        
        ***REMOVED*** Build coverage report
        emails = sum(1 for c in contacts if c.email)
        phones = sum(1 for c in contacts if c.phone) + sum(1 for b in businesses if b.phone)
        websites = sum(1 for b in businesses if b.website)
        
        coverage_report = CoverageReport(
            businesses_found=len(businesses),
            contacts_found=len(contacts),
            emails=emails,
            phones=phones,
            websites=websites,
            is_capped=len(businesses) + len(contacts) >= max_results,
            capped_at=max_results if len(businesses) + len(contacts) >= max_results else None
        )
        
        return AcquisitionJobResult(
            businesses=businesses,
            contacts=contacts,
            evidence=evidence,
            coverage_report=coverage_report
        )


***REMOVED*** Global adapter instance
_stagehand_adapter: Optional[StagehandAdapter] = None


def get_stagehand_adapter() -> StagehandAdapter:
    """Get global Stagehand adapter instance."""
    global _stagehand_adapter
    if _stagehand_adapter is None:
        _stagehand_adapter = StagehandAdapter()
    return _stagehand_adapter
