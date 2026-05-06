"""
ROUTER: company_research_router
PURPOSE: API endpoints for company research and intelligence
ENCODING: UTF-8 WITHOUT BOM
"""

import logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from src.services.company_intelligence_service import get_company_intelligence_service
from src.middleware.locale_middleware import get_locale_from_request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/research", tags=["company-research"])


class CompanyResearchRequest(BaseModel):
    company_name: str
    industry: Optional[str] = None
    location: Optional[str] = None


class BatchResearchRequest(BaseModel):
    company_names: List[str]
    industry: Optional[str] = None


@router.post("/company-intelligence")
async def get_company_intelligence(
    request: CompanyResearchRequest,
    http_request: Request
):
    """
    Conduct deep web research and AI analysis on a company.
    Returns a comprehensive Company Intelligence report.
    """
    # Get locale from request
    locale = get_locale_from_request(http_request)
    
    # Validate required fields
    if not request.company_name or not request.company_name.strip():
        raise HTTPException(
            status_code=422,
            detail="company_name is required and cannot be empty"
        )
    
    service = get_company_intelligence_service()
    
    try:
        result = service.research_and_analyze_company(
            company_name=request.company_name,
            industry=request.industry,
            location=request.location,
            locale=locale
        )
        
        if not result.get("success"):
            error = result.get("error", "Research failed")
            step = result.get("step", "unknown")
            
            # Check if it's a configuration error (should return 503)
            if "not configured" in error.lower() or "not available" in error.lower() or step == "web_research":
                # Check if web research service is available
                from src.services.web_research_service import get_web_research_service
                web_research = get_web_research_service()
                if not web_research.is_available():
                    raise HTTPException(
                        status_code=503,
                        detail="Research service is not configured. Please set GOOGLE_CUSTOM_SEARCH_API_KEY and GOOGLE_CUSTOM_SEARCH_ENGINE_ID environment variables."
                    )
                
                # Check if Gemini service is available
                from src.services.gemini_analysis_service import get_gemini_analysis_service
                gemini_analysis = get_gemini_analysis_service()
                if not gemini_analysis.is_available():
                    raise HTTPException(
                        status_code=503,
                        detail="AI analysis service is not configured. Please configure Google Gemini API credentials."
                    )
            
            # Other errors: return 500 with logged error
            logger.error(f"Company research failed: {error} (step: {step})", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Research failed: {error}"
            )
        
        return {
            "success": True,
            "data": result.get("company_intelligence"),
            "research_summary": result.get("research_summary")
        }
    except HTTPException:
        # Re-raise HTTP exceptions (503, 422, etc.)
        raise
    except Exception as e:
        # Unexpected errors: log and return 500
        logger.error(f"Unexpected error in company research: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error during research"
        )


@router.post("/batch-research")
async def batch_research_companies(request: BatchResearchRequest):
    """
    Research multiple companies in batch.
    """
    service = get_company_intelligence_service()
    
    result = service.batch_research_companies(
        company_names=request.company_names,
        industry=request.industry
    )
    
    return result


@router.get("/health")
def health():
    """Check health status of research services."""
    from src.services.web_research_service import get_web_research_service
    from src.services.gemini_analysis_service import get_gemini_analysis_service
    
    web_research = get_web_research_service()
    gemini_analysis = get_gemini_analysis_service()
    
    return {
        "status": "ok",
        "domain": "company-research",
        "web_research_available": web_research.is_available(),
        "gemini_analysis_available": gemini_analysis.is_available()
    }


