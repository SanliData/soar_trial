"""
SERVICE: sniper_b2b_service
PURPOSE: Sniper-B2B Autonomous Sales Cycle - 10m accuracy targeting with auto persona & ad generation
ENCODING: UTF-8 WITHOUT BOM
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.services.industrial_chain_hunter_service import get_industrial_chain_hunter_service
from src.services.geocoding_service import get_geocoding_service
from src.services.gemini_analysis_service import get_gemini_analysis_service
from src.services.google_ads_service import get_google_ads_service

logger = logging.getLogger(__name__)


class SniperB2BService:
    """
    Sniper-B2B Autonomous Sales Cycle Service.
    Implements 10m accuracy targeting with automatic persona and ad copy generation.
    """
    
    def __init__(self):
        """Initialize Sniper B2B Service."""
        self.chain_hunter = get_industrial_chain_hunter_service()
        self.geocoding = get_geocoding_service()
        self.gemini = get_gemini_analysis_service()
        self.google_ads = get_google_ads_service()
    
    def execute_sniper_cycle(
        self,
        raw_material: str,
        user_id: int,
        locale: str = "tr"
    ) -> Dict[str, Any]:
        """
        Execute complete Sniper-B2B cycle: X -> Y -> Producers -> Geocode -> Personas -> Ads -> Targeting.
        
        Args:
            raw_material: Raw material (X)
            user_id: FinderOS user ID
            locale: Language code
        
        Returns:
            Complete cycle result with all generated data
        """
        try:
            ***REMOVED*** Phase 1-2: X to Y Mapping and Producer Extraction
            logger.info(f"Phase 1-2: Hunting manufacturers for {raw_material}")
            hunt_result = self.chain_hunter.hunt_manufacturers(
                raw_material=raw_material,
                locale=locale,
                min_confidence=0.6
            )
            
            if not hunt_result.get("success"):
                return {
                    "success": False,
                    "error": hunt_result.get("error", "Hunt failed"),
                    "phase": "hunt"
                }
            
            producers = hunt_result.get("producers", [])
            if not producers:
                return {
                    "success": False,
                    "error": "No producers found",
                    "phase": "hunt"
                }
            
            ***REMOVED*** Phase 3: Geocode addresses and create 10m radius targets
            logger.info(f"Phase 3: Geocoding {len(producers)} producers")
            geocoded_producers = []
            
            for producer in producers[:10]:  ***REMOVED*** Limit to top 10 for performance
                ***REMOVED*** Extract address from producer data
                address = producer.get("address") or self._extract_address_from_producer(producer)
                
                if address:
                    geocode_result = self.geocoding.geocode_address(address)
                    
                    if geocode_result.get("success"):
                        producer["coordinates"] = {
                            "latitude": geocode_result["latitude"],
                            "longitude": geocode_result["longitude"],
                            "accuracy": geocode_result.get("accuracy", "APPROXIMATE"),
                            "formatted_address": geocode_result.get("formatted_address", address)
                        }
                        producer["sniper_ready"] = True
                    else:
                        producer["sniper_ready"] = False
                        producer["geocode_error"] = geocode_result.get("error")
                else:
                    producer["sniper_ready"] = False
                    producer["geocode_error"] = "No address found"
                
                geocoded_producers.append(producer)
            
            ***REMOVED*** Phase 4: Generate Personas and Ad Copies
            logger.info("Phase 4: Generating personas and ad copies")
            enriched_producers = []
            
            for producer in geocoded_producers:
                if not producer.get("sniper_ready"):
                    enriched_producers.append(producer)
                    continue
                
                ***REMOVED*** Generate personas
                personas_result = self._generate_personas_for_company(
                    company_name=producer.get("name", ""),
                    industry=producer.get("industry", ""),
                    locale=locale
                )
                
                producer["personas"] = personas_result.get("personas", [])
                
                ***REMOVED*** Generate ad copies for each persona
                ad_copies = []
                for persona in producer["personas"]:
                    ad_copy_result = self._generate_persona_ad_copy(
                        raw_material=raw_material,
                        end_product=producer.get("source_product", ""),
                        persona=persona,
                        company_name=producer.get("name", ""),
                        locale=locale
                    )
                    
                    if ad_copy_result.get("success"):
                        ad_copies.append({
                            "persona_id": persona.get("id"),
                            "persona_name": persona.get("name"),
                            "ad_copy": ad_copy_result.get("ad_copy")
                        })
                
                producer["ad_copies"] = ad_copies
                enriched_producers.append(producer)
            
            return {
                "success": True,
                "raw_material": raw_material,
                "end_products": hunt_result.get("end_products", []),
                "producers": enriched_producers,
                "total_producers": len(enriched_producers),
                "sniper_ready_count": sum(1 for p in enriched_producers if p.get("sniper_ready")),
                "cycle_date": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error in sniper cycle: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_address_from_producer(self, producer: Dict[str, Any]) -> Optional[str]:
        """
        Extract physical address from producer data.
        Tries multiple sources: URL content, metadata, etc.
        """
        ***REMOVED*** Try to get address from producer metadata
        if producer.get("address"):
            return producer["address"]
        
        ***REMOVED*** Try to extract from URL (would need web scraping)
        ***REMOVED*** For now, return None - address should be added during producer discovery
        return None
    
    def _generate_personas_for_company(
        self,
        company_name: str,
        industry: str,
        locale: str = "tr"
    ) -> Dict[str, Any]:
        """
        Generate 2 personas for a company: 'Production Head' and 'Owner'.
        
        Args:
            company_name: Company name
            industry: Industry sector
            locale: Language code
        
        Returns:
            Dictionary with generated personas
        """
        if not self.gemini.is_available():
            ***REMOVED*** Fallback personas
            return {
                "success": True,
                "personas": [
                    {
                        "id": "production_head",
                        "name": "Production Head",
                        "job_title": "Production Manager / Head of Production",
                        "department": "Production",
                        "seniority_level": "Director",
                        "pain_points": ["Production efficiency", "Cost optimization", "Quality control"],
                        "decision_power": "High"
                    },
                    {
                        "id": "owner",
                        "name": "Company Owner",
                        "job_title": "Owner / CEO",
                        "department": "Executive",
                        "seniority_level": "C-Level",
                        "pain_points": ["Business growth", "Profitability", "Market expansion"],
                        "decision_power": "Very High"
                    }
                ]
            }
        
        try:
            language_map = {
                "tr": "Turkish",
                "en": "English",
                "de": "German",
                "es": "Spanish"
            }
            language = language_map.get(locale, "English")
            
            prompt = f"""
