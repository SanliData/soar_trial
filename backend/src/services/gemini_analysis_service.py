"""
SERVICE: gemini_analysis_service
PURPOSE: Google Gemini API (Vertex AI) integration for text analysis and company intelligence
ENCODING: UTF-8 WITHOUT BOM
"""

import os
from typing import Dict, List, Optional, Any
import json

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    GEMINI_AVAILABLE = True
    GEMINI_MODE = "vertex"
except ImportError:
    try:
        import google.generativeai as genai
        GEMINI_AVAILABLE = True
        GEMINI_MODE = "genai"
    except ImportError:
        GEMINI_AVAILABLE = False
        GEMINI_MODE = None


class GeminiAnalysisService:
    """
    Service for analyzing text using Google Gemini API (Vertex AI).
    Creates Company Intelligence reports from raw research data.
    """
    
    def __init__(self):
        """Initialize Gemini Analysis Service."""
        self.model = None
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        
        if GEMINI_AVAILABLE:
            try:
                if GEMINI_MODE == "genai" and self.api_key:
                    # Use Generative AI SDK (API key)
                    genai.configure(api_key=self.api_key)
                    self.model = GenerativeModel("gemini-pro")
                    self.mode = "genai"
                elif self.project_id:
                    # Use Vertex AI (project-based)
                    vertexai.init(project=self.project_id, location=self.location)
                    self.model = GenerativeModel("gemini-pro")
                    self.mode = "vertex"
                else:
                    self.model = None
                    self.mode = None
            except Exception as e:
                print(f"Warning: Could not initialize Gemini API: {e}")
                self.model = None
                self.mode = None
        else:
            self.model = None
            self.mode = None
    
    def is_available(self) -> bool:
        """Check if Gemini API is available and configured."""
        return GEMINI_AVAILABLE and self.model is not None
    
    def analyze_company_research(
        self,
        company_name: str,
        raw_research_text: str,
        locale: str = "en"
    ) -> Dict[str, Any]:
        """
        Analyze company research text and create Company Intelligence report.
        
        Args:
            company_name: Name of the company
            raw_research_text: Raw text from web research
        
        Returns:
            Dictionary containing:
                - success: bool
                - company_intelligence: Company Intelligence report
                - error: Error message if any
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Google Gemini API is not available. Please install google-generativeai or vertexai and configure credentials."
            }
        
        try:
            # Language mapping for Gemini prompts
            language_map = {
                "tr": "Turkish",
                "en": "English",
                "de": "German",
                "es": "Spanish"
            }
            language = language_map.get(locale, "English")
            
            # Create prompt for company analysis
            prompt = f"""
Analyze the following research data about the company "{company_name}" and create a comprehensive Company Intelligence report.

IMPORTANT: Respond in {language} language.

Research Data:
{raw_research_text}

Please provide a structured analysis in JSON format with the following fields:
1. "business_activity": A clear description of what the company does (main business activities, products, services)
2. "employee_count": Estimated number of employees (if available, otherwise "unknown")
3. "technology_stack": List of technologies, tools, platforms mentioned (if any)
4. "industry": Primary industry sector
5. "key_insights": List of 3-5 key insights about the company
6. "summary": A brief summary paragraph (2-3 sentences)

