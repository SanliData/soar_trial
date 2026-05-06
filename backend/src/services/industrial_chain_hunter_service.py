"""
SERVICE: industrial_chain_hunter_service
PURPOSE: Reverse supply chain analysis - Find manufacturers from raw materials (X -> Y -> Producer)
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import logging
import re
from typing import Dict, List, Optional, Any
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from src.services.gemini_analysis_service import get_gemini_analysis_service
from src.services.web_research_service import get_web_research_service

logger = logging.getLogger(__name__)


class IndustrialChainHunterService:
    """
    Service for reverse supply chain analysis.
    Finds manufacturers by analyzing raw materials (X) -> end products (Y) -> producers.
    """
    
    ***REMOVED*** Keywords that indicate manufacturing/production
    PRODUCER_KEYWORDS = [
        "factory", "manufacturing", "producer", "production", "bakery", "workshop",
        "facility", "plant", "mill", "manufacturer", "maker", "artisan", "craft",
        "homemade", "handmade", "our own", "we produce", "we manufacture",
        "kendi tesisimizde", "kendi üretimimiz", "kendi fırınımız", "üretim",
        "fabrika", "imalat", "üretici", "fırın", "atölye", "tesis"
    ]
    
    ***REMOVED*** Keywords that indicate reseller/retailer
    RESELLER_KEYWORDS = [
        "distributor", "wholesaler", "retailer", "reseller", "supplier",
        "importer", "exporter", "trader", "dealer", "store", "shop",
        "bayii", "distribütör", "toptancı", "perakendeci", "satıcı"
    ]
    
    def __init__(self):
        """Initialize Industrial Chain Hunter Service."""
        self.gemini_service = get_gemini_analysis_service()
        self.web_research = get_web_research_service()
    
    def analyze_raw_material_to_products(
        self,
        raw_material: str,
        locale: str = "tr"
    ) -> Dict[str, Any]:
        """
        Use Gemini AI to analyze what end products (Y) can be made from raw material (X).
        
        Args:
            raw_material: Raw material name (e.g., "Maya", "Flour", "Steel")
            locale: Language code (tr, en, de, es)
        
        Returns:
            Dictionary with list of end products and their characteristics
        """
        if not self.gemini_service.is_available():
            return {
                "success": False,
                "error": "Gemini API not available"
            }
        
        try:
            ***REMOVED*** Language mapping
            language_map = {
                "tr": "Turkish",
                "en": "English",
                "de": "German",
                "es": "Spanish"
            }
            language = language_map.get(locale, "English")
            
            prompt = f"""
Analyze the raw material "{raw_material}" and list all end products (Y) that can be manufactured from it.

IMPORTANT: Respond in {language} language.

For each end product, provide:
1. Product name
2. Industry/sector (e.g., "Food & Beverage", "Construction", "Textile")
3. Market demand level (High/Medium/Low)
4. Typical production scale (Small/Medium/Large/Industrial)
5. Key characteristics or applications

Format your response as JSON:
{{
    "raw_material": "{raw_material}",
    "end_products": [
        {{
            "name": "Product name",
            "industry": "Industry sector",
            "demand": "High/Medium/Low",
            "scale": "Small/Medium/Large/Industrial",
            "characteristics": ["characteristic1", "characteristic2"]
        }}
    ]
}}