Generate 2 personas for a B2B company that manufactures products.

Company: {company_name}
Industry: {industry}

IMPORTANT: Respond in {language} language.

Create 2 personas:
1. "Production Head" - Person responsible for production operations
2. "Owner" - Company owner/CEO

For each persona, provide:
- job_title: Their job title
- department: Department they work in
- seniority_level: C-Level, Director, Manager, etc.
- pain_points: List of 3-5 pain points they care about
- decision_power: High, Medium, Low
- typical_concerns: What they typically worry about

Format as JSON:
{{
    "personas": [
        {{
            "id": "production_head",
            "name": "Production Head",
            "job_title": "...",
            "department": "...",
            "seniority_level": "...",
            "pain_points": ["...", "..."],
            "decision_power": "...",
            "typical_concerns": "..."
        }},
        {{
            "id": "owner",
            "name": "Owner",
            "job_title": "...",
            "department": "...",
            "seniority_level": "...",
            "pain_points": ["...", "..."],
            "decision_power": "...",
            "typical_concerns": "..."
        }}
    ]
}}

Respond ONLY with valid JSON. All text in {language}.
"""
            
            if hasattr(self.gemini, 'model') and self.gemini.model:
                if self.gemini.mode == "genai":
                    response = self.gemini.model.generate_content(prompt)
                    analysis_text = response.text
                elif self.gemini.mode == "vertex":
                    response = self.gemini.model.generate_content(prompt)
                    analysis_text = response.text
                else:
                    analysis_text = ""
            else:
                analysis_text = ""
            
            import json
            try:
                start_idx = analysis_text.find("{")
                end_idx = analysis_text.rfind("}") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_text = analysis_text[start_idx:end_idx]
                    result = json.loads(json_text)
                    return {
                        "success": True,
                        "personas": result.get("personas", [])
                    }
            except json.JSONDecodeError:
                pass
            
            ***REMOVED*** Fallback
            return {
                "success": True,
                "personas": [
                    {
                        "id": "production_head",
                        "name": "Production Head",
                        "job_title": "Production Manager",
                        "department": "Production",
                        "seniority_level": "Director",
                        "pain_points": ["Efficiency", "Cost", "Quality"],
                        "decision_power": "High"
                    },
                    {
                        "id": "owner",
                        "name": "Owner",
                        "job_title": "CEO / Owner",
                        "department": "Executive",
                        "seniority_level": "C-Level",
                        "pain_points": ["Growth", "Profit", "Expansion"],
                        "decision_power": "Very High"
                    }
                ]
            }
        
        except Exception as e:
            logger.error(f"Error generating personas: {e}")
            return {
                "success": False,
                "error": str(e),
                "personas": []
            }
    
    def _generate_persona_ad_copy(
        self,
        raw_material: str,
        end_product: str,
        persona: Dict[str, Any],
        company_name: str,
        locale: str = "tr"
    ) -> Dict[str, Any]:
        """
        Generate ad copy specifically for a persona, focusing on X efficiency in producing Y.
        
        Args:
            raw_material: Raw material (X)
            end_product: End product (Y)
            persona: Persona dictionary
            company_name: Company name
            locale: Language code
        
        Returns:
            Dictionary with generated ad copy
        """
        if not self.gemini.is_available():
            return {
                "success": False,
                "error": "Gemini not available"
            }
        
        try:
            language_map = {
                "tr": "Turkish",
                "en": "English",
                "de": "German",
                "es": "Spanish"
            }
            language = language_map.get(locale, "English")
            
            persona_name = persona.get("name", "")
            pain_points = persona.get("pain_points", [])
            
            prompt = f"""
