"""
SERVICE: geocoding_service
PURPOSE: Convert addresses to precise Lat/Long coordinates for 10m accuracy targeting
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import logging
import requests
from typing import Dict, Optional, Tuple, Any

logger = logging.getLogger(__name__)


class GeocodingService:
    """
    Service for geocoding addresses to precise coordinates.
    Supports multiple providers: Google Geocoding API, Nominatim (OpenStreetMap), etc.
    """
    
    def __init__(self):
        """Initialize Geocoding Service."""
        self.google_api_key = os.getenv("GOOGLE_GEOCODING_API_KEY")
        self.nominatim_base_url = "https://nominatim.openstreetmap.org/search"
    
    def geocode_address(
        self,
        address: str,
        provider: str = "google"
    ) -> Dict[str, Any]:
        """
        Geocode an address to precise Lat/Long coordinates.
        
        Args:
            address: Full address string
            provider: "google" or "nominatim"
        
        Returns:
            Dictionary with:
                - success: bool
                - latitude: float
                - longitude: float
                - formatted_address: str
                - accuracy: str (e.g., "ROOFTOP", "RANGE_INTERPOLATED")
                - error: str if failed
        """
        if provider == "google":
            return self._geocode_google(address)
        elif provider == "nominatim":
            return self._geocode_nominatim(address)
        else:
            return {
                "success": False,
                "error": f"Unknown provider: {provider}"
            }
    
    def _geocode_google(self, address: str) -> Dict[str, Any]:
        """Geocode using Google Geocoding API."""
        if not self.google_api_key:
            logger.warning("Google Geocoding API key not configured, falling back to Nominatim")
            return self._geocode_nominatim(address)
        
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                "address": address,
                "key": self.google_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "OK" or not data.get("results"):
                return {
                    "success": False,
                    "error": f"Geocoding failed: {data.get('status', 'UNKNOWN_ERROR')}"
                }
            
            result = data["results"][0]
            location = result["geometry"]["location"]
            location_type = result["geometry"]["location_type"]
            
            ***REMOVED*** Map Google location types to accuracy
            accuracy_map = {
                "ROOFTOP": "ROOFTOP",  ***REMOVED*** Most accurate
                "RANGE_INTERPOLATED": "RANGE_INTERPOLATED",
                "GEOMETRIC_CENTER": "GEOMETRIC_CENTER",
                "APPROXIMATE": "APPROXIMATE"
            }
            accuracy = accuracy_map.get(location_type, "APPROXIMATE")
            
            return {
                "success": True,
                "latitude": location["lat"],
                "longitude": location["lng"],
                "formatted_address": result.get("formatted_address", address),
                "accuracy": accuracy,
                "location_type": location_type,
                "provider": "google"
            }
        
        except Exception as e:
            logger.error(f"Google geocoding error: {e}")
            ***REMOVED*** Fallback to Nominatim
            return self._geocode_nominatim(address)
    
    def _geocode_nominatim(self, address: str) -> Dict[str, Any]:
        """Geocode using Nominatim (OpenStreetMap) - Free alternative."""
        try:
            params = {
                "q": address,
                "format": "json",
                "limit": 1,
                "addressdetails": 1
            }
            
            headers = {
                "User-Agent": "FinderOS/1.0 (B2B Sales Platform)"
            }
            
            response = requests.get(
                self.nominatim_base_url,
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                return {
                    "success": False,
                    "error": "No results found"
                }
            
            result = data[0]
            
            return {
                "success": True,
                "latitude": float(result["lat"]),
                "longitude": float(result["lon"]),
                "formatted_address": result.get("display_name", address),
                "accuracy": "APPROXIMATE",  ***REMOVED*** Nominatim is less precise
                "location_type": "NOMINATIM",
                "provider": "nominatim"
            }
        
        except Exception as e:
            logger.error(f"Nominatim geocoding error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def reverse_geocode(
        self,
        latitude: float,
        longitude: float,
        provider: str = "google"
    ) -> Dict[str, Any]:
        """
        Reverse geocode coordinates to address.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            provider: "google" or "nominatim"
        
        Returns:
            Dictionary with formatted address
        """
        if provider == "google" and self.google_api_key:
            try:
                url = "https://maps.googleapis.com/maps/api/geocode/json"
                params = {
                    "latlng": f"{latitude},{longitude}",
                    "key": self.google_api_key
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("status") == "OK" and data.get("results"):
                    return {
                        "success": True,
                        "formatted_address": data["results"][0].get("formatted_address", ""),
                        "provider": "google"
                    }
            except Exception as e:
                logger.error(f"Reverse geocoding error: {e}")
        
        return {
            "success": False,
            "error": "Reverse geocoding failed"
        }


***REMOVED*** Singleton instance
_geocoding_service_instance = None


def get_geocoding_service() -> GeocodingService:
    """Get or create GeocodingService singleton instance."""
    global _geocoding_service_instance
    if _geocoding_service_instance is None:
        _geocoding_service_instance = GeocodingService()
    return _geocoding_service_instance

