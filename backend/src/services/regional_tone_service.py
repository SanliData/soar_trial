"""
SERVICE: regional_tone_service
PURPOSE: Regional tone override service for multi-language support
ENCODING: UTF-8 WITHOUT BOM

Manages regional tone variations and business communication style per region.
Supports: EN, TR, FR, DE, ES, IT, AR (Egypt)
"""

from typing import Dict, Any, Optional
from enum import Enum


class RegionalTone(Enum):
    """Regional tone variations"""
    FORMAL = "formal"
    INFORMAL = "informal"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    DIRECT = "direct"
    POLITE = "polite"


***REMOVED*** Regional tone mappings
REGIONAL_TONE_MAP = {
    "en-US": {
        "default_tone": RegionalTone.PROFESSIONAL,
        "business_style": "direct",
        "greeting_style": "professional"
    },
    "en-GB": {
        "default_tone": RegionalTone.POLITE,
        "business_style": "formal",
        "greeting_style": "polite"
    },
    "tr-TR": {
        "default_tone": RegionalTone.POLITE,
        "business_style": "respectful",
        "greeting_style": "formal"
    },
    "fr-FR": {
        "default_tone": RegionalTone.FORMAL,
        "business_style": "formal",
        "greeting_style": "polite"
    },
    "fr-CA": {
        "default_tone": RegionalTone.PROFESSIONAL,
        "business_style": "direct",
        "greeting_style": "professional"
    },
    "de-DE": {
        "default_tone": RegionalTone.DIRECT,
        "business_style": "direct",
        "greeting_style": "professional"
    },
    "es-ES": {
        "default_tone": RegionalTone.POLITE,
        "business_style": "friendly",
        "greeting_style": "warm"
    },
    "it-IT": {
        "default_tone": RegionalTone.POLITE,
        "business_style": "friendly",
        "greeting_style": "warm"
    },
    "ar-EG": {
        "default_tone": RegionalTone.FORMAL,
        "business_style": "respectful",
        "greeting_style": "formal",
        "rtl": True
    }
}


class RegionalToneService:
    """Service for managing regional tone overrides"""
    
    @staticmethod
    def get_regional_tone(locale: str) -> Dict[str, Any]:
        """
        Get regional tone configuration for a locale.
        
        Args:
            locale: Locale string (e.g., "en-US", "tr-TR", "ar-EG")
        
        Returns:
            Dictionary with tone configuration
        """
        ***REMOVED*** Try exact match first
        if locale in REGIONAL_TONE_MAP:
            return REGIONAL_TONE_MAP[locale]
        
        ***REMOVED*** Try language match (e.g., "en" for "en-AU")
        language = locale.split("-")[0] if "-" in locale else locale
        
        ***REMOVED*** Find first match with same language
        for key, value in REGIONAL_TONE_MAP.items():
            if key.startswith(language + "-"):
                return value
        
        ***REMOVED*** Default to English US if no match
        return REGIONAL_TONE_MAP["en-US"]
    
    @staticmethod
    def get_supported_locales() -> list[str]:
        """Get list of supported locales"""
        return list(REGIONAL_TONE_MAP.keys())
    
    @staticmethod
    def is_rtl(locale: str) -> bool:
        """Check if locale uses right-to-left text direction"""
        tone_config = RegionalToneService.get_regional_tone(locale)
        return tone_config.get("rtl", False)
