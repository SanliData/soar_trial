"""
SERVICE: web_research_service
PURPOSE: Google Custom Search API integration for deep company research
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import requests
from typing import Dict, List, Optional, Any
import json


class WebResearchService:
    """
    Service for conducting deep web research on companies using Google Custom Search API.
    """
    
    def __init__(self):
        """Initialize Web Research Service with API credentials."""
        self.api_key = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID")
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def is_available(self) -> bool:
        """Check if Google Custom Search API is configured."""
        return bool(self.api_key and self.search_engine_id)
    
    def search_company(
        self,
        company_name: str,
        additional_terms: Optional[List[str]] = None,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search for company information on the web.
        
        Args:
            company_name: Name of the company to search
            additional_terms: Additional search terms (e.g., ["about", "technology", "employees"])
            max_results: Maximum number of results to return
        
        Returns:
            Dictionary containing:
                - success: bool
                - results: List of search results with titles, snippets, links
                - raw_text: Combined text from all results
                - error: Error message if any
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Google Custom Search API is not configured. Please set GOOGLE_CUSTOM_SEARCH_API_KEY and GOOGLE_CUSTOM_SEARCH_ENGINE_ID environment variables."
            }
        
        try:
            ***REMOVED*** Build search query
            query_terms = [company_name]
            if additional_terms:
                query_terms.extend(additional_terms)
            query = " ".join(query_terms)
            
            ***REMOVED*** Prepare search parameters
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": min(max_results, 10)  ***REMOVED*** Google API max is 10 per request
            }
            
            all_results = []
            raw_text_parts = []
            
            ***REMOVED*** Make API request
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            ***REMOVED*** Extract results
            if "items" in data:
                for item in data["items"]:
                    result = {
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "link": item.get("link", ""),
                        "display_link": item.get("displayLink", "")
                    }
                    all_results.append(result)
                    raw_text_parts.append(f"{result['title']}\n{result['snippet']}")
            
            ***REMOVED*** Combine all text
            raw_text = "\n\n".join(raw_text_parts)
            
            return {
                "success": True,
                "results": all_results,
                "raw_text": raw_text,
                "query": query,
                "total_results": len(all_results)
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Error searching for company: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def deep_research_company(
        self,
        company_name: str,
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Conduct deep research on a company using multiple search queries.
        
        Args:
            company_name: Name of the company
            industry: Industry sector (optional)
        
        Returns:
            Comprehensive research results
        """
        research_data = {
            "company_name": company_name,
            "searches": []
        }
        
        ***REMOVED*** Multiple search queries for comprehensive research
        search_queries = [
            {"terms": ["about", "company"], "purpose": "general_info"},
            {"terms": ["technology", "stack", "tools"], "purpose": "technology"},
            {"terms": ["employees", "team", "size"], "purpose": "workforce"},
            {"terms": ["services", "products", "offerings"], "purpose": "offerings"},
            {"terms": ["location", "address", "headquarters"], "purpose": "location"}
        ]
        
        all_raw_text = []
        
        for search_query in search_queries:
            result = self.search_company(
                company_name=company_name,
                additional_terms=search_query["terms"],
                max_results=10
            )
            
            if result.get("success"):
                research_data["searches"].append({
                    "purpose": search_query["purpose"],
                    "results": result.get("results", []),
                    "raw_text": result.get("raw_text", "")
                })
                all_raw_text.append(result.get("raw_text", ""))
        
        ***REMOVED*** Combine all research text
        research_data["combined_raw_text"] = "\n\n---\n\n".join(all_raw_text)
        research_data["total_searches"] = len(research_data["searches"])
        
        return {
            "success": True,
            "research_data": research_data
        }


***REMOVED*** Singleton instance
_web_research_service_instance = None


def get_web_research_service() -> WebResearchService:
    """Get or create WebResearchService singleton instance."""
    global _web_research_service_instance
    if _web_research_service_instance is None:
        _web_research_service_instance = WebResearchService()
    return _web_research_service_instance


