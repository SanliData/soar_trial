***REMOVED*** -*- coding: utf-8 -*-
"""
Industry Research Service - Research which industries and companies use a product
"""

from typing import List, Dict, Optional
from backend.models.b2b_product import Product
from backend.services.b2b.product_service import product_service
import os
from backend.services.openai_client import OpenAIVisionClient


class IndustryResearchService:
    """Research which industries and companies use a product"""
    
    def __init__(self):
        self.openai_client = OpenAIVisionClient() if os.getenv("OPENAI_API_KEY") else None
    
    def research_industries_for_product(self, product_id: int) -> Dict:
        """
        Research which industries use the product
        Example: For "yeast" -> bakeries, pastry shops, burger restaurants, etc.
        """
        product = product_service.get_product_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        
        ***REMOVED*** Get target industries from product analysis
        target_industries = product.target_industries or []
        
        ***REMOVED*** If product not analyzed yet, analyze it first
        if not target_industries:
            product = product_service.understand_product(product_id)
            target_industries = product.target_industries or []
        
        ***REMOVED*** Research specific company types for each industry
        industry_details = {}
        for industry in target_industries:
            company_types = self._get_company_types_for_industry(industry, product)
            industry_details[industry] = {
                "industry": industry,
                "company_types": company_types,
                "example_companies": []  ***REMOVED*** Will be populated by company discovery
            }
        
        return {
            "product_id": product_id,
            "product_name": product.name,
            "target_industries": target_industries,
            "industry_details": industry_details
        }
    
    def _get_company_types_for_industry(self, industry: str, product: Product) -> List[str]:
        """Get specific company types for an industry"""
        ***REMOVED*** Industry to company types mapping
        industry_company_types = {
            "bakery": ["bakery", "bread factory", "pastry shop", "confectionery"],
            "restaurant": ["restaurant", "cafe", "fast food", "burger restaurant", "pizza place"],
            "pastry": ["pastry shop", "patisserie", "cake shop", "dessert shop"],
            "manufacturing": ["manufacturing company", "factory", "production facility"],
            "retail": ["retail store", "supermarket", "grocery store"],
        }
        
        ***REMOVED*** Use AI to generate more specific types if available
        if self.openai_client:
            prompt = f"""
            For product "{product.name}" in industry "{industry}",
            list specific types of companies that would use this product.
            Return as JSON array: ["company type 1", "company type 2", ...]
            """
            try:
                response = self.openai_client.analyze_text(prompt)
                ai_types = response.get("metadata", {}).get("company_types", [])
                if ai_types:
                    return ai_types
            except:
                pass
        
        ***REMOVED*** Fallback to predefined mapping
        return industry_company_types.get(industry.lower(), [industry])
    
    def get_search_keywords_for_product(self, product_id: int) -> List[str]:
        """Generate search keywords for finding companies that use the product"""
        product = product_service.get_product_by_id(product_id)
        if not product:
            return []
        
        keywords = []
        
        ***REMOVED*** Add product name variations
        keywords.append(product.name)
        if product.category:
            keywords.append(product.category)
        
        ***REMOVED*** Add industry-based keywords
        for industry in product.target_industries or []:
            keywords.append(industry)
            ***REMOVED*** Add company type keywords
            company_types = self._get_company_types_for_industry(industry, product)
            keywords.extend(company_types)
        
        return list(set(keywords))  ***REMOVED*** Remove duplicates


***REMOVED*** Global instance
industry_research_service = IndustryResearchService()

