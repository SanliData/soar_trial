"""
SERVICE: sales_page_audit_service
PURPOSE: AI-powered sales page audit using Gemini API
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import logging
from typing import Dict, Optional, Any, List
import requests
from bs4 import BeautifulSoup

from src.services.gemini_analysis_service import get_gemini_analysis_service

logger = logging.getLogger(__name__)


class SalesPageAuditService:
    """
    Service for auditing sales pages using AI (Gemini).
    Provides recommendations for US market optimization (LPO - Landing Page Optimization).
    """
    
    def __init__(self):
        """Initialize Sales Page Audit Service."""
        self.gemini_service = get_gemini_analysis_service()
    
    def fetch_page_content(self, url: str) -> Optional[str]:
        """
        Fetch and extract text content from a web page.
        
        Args:
            url: URL to fetch
        
        Returns:
            Extracted text content or None if failed
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:5000]   # Limit to 5000 characters for Gemini
        except Exception as e:
            logger.error(f"Error fetching page content: {e}")
            return None
    
    def audit_sales_page(
        self,
        url: str,
        target_market: str = "US",
        business_type: Optional[str] = None,
        locale: str = "en"
    ) -> Dict[str, Any]:
        """
        Audit a sales page and provide optimization recommendations.
        
        Args:
            url: Sales page URL
            target_market: Target market (default: "US")
            business_type: Type of business (optional)
        
        Returns:
            Dictionary with audit results and recommendations
        """
        try:
            # Fetch page content
            page_content = self.fetch_page_content(url)
            
            if not page_content:
                return {
                    "success": False,
                    "error": "Could not fetch page content",
                    "url": url
                }
            
            # Language mapping for Gemini prompts
            language_map = {
                "tr": "Turkish",
                "en": "English",
                "de": "German",
                "es": "Spanish"
            }
            language = language_map.get(locale, "English")
            
            # Build audit prompt
            prompt = f"""
Analyze this sales page for the {target_market} market and provide optimization recommendations.

IMPORTANT: Respond in {language} language. All recommendations and assessments must be in {language}.

Page URL: {url}
Business Type: {business_type or "Not specified"}

Page Content:
{page_content}

Please provide:
1. Trust Signals: Does the page have sufficient trust elements (testimonials, certifications, security badges, guarantees)?
2. Value Proposition: Is the value proposition clear and compelling?
3. Call-to-Action (CTA): Are CTAs prominent and action-oriented?
4. Social Proof: Are there testimonials, reviews, or case studies?
5. Pricing Clarity: Is pricing transparent and easy to understand?
6. Mobile Optimization: Is the page mobile-friendly?
7. Page Speed: Any obvious performance issues?
8. US Market Specific: Are there any US-specific trust elements (BBB, state licenses, US-based company indicators)?

Provide specific, actionable recommendations for each area. All text must be in {language}.
Format your response as JSON with the following structure:
{{
    "overall_score": 0-100,
    "trust_signals": {{
        "score": 0-100,
        "present": ["list of present trust signals"],
        "missing": ["list of missing trust signals"],
        "recommendations": ["specific recommendations"]
    }},
    "value_proposition": {{
        "score": 0-100,
        "clarity": "assessment",
        "recommendations": ["specific recommendations"]
    }},
    "cta": {{
        "score": 0-100,
        "assessment": "assessment",
        "recommendations": ["specific recommendations"]
    }},
    "social_proof": {{
        "score": 0-100,
        "present": ["list of present social proof"],
        "missing": ["list of missing social proof"],
        "recommendations": ["specific recommendations"]
    }},
    "pricing": {{
        "score": 0-100,
        "clarity": "assessment",
        "recommendations": ["specific recommendations"]
    }},
    "mobile_optimization": {{
        "score": 0-100,
        "assessment": "assessment",
        "recommendations": ["specific recommendations"]
    }},
    "us_market_specific": {{
        "score": 0-100,
        "present": ["list of present US-specific elements"],
        "missing": ["list of missing US-specific elements"],
        "recommendations": ["specific recommendations"]
    }},
    "top_priorities": ["top 3 priority recommendations"]
}}
"""
            
            # Get AI analysis
            analysis_result = self.gemini_service.analyze_text(prompt)
            
            if not analysis_result.get("success"):
                return {
                    "success": False,
                    "error": "AI analysis failed",
                    "url": url
                }
            
            # Parse AI response
            analysis_text = analysis_result.get("analysis", "")
            
            # Try to extract JSON from response
            try:
                import json
                # Find JSON in the response
                start_idx = analysis_text.find("{")
                end_idx = analysis_text.rfind("}") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = analysis_text[start_idx:end_idx]
                    audit_data = json.loads(json_str)
                else:
                    # Fallback: create structured response from text
                    audit_data = {
                        "overall_score": 70,
                        "analysis": analysis_text,
                        "top_priorities": [
                            "Review trust signals",
                            "Optimize value proposition",
                            "Improve CTA visibility"
                        ]
                    }
            except Exception as e:
                logger.warning(f"Could not parse JSON from AI response: {e}")
                audit_data = {
                    "overall_score": 70,
                    "analysis": analysis_text,
                    "top_priorities": [
                        "Review trust signals",
                        "Optimize value proposition",
                        "Improve CTA visibility"
                    ]
                }
            
            return {
                "success": True,
                "url": url,
                "target_market": target_market,
                "audit": audit_data,
                "raw_analysis": analysis_text
            }
            
        except Exception as e:
            logger.error(f"Error auditing sales page: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": url
            }


# Global instance
_sales_page_audit_service_instance = None


def get_sales_page_audit_service() -> SalesPageAuditService:
    """Get or create SalesPageAuditService singleton instance."""
    global _sales_page_audit_service_instance
    if _sales_page_audit_service_instance is None:
        _sales_page_audit_service_instance = SalesPageAuditService()
    return _sales_page_audit_service_instance


