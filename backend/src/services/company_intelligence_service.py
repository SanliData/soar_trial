"""
SERVICE: company_intelligence_service
PURPOSE: Orchestrates web research and AI analysis to create Company Intelligence reports
ENCODING: UTF-8 WITHOUT BOM
"""

from typing import Dict, List, Optional, Any
from src.services.web_research_service import get_web_research_service
from src.services.gemini_analysis_service import get_gemini_analysis_service
from datetime import datetime


class CompanyIntelligenceService:
    """
    Service that orchestrates web research and AI analysis to create comprehensive
    Company Intelligence reports.
    """
    
    def __init__(self):
        """Initialize Company Intelligence Service."""
        self.web_research = get_web_research_service()
        self.gemini_analysis = get_gemini_analysis_service()
    
    def research_and_analyze_company(
        self,
        company_name: str,
        industry: Optional[str] = None,
        location: Optional[str] = None,
        locale: str = "en"
    ) -> Dict[str, Any]:
        """
        Conduct deep web research and AI analysis on a company.
        
        Args:
            company_name: Name of the company to research
            industry: Industry sector (optional)
            location: Company location (optional)
        
        Returns:
            Complete Company Intelligence report
        """
        ***REMOVED*** Step 1: Conduct web research
        research_result = self.web_research.deep_research_company(
            company_name=company_name,
            industry=industry
        )
        
        if not research_result.get("success"):
            return {
                "success": False,
                "error": research_result.get("error", "Web research failed"),
                "step": "web_research"
            }
        
        research_data = research_result.get("research_data", {})
        combined_text = research_data.get("combined_raw_text", "")
        
        if not combined_text:
            return {
                "success": False,
                "error": "No research data collected",
                "step": "web_research"
            }
        
        ***REMOVED*** Step 2: Analyze with Gemini AI
        additional_context = {}
        if industry:
            additional_context["industry"] = industry
        if location:
            additional_context["location"] = location
        
        analysis_result = self.gemini_analysis.create_company_intelligence_report(
            company_name=company_name,
            raw_research_text=combined_text,
            additional_context=additional_context,
            locale=locale
        )
        
        if not analysis_result.get("success"):
            return {
                "success": False,
                "error": analysis_result.get("error", "AI analysis failed"),
                "step": "ai_analysis",
                "research_data": research_data  ***REMOVED*** Return research data even if analysis fails
            }
        
        ***REMOVED*** Step 3: Combine results
        report = analysis_result.get("report", {})
        report["research_sources"] = research_data.get("searches", [])
        report["metadata"]["analysis_date"] = datetime.utcnow().isoformat()
        
        return {
            "success": True,
            "company_intelligence": report,
            "research_summary": {
                "total_searches": research_data.get("total_searches", 0),
                "total_results": sum(
                    len(search.get("results", []))
                    for search in research_data.get("searches", [])
                )
            }
        }
    
    def batch_research_companies(
        self,
        company_names: List[str],
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Research multiple companies in batch.
        
        Args:
            company_names: List of company names
            industry: Industry sector (optional)
        
        Returns:
            Dictionary with results for each company
        """
        results = {
            "success": True,
            "companies": [],
            "errors": []
        }
        
        for company_name in company_names:
            result = self.research_and_analyze_company(
                company_name=company_name,
                industry=industry
            )
            
            if result.get("success"):
                results["companies"].append({
                    "company_name": company_name,
                    "intelligence": result.get("company_intelligence")
                })
            else:
                results["errors"].append({
                    "company_name": company_name,
                    "error": result.get("error", "Unknown error")
                })
        
        results["summary"] = {
            "total": len(company_names),
            "successful": len(results["companies"]),
            "failed": len(results["errors"])
        }
        
        return results


***REMOVED*** Singleton instance
_company_intelligence_service_instance = None


def get_company_intelligence_service() -> CompanyIntelligenceService:
    """Get or create CompanyIntelligenceService singleton instance."""
    global _company_intelligence_service_instance
    if _company_intelligence_service_instance is None:
        _company_intelligence_service_instance = CompanyIntelligenceService()
    return _company_intelligence_service_instance


