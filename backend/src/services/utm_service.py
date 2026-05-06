"""
SERVICE: utm_service
PURPOSE: UTM parameter generation for tracking conversion paths
ENCODING: UTF-8 WITHOUT BOM
"""

import urllib.parse
from typing import Dict, Optional, Any
from datetime import datetime


class UTMService:
    """
    Service for generating UTM tracking parameters.
    Helps track which ads, regions, and data sources drive conversions.
    """
    
    def __init__(self):
        """Initialize UTM Service."""
        pass
    
    def generate_utm_parameters(
        self,
        campaign_id: int,
        campaign_name: str,
        source: str = "finderos",
        medium: str = "cpc",
        region: Optional[str] = None,
        company_pool_id: Optional[int] = None,
        personnel_pool_id: Optional[int] = None,
        additional_params: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Generate UTM parameters for tracking.
        
        Args:
            campaign_id: Campaign ID
            campaign_name: Campaign name
            source: Traffic source (default: "finderos")
            medium: Marketing medium (default: "cpc")
            region: Target region
            company_pool_id: Company pool ID (from Step 4)
            personnel_pool_id: Personnel pool ID (from Step 7)
            additional_params: Additional custom parameters
        
        Returns:
            Dictionary of UTM parameters
        """
        utm_params = {
            "utm_source": source,
            "utm_medium": medium,
            "utm_campaign": f"finderos_{campaign_id}_{campaign_name.lower().replace(' ', '_')}",
            "utm_content": f"campaign_{campaign_id}"
        }
        
        ***REMOVED*** Add region if provided
        if region:
            utm_params["utm_term"] = region.replace(" ", "_").lower()
        
        ***REMOVED*** Add custom parameters
        if company_pool_id:
            utm_params["utm_company_pool"] = str(company_pool_id)
        
        if personnel_pool_id:
            utm_params["utm_personnel_pool"] = str(personnel_pool_id)
        
        ***REMOVED*** Add timestamp for tracking
        utm_params["utm_timestamp"] = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        
        ***REMOVED*** Add additional custom parameters
        if additional_params:
            utm_params.update(additional_params)
        
        return utm_params
    
    def build_tracked_url(
        self,
        base_url: str,
        utm_params: Dict[str, str]
    ) -> str:
        """
        Build a URL with UTM parameters.
        
        Args:
            base_url: Base URL (e.g., "https://example.com/product")
            utm_params: UTM parameters dictionary
        
        Returns:
            URL with UTM parameters appended
        """
        ***REMOVED*** Parse existing URL
        parsed = urllib.parse.urlparse(base_url)
        
        ***REMOVED*** Parse existing query parameters
        existing_params = urllib.parse.parse_qs(parsed.query)
        
        ***REMOVED*** Add UTM parameters
        for key, value in utm_params.items():
            existing_params[key] = [value]
        
        ***REMOVED*** Rebuild query string
        new_query = urllib.parse.urlencode(existing_params, doseq=True)
        
        ***REMOVED*** Reconstruct URL
        new_parsed = parsed._replace(query=new_query)
        return urllib.parse.urlunparse(new_parsed)
    
    def extract_utm_data(self, url: str) -> Dict[str, Optional[str]]:
        """
        Extract UTM parameters from a URL.
        
        Args:
            url: URL with UTM parameters
        
        Returns:
            Dictionary of extracted UTM data
        """
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        
        return {
            "utm_source": params.get("utm_source", [None])[0],
            "utm_medium": params.get("utm_medium", [None])[0],
            "utm_campaign": params.get("utm_campaign", [None])[0],
            "utm_content": params.get("utm_content", [None])[0],
            "utm_term": params.get("utm_term", [None])[0],
            "utm_company_pool": params.get("utm_company_pool", [None])[0],
            "utm_personnel_pool": params.get("utm_personnel_pool", [None])[0],
            "utm_timestamp": params.get("utm_timestamp", [None])[0]
        }


***REMOVED*** Global instance
_utm_service_instance = None


def get_utm_service() -> UTMService:
    """Get or create UTMService singleton instance."""
    global _utm_service_instance
    if _utm_service_instance is None:
        _utm_service_instance = UTMService()
    return _utm_service_instance