Respond ONLY with valid JSON, no additional text. All text content should be in {language}.
"""
            
            # Generate response
            if self.mode == "genai":
                response = self.model.generate_content(prompt)
                analysis_text = response.text
            elif self.mode == "vertex":
                response = self.model.generate_content(prompt)
                analysis_text = response.text
            else:
                # Fallback: return structured mock data if API not available
                return {
                    "success": True,
                    "company_intelligence": {
                        "business_activity": f"{company_name} is a company operating in the industry",
                        "employee_count": "unknown",
                        "technology_stack": [],
                        "industry": "unknown",
                        "key_insights": [
                            "Company information requires API configuration",
                            "Install google-generativeai or vertexai package",
                            "Configure GOOGLE_GEMINI_API_KEY or GOOGLE_CLOUD_PROJECT_ID"
                        ],
                        "summary": f"Analysis for {company_name} requires Gemini API configuration. Please set up credentials to get detailed intelligence."
                    },
                    "raw_analysis": "API not configured"
                }
            
            # Parse JSON response
            # Try to extract JSON from response (in case there's extra text)
            try:
                # Find JSON object in response
                start_idx = analysis_text.find("{")
                end_idx = analysis_text.rfind("}") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_text = analysis_text[start_idx:end_idx]
                    company_intelligence = json.loads(json_text)
                else:
                    # Fallback: try parsing entire response
                    company_intelligence = json.loads(analysis_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, create structured response from text
                company_intelligence = {
                    "business_activity": "Analysis in progress",
                    "employee_count": "unknown",
                    "technology_stack": [],
                    "industry": "unknown",
                    "key_insights": [analysis_text[:200]],
                    "summary": analysis_text[:500]
                }
            
            return {
                "success": True,
                "company_intelligence": company_intelligence,
                "raw_analysis": analysis_text
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error analyzing company research: {str(e)}"
            }
    
    def create_company_intelligence_report(
        self,
        company_name: str,
        raw_research_text: str,
        additional_context: Optional[Dict[str, Any]] = None,
        locale: str = "en"
    ) -> Dict[str, Any]:
        """
        Create a comprehensive Company Intelligence report.
        
        Args:
            company_name: Name of the company
            raw_research_text: Raw research text from web search
            additional_context: Additional context (industry, location, etc.)
        
        Returns:
            Complete Company Intelligence report
        """
        # Analyze research text
        analysis = self.analyze_company_research(company_name, raw_research_text, locale=locale)
        
        if not analysis.get("success"):
            return analysis
        
        # Build comprehensive report
        intelligence = analysis.get("company_intelligence", {})
        
        report = {
            "company_name": company_name,
            "intelligence": {
                "business_activity": intelligence.get("business_activity", "Unknown"),
                "employee_count": intelligence.get("employee_count", "unknown"),
                "technology_stack": intelligence.get("technology_stack", []),
                "industry": intelligence.get("industry", "unknown"),
                "key_insights": intelligence.get("key_insights", []),
                "summary": intelligence.get("summary", "")
            },
            "metadata": {
                "analysis_date": None,   # Can be set by caller
                "source": "Google Custom Search + Gemini AI",
                "confidence": "high" if intelligence.get("key_insights") else "medium"
            }
        }
        
        # Add additional context if provided
        if additional_context:
            report["metadata"].update(additional_context)
        
        return {
            "success": True,
            "report": report
        }
    
    def generate_ad_copy(
        self,
        product_name: str,
        product_description: str,
        product_category: Optional[str] = None,
        num_variations: int = 3,
        locale: str = "en"
    ) -> Dict[str, Any]:
        """
        Generate Google Ads ad copy (headlines and descriptions) using product information.
        Used for Step 8-9 campaign creation with Step 1 product data.
        
        Args:
            product_name: Product name from Step 1
            product_description: Product description from Step 1
            product_category: Optional product category
            num_variations: Number of ad variations to generate (default: 3)
        
        Returns:
            Dictionary containing:
                - success: bool
                - ad_variations: List of ad variations with headlines and descriptions
                - error: Error message if any
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Google Gemini API is not available. Please install google-generativeai or vertexai and configure credentials."
            }
        
        try:
            # Language mapping for Gemini prompts
            language_map = {
                "tr": "Turkish",
                "en": "English",
                "de": "German",
                "es": "Spanish"
            }
            language = language_map.get(locale, "English")
            
            # Create prompt for ad copy generation
            category_text = f"Category: {product_category}" if product_category else ""
            
            prompt = f"""
Generate {num_variations} different Google Ads variations for a B2B product.

IMPORTANT: All ad copy (headlines and descriptions) must be in {language} language.

Product Information:
- Name: {product_name}
- Description: {product_description}
{category_text}

For each variation, create:
1. Headline 1 (30 characters max)
2. Headline 2 (30 characters max)
3. Headline 3 (30 characters max)
4. Description (90 characters max)

Requirements:
- Focus on B2B value propositions
- Highlight benefits for businesses
- Use professional, compelling language in {language}
- Each headline should be unique and attention-grabbing
- Description should include a clear call-to-action
- All text must be in {language}

Respond ONLY with valid JSON in this format:
{{
  "ad_variations": [
    {{
      "headline_1": "...",
      "headline_2": "...",
      "headline_3": "...",
      "description": "..."
    }},
    ...
  ]
}}
"""
            
            # Generate response
            if self.mode == "genai":
                response = self.model.generate_content(prompt)
                response_text = response.text
            elif self.mode == "vertex":
                response = self.model.generate_content(prompt)
                response_text = response.text
            else:
                # Fallback: return mock ad variations
                return {
                    "success": True,
                    "ad_variations": [
                        {
                            "headline_1": f"{product_name[:28]}",
                            "headline_2": "B2B Solutions",
                            "headline_3": "Get Started Today",
                            "description": f"{product_description[:88]}"
                        }
                    ] * num_variations
                }
            
            # Parse JSON response
            try:
                # Find JSON object in response
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_text = response_text[start_idx:end_idx]
                    result = json.loads(json_text)
                    ad_variations = result.get("ad_variations", [])
                else:
                    # Fallback: try parsing entire response
                    result = json.loads(response_text)
                    ad_variations = result.get("ad_variations", [])
            except json.JSONDecodeError:
                # If JSON parsing fails, create structured response from text
                ad_variations = [
                    {
                        "headline_1": f"{product_name[:28]}",
                        "headline_2": "Professional B2B Solution",
                        "headline_3": "Contact Us Today",
                        "description": f"{product_description[:88]}"
                    }
                ] * num_variations
            
            # Validate and truncate to character limits
            for variation in ad_variations:
                variation["headline_1"] = variation.get("headline_1", "")[:30]
                variation["headline_2"] = variation.get("headline_2", "")[:30]
                variation["headline_3"] = variation.get("headline_3", "")[:30]
                variation["description"] = variation.get("description", "")[:90]
            
            return {
                "success": True,
                "ad_variations": ad_variations[:num_variations],
                "product_name": product_name,
                "raw_response": response_text
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error generating ad copy: {str(e)}"
            }

    def infer_hs_code(
        self,
        product_service: str,
        target_type: str = "",
        geography: str = "",
        industry: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Infer HS (Harmonized System) / gümrük kodu from product/service and context.
        Used when user does not provide HS code so every query has one (required for archive).
        Returns: {"hs_code": "1234" or "123456", "description": "...", "source": "ai"}
        Fallback: {"hs_code": "9999", "description": "Other / Unclassified", "source": "ai"}
        """
        fallback = {
            "hs_code": "9999",
            "description": "Other / Unclassified (AI not configured)",
            "source": "ai",
        }
        if not product_service and not target_type and not industry:
            return fallback
        prompt = f"""You are a customs/HS code expert. Given the following B2B product or service description, suggest the most appropriate HS code (Harmonized System, 4 or 6 digits) for international trade/customs.

Product or service: {product_service or "not specified"}
Target business type: {target_type or "not specified"}
Geography/region: {geography or "not specified"}
Industry: {industry or "not specified"}

Reply ONLY with valid JSON in this exact format, no other text:
{{"hs_code": "XXXX", "description": "Short customs/product description in English"}}

Use 4 or 6 digit HS code. If uncertain, use the closest chapter (2 digits) plus 2-4 more digits. Example: 8471 for computers, 8517 for phones."""

        try:
            if self.mode in ("genai", "vertex") and self.model:
                response = self.model.generate_content(prompt)
                text = (response.text or "").strip()
            else:
                return fallback
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                obj = json.loads(text[start:end])
                code = (obj.get("hs_code") or "9999").strip().replace(" ", "")[:10]
                if not code.isdigit():
                    code = "9999"
                return {
                    "hs_code": code,
                    "description": (obj.get("description") or "Other")[:200],
                    "source": "ai",
                }
        except Exception:
            pass
        return fallback


# Singleton instance
_gemini_analysis_service_instance = None


def get_gemini_analysis_service() -> GeminiAnalysisService:
    """Get or create GeminiAnalysisService singleton instance."""
    global _gemini_analysis_service_instance
    if _gemini_analysis_service_instance is None:
        _gemini_analysis_service_instance = GeminiAnalysisService()
    return _gemini_analysis_service_instance