Respond ONLY with valid JSON, no additional text. All text must be in {language}.
"""
            
            ***REMOVED*** Get AI analysis
            if hasattr(self.gemini_service, 'model') and self.gemini_service.model:
                if self.gemini_service.mode == "genai":
                    response = self.gemini_service.model.generate_content(prompt)
                    analysis_text = response.text
                elif self.gemini_service.mode == "vertex":
                    response = self.gemini_service.model.generate_content(prompt)
                    analysis_text = response.text
                else:
                    analysis_text = ""
            else:
                return {
                    "success": False,
                    "error": "Gemini model not initialized"
                }
            
            ***REMOVED*** Parse JSON response
            import json
            try:
                start_idx = analysis_text.find("{")
                end_idx = analysis_text.rfind("}") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_text = analysis_text[start_idx:end_idx]
                    result = json.loads(json_text)
                else:
                    result = json.loads(analysis_text)
                
                return {
                    "success": True,
                    "raw_material": raw_material,
                    "end_products": result.get("end_products", [])
                }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response: {e}")
                return {
                    "success": False,
                    "error": "Failed to parse AI response",
                    "raw_response": analysis_text
                }
        
        except Exception as e:
            logger.error(f"Error analyzing raw material: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_producers_for_product(
        self,
        product_name: str,
        industry: Optional[str] = None,
        locale: str = "tr"
    ) -> Dict[str, Any]:
        """
        Search for businesses selling/producing a specific product.
        Analyzes their ads and websites to determine if they are producers or resellers.
        
        Args:
            product_name: Name of the end product (Y)
            industry: Industry sector (optional)
            locale: Language code
        
        Returns:
            Dictionary with list of potential producers
        """
        try:
            ***REMOVED*** Search for businesses selling this product
            search_query = f"{product_name} manufacturer producer factory"
            if industry:
                search_query += f" {industry}"
            
            ***REMOVED*** Use web research service to find businesses
            research_result = self.web_research.deep_research_company(
                company_name=search_query,
                industry=industry
            )
            
            if not research_result.get("success"):
                return {
                    "success": False,
                    "error": "Web research failed"
                }
            
            ***REMOVED*** Extract URLs from research
            research_data = research_result.get("research_data", {})
            searches = research_data.get("searches", [])
            
            potential_producers = []
            
            for search in searches:
                results = search.get("results", [])
                for result in results[:10]:  ***REMOVED*** Limit to top 10 per search
                    url = result.get("url", "")
                    title = result.get("title", "")
                    snippet = result.get("snippet", "")
                    
                    if not url:
                        continue
                    
                    ***REMOVED*** Analyze if this is a producer
                    producer_analysis = self._analyze_producer_status(
                        url=url,
                        title=title,
                        snippet=snippet,
                        product_name=product_name
                    )
                    
                    if producer_analysis.get("is_producer", False):
                        ***REMOVED*** Try to extract address from page
                        address = self._extract_address_from_page(url)
                        
                        potential_producers.append({
                            "name": producer_analysis.get("company_name", title),
                            "url": url,
                            "address": address,  ***REMOVED*** Physical address if found
                            "confidence": producer_analysis.get("confidence", 0.5),
                            "reasoning": producer_analysis.get("reasoning", ""),
                            "keywords_found": producer_analysis.get("keywords_found", []),
                            "industry": industry or "Unknown",
                            "product": product_name
                        })
            
            return {
                "success": True,
                "product": product_name,
                "producers": potential_producers,
                "total_found": len(potential_producers)
            }
        
        except Exception as e:
            logger.error(f"Error searching producers: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _analyze_producer_status(
        self,
        url: str,
        title: str,
        snippet: str,
        product_name: str
    ) -> Dict[str, Any]:
        """
        Analyze if a business is a producer or reseller based on their content.
        
        Args:
            url: Business website URL
            title: Page title
            snippet: Search result snippet
            product_name: Product name being searched
        
        Returns:
            Dictionary with producer status analysis
        """
        try:
            ***REMOVED*** Combine all text for analysis
            combined_text = f"{title} {snippet}".lower()
            
            ***REMOVED*** Try to fetch page content for deeper analysis
            page_content = self._fetch_page_content(url)
            if page_content:
                combined_text += " " + page_content.lower()
            
            ***REMOVED*** Count producer keywords
            producer_score = 0
            keywords_found = []
            
            for keyword in self.PRODUCER_KEYWORDS:
                if keyword.lower() in combined_text:
                    producer_score += 1
                    keywords_found.append(keyword)
            
            ***REMOVED*** Count reseller keywords
            reseller_score = 0
            for keyword in self.RESELLER_KEYWORDS:
                if keyword.lower() in combined_text:
                    reseller_score += 1
            
            ***REMOVED*** Determine if producer
            is_producer = producer_score > reseller_score and producer_score >= 2
            
            ***REMOVED*** Calculate confidence
            confidence = min(1.0, producer_score / 5.0) if is_producer else 0.0
            
            ***REMOVED*** Generate reasoning
            reasoning_parts = []
            if keywords_found:
                reasoning_parts.append(f"Found producer keywords: {', '.join(keywords_found[:3])}")
            if reseller_score > 0:
                reasoning_parts.append(f"Also found {reseller_score} reseller indicators")
            if is_producer:
                reasoning_parts.append("Likely a manufacturer/producer")
            else:
                reasoning_parts.append("Appears to be a reseller/distributor")
            
            reasoning = ". ".join(reasoning_parts)
            
            ***REMOVED*** Extract company name from title or URL
            company_name = title.split(" - ")[0].split(" | ")[0]
            if len(company_name) > 100:
                company_name = company_name[:100]
            
            return {
                "is_producer": is_producer,
                "confidence": confidence,
                "reasoning": reasoning,
                "keywords_found": keywords_found,
                "producer_score": producer_score,
                "reseller_score": reseller_score,
                "company_name": company_name
            }
        
        except Exception as e:
            logger.error(f"Error analyzing producer status: {e}")
            return {
                "is_producer": False,
                "confidence": 0.0,
                "reasoning": f"Analysis error: {str(e)}",
                "keywords_found": [],
                "company_name": ""
            }
    
    def _fetch_page_content(self, url: str, max_length: int = 5000) -> Optional[str]:
        """
        Fetch and extract text content from a web page.
        
        Args:
            url: URL to fetch
            max_length: Maximum content length
        
        Returns:
            Extracted text content or None
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            ***REMOVED*** Remove script and style
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:max_length]
        
        except Exception as e:
            logger.debug(f"Could not fetch page content for {url}: {e}")
            return None
    
    def _extract_address_from_page(self, url: str) -> Optional[str]:
        """
        Extract physical address from a web page.
        
        Args:
            url: URL to fetch
        
        Returns:
            Extracted address or None
        """
        try:
            page_content = self._fetch_page_content(url, max_length=10000)
            if not page_content:
                return None
            
            ***REMOVED*** Look for common address patterns
            ***REMOVED*** Turkish addresses
            address_patterns = [
                r'(?:Adres|Address|Adresi)[:\s]+([A-ZÇĞİÖŞÜ][^,\n]{10,100})',
                r'([A-ZÇĞİÖŞÜ][^,\n]{5,50}\s+(?:Sokak|Cadde|Mahalle|Mahallesi|Bulvar|Boulevard)[^,\n]{0,50})',
                r'([0-9]{5}\s+[A-ZÇĞİÖŞÜ][^,\n]{5,50})',  ***REMOVED*** ZIP code pattern
            ]
            
            ***REMOVED*** English addresses
            address_patterns.extend([
                r'(?:Address|Location)[:\s]+([A-Z][^,\n]{10,100})',
                r'([0-9]+\s+[A-Z][^,\n]{5,50}\s+(?:Street|Avenue|Road|Boulevard)[^,\n]{0,50})',
                r'([A-Z][^,\n]{5,50},\s*[A-Z]{2}\s+[0-9]{5})',  ***REMOVED*** US address pattern
            ])
            
            for pattern in address_patterns:
                match = re.search(pattern, page_content, re.IGNORECASE)
                if match:
                    address = match.group(1).strip()
                    if len(address) > 10:  ***REMOVED*** Minimum address length
                        return address
            
            return None
        
        except Exception as e:
            logger.debug(f"Could not extract address from {url}: {e}")
            return None
    
    def hunt_manufacturers(
        self,
        raw_material: str,
        locale: str = "tr",
        min_confidence: float = 0.5
    ) -> Dict[str, Any]:
        """
        Complete workflow: X (raw material) -> Y (products) -> Producers
        
        Args:
            raw_material: Raw material name (X)
            locale: Language code
            min_confidence: Minimum confidence score for producers
        
        Returns:
            Complete analysis with all found producers
        """
        try:
            ***REMOVED*** Step 1: Analyze raw material to products
            products_analysis = self.analyze_raw_material_to_products(
                raw_material=raw_material,
                locale=locale
            )
            
            if not products_analysis.get("success"):
                return products_analysis
            
            end_products = products_analysis.get("end_products", [])
            
            ***REMOVED*** Step 2: For each product, find producers
            all_producers = []
            
            for product in end_products[:5]:  ***REMOVED*** Limit to top 5 products
                product_name = product.get("name", "")
                industry = product.get("industry", "")
                
                if not product_name:
                    continue
                
                producers_result = self.search_producers_for_product(
                    product_name=product_name,
                    industry=industry,
                    locale=locale
                )
                
                if producers_result.get("success"):
                    producers = producers_result.get("producers", [])
                    ***REMOVED*** Filter by confidence
                    filtered_producers = [
                        p for p in producers
                        if p.get("confidence", 0) >= min_confidence
                    ]
                    
                    ***REMOVED*** Add product context to each producer
                    for producer in filtered_producers:
                        producer["source_product"] = product_name
                        producer["source_industry"] = industry
                        producer["source_demand"] = product.get("demand", "Unknown")
                    
                    all_producers.extend(filtered_producers)
            
            ***REMOVED*** Remove duplicates (by URL)
            seen_urls = set()
            unique_producers = []
            for producer in all_producers:
                url = producer.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_producers.append(producer)
            
            return {
                "success": True,
                "raw_material": raw_material,
                "end_products": end_products,
                "producers": unique_producers,
                "total_producers": len(unique_producers),
                "analysis_date": None  ***REMOVED*** Can be set by caller
            }
        
        except Exception as e:
            logger.error(f"Error in hunt_manufacturers: {e}")
            return {
                "success": False,
                "error": str(e)
            }


***REMOVED*** Singleton instance
_industrial_chain_hunter_service_instance = None


def get_industrial_chain_hunter_service() -> IndustrialChainHunterService:
    """Get or create IndustrialChainHunterService singleton instance."""
    global _industrial_chain_hunter_service_instance
    if _industrial_chain_hunter_service_instance is None:
        _industrial_chain_hunter_service_instance = IndustrialChainHunterService()
    return _industrial_chain_hunter_service_instance

