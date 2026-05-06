***REMOVED*** -*- coding: utf-8 -*-
"""
Company Discovery Service - Automatically find companies from web/official sites
"""

from typing import List, Dict, Optional
from backend.models.b2b_company import Company
from backend.models.b2b_product import Product
from backend.services.b2b.customer_pool_service import customer_pool_service
from backend.services.b2b.industry_research_service import industry_research_service
from backend.services.b2b.product_service import product_service
import requests
import os


class CompanyDiscoveryService:
    """Automatically discover companies from web and official sites"""
    
    def __init__(self):
        self.google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.google_places_api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    
    def discover_companies_for_product(
        self,
        product_id: int,
        location: Optional[str] = None,  ***REMOVED*** City, country, etc.
        limit: int = 100
    ) -> List[Company]:
        """
        Discover companies that use the product
        Searches web, Google Maps, official sites, etc.
        """
        product = product_service.get_product_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        
        ***REMOVED*** Get search keywords
        keywords = industry_research_service.get_search_keywords_for_product(product_id)
        
        ***REMOVED*** Get industry research
        industry_research = industry_research_service.research_industries_for_product(product_id)
        
        discovered_companies = []
        
        ***REMOVED*** Method 1: Google Places API (if available)
        if self.google_places_api_key:
            companies = self._discover_via_google_places(keywords, location, limit)
            discovered_companies.extend(companies)
        
        ***REMOVED*** Method 2: Google Maps Search (if available)
        if self.google_maps_api_key and len(discovered_companies) < limit:
            companies = self._discover_via_google_maps(keywords, location, limit - len(discovered_companies))
            discovered_companies.extend(companies)
        
        ***REMOVED*** Method 3: Web scraping (basic, for official sites)
        ***REMOVED*** Note: This is a simplified version. Real implementation would need
        ***REMOVED*** proper web scraping with rate limiting and respect for robots.txt
        
        ***REMOVED*** Create company records
        created_companies = []
        for company_data in discovered_companies:
            company = customer_pool_service.create_company(
                name=company_data.get("name", ""),
                official_name=company_data.get("official_name"),
                website=company_data.get("website"),
                industry=company_data.get("industry"),
                address_line1=company_data.get("address_line1"),
                city=company_data.get("city"),
                state=company_data.get("state"),
                postal_code=company_data.get("postal_code"),
                country=company_data.get("country"),
                metadata={"source": "auto_discovery", "product_id": product_id}
            )
            company.product_id = product_id
            created_companies.append(company)
        
        return created_companies
    
    def _discover_via_google_places(
        self,
        keywords: List[str],
        location: Optional[str],
        limit: int
    ) -> List[Dict]:
        """Discover companies via Google Places API"""
        if not self.google_places_api_key:
            return []
        
        companies = []
        
        for keyword in keywords[:5]:  ***REMOVED*** Limit keyword searches
            try:
                ***REMOVED*** Google Places Text Search
                url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
                query = keyword
                if location:
                    query += f" in {location}"
                
                params = {
                    "query": query,
                    "key": self.google_places_api_key,
                    "type": "establishment"
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for place in data.get("results", [])[:limit]:
                        company_data = {
                            "name": place.get("name"),
                            "address_line1": place.get("formatted_address", "").split(",")[0] if place.get("formatted_address") else None,
                            "city": self._extract_city_from_address(place.get("formatted_address", "")),
                            "country": self._extract_country_from_address(place.get("formatted_address", "")),
                            "website": place.get("website"),
                            "industry": keyword,
                            "latitude": place.get("geometry", {}).get("location", {}).get("lat"),
                            "longitude": place.get("geometry", {}).get("location", {}).get("lng"),
                        }
                        companies.append(company_data)
            except Exception as e:
                print(f"Google Places API error: {e}")
        
        return companies[:limit]
    
    def _discover_via_google_maps(
        self,
        keywords: List[str],
        location: Optional[str],
        limit: int
    ) -> List[Dict]:
        """Discover companies via Google Maps Geocoding API"""
        ***REMOVED*** Similar to Places API but using Geocoding
        ***REMOVED*** This is a simplified version
        return []
    
    def _extract_city_from_address(self, address: str) -> Optional[str]:
        """Extract city from formatted address"""
        if not address:
            return None
        parts = address.split(",")
        if len(parts) >= 2:
            return parts[-2].strip()
        return None
    
    def _extract_country_from_address(self, address: str) -> Optional[str]:
        """Extract country from formatted address"""
        if not address:
            return None
        parts = address.split(",")
        if len(parts) >= 1:
            return parts[-1].strip()
        return None


***REMOVED*** Global instance
company_discovery_service = CompanyDiscoveryService()