Create a Google Ads copy for a B2B sales campaign targeting a specific persona.

Raw Material (X): {raw_material}
End Product (Y): {end_product}
Target Company: {company_name}
Target Persona: {persona_name}
Persona Pain Points: {', '.join(pain_points[:3])}

IMPORTANT: All ad copy must be in {language} language.

Create a compelling ad that:
1. Addresses the persona's pain points
2. Highlights how {raw_material} improves efficiency in producing {end_product}
3. Uses professional B2B language
4. Includes a clear call-to-action

Format as JSON:
{{
    "headline_1": "... (30 chars max)",
    "headline_2": "... (30 chars max)",
    "headline_3": "... (30 chars max)",
    "description": "... (90 chars max)",
    "focus_message": "Main value proposition for this persona"
}}

Respond ONLY with valid JSON. All text in {language}.
"""
            
            if hasattr(self.gemini, 'model') and self.gemini.model:
                if self.gemini.mode == "genai":
                    response = self.gemini.model.generate_content(prompt)
                    analysis_text = response.text
                elif self.gemini.mode == "vertex":
                    response = self.gemini.model.generate_content(prompt)
                    analysis_text = response.text
                else:
                    analysis_text = ""
            else:
                analysis_text = ""
            
            import json
            try:
                start_idx = analysis_text.find("{")
                end_idx = analysis_text.rfind("}") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_text = analysis_text[start_idx:end_idx]
                    result = json.loads(json_text)
                    return {
                        "success": True,
                        "ad_copy": result
                    }
            except json.JSONDecodeError:
                pass
            
            return {
                "success": False,
                "error": "Failed to parse ad copy"
            }
        
        except Exception as e:
            logger.error(f"Error generating persona ad copy: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_sniper_campaign(
        self,
        producer: Dict[str, Any],
        customer_id: str,
        user_id: int,
        raw_material: str,
        locale: str = "tr"
    ) -> Dict[str, Any]:
        """
        Create a Google Ads campaign with 10m radius targeting for a producer.
        
        Args:
            producer: Producer dictionary with coordinates
            customer_id: Google Ads customer ID
            user_id: FinderOS user ID
            raw_material: Raw material (X)
            locale: Language code
        
        Returns:
            Campaign creation result
        """
        if not producer.get("sniper_ready"):
            return {
                "success": False,
                "error": "Producer not sniper-ready (no coordinates)"
            }
        
        coordinates = producer.get("coordinates", {})
        latitude = coordinates.get("latitude")
        longitude = coordinates.get("longitude")
        
        if not latitude or not longitude:
            return {
                "success": False,
                "error": "Missing coordinates"
            }
        
        ***REMOVED*** Use Google Ads service to create campaign with 10m radius location targeting
        ***REMOVED*** Prepare product info and ad data (would come from Step 1 and Step 8)
        product_info = {
            "name": raw_material,
            "description": f"Raw material for {producer.get('source_product', 'production')}"
        }
        
        ***REMOVED*** Get ad copy from producer's generated ad copies
        ad_copies = producer.get("ad_copies", [])
        if ad_copies:
            ad_data = {
                "ad_content": ad_copies[0].get("ad_copy", {}).get("description", ""),
                "headlines": [
                    ad_copies[0].get("ad_copy", {}).get("headline_1", ""),
                    ad_copies[0].get("ad_copy", {}).get("headline_2", ""),
                    ad_copies[0].get("ad_copy", {}).get("headline_3", "")
                ]
            }
        else:
            ad_data = {
                "ad_content": f"Optimize {raw_material} for {producer.get('source_product', 'production')}"
            }
        
        ***REMOVED*** Create campaign with 10m radius targeting
        campaign_result = self.google_ads.create_search_campaign_with_ads(
            customer_id=customer_id,
            user_id=user_id,
            campaign_name=f"Sniper: {producer.get('name', 'Producer')} - {raw_material}",
            product_info=product_info,
            ad_data=ad_data,
            budget_amount_micros=10000000,  ***REMOVED*** $10/day
            conversion_strategy="appointment",
            locale=locale,
            target_coordinates={
                "latitude": latitude,
                "longitude": longitude
            }
        )
        
        if campaign_result.get("success"):
            return {
                "success": True,
                "message": "Sniper campaign created with 10m radius targeting",
                "campaign_id": campaign_result.get("campaign_id"),
                "target_location": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "radius_meters": 10
                }
            }
        else:
            return {
                "success": False,
                "error": campaign_result.get("error", "Campaign creation failed")
            }


***REMOVED*** Singleton instance
_sniper_b2b_service_instance = None


def get_sniper_b2b_service() -> SniperB2BService:
    """Get or create SniperB2BService singleton instance."""
    global _sniper_b2b_service_instance
    if _sniper_b2b_service_instance is None:
        _sniper_b2b_service_instance = SniperB2BService()
    return _sniper_b2b_service_instance

