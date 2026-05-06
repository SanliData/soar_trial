***REMOVED*** -*- coding: utf-8 -*-
"""
Address Validation Service - Address validation service
Address validation and coordinate resolution with services like Google Maps, OpenStreetMap
"""

from typing import Optional, Dict, Tuple, List
from datetime import datetime
import requests
import os
from backend.models.b2b_company import Company
from backend.services.b2b.customer_pool_service import customer_pool_service


class AddressValidationService:
    """Address validation and coordinate resolution service"""
    
    def __init__(self):
        self.google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.openstreetmap_enabled = True  ***REMOVED*** Free alternative
    
    def validate_address_google_maps(
        self,
        address_line1: str,
        city: Optional[str] = None,
        state: Optional[str] = None,
        postal_code: Optional[str] = None,
        country: Optional[str] = None
    ) -> Optional[Dict]:
        """Validate address with Google Maps API"""
        if not self.google_maps_api_key:
            return None
        
        ***REMOVED*** Build address string
        address_parts = [address_line1]
        if city:
            address_parts.append(city)
        if state:
            address_parts.append(state)
        if postal_code:
            address_parts.append(postal_code)
        if country:
            address_parts.append(country)
        
        address_string = ", ".join(address_parts)
        
        ***REMOVED*** Google Geocoding API
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address_string,
            "key": self.google_maps_api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "OK" and data.get("results"):
                result = data["results"][0]
                location = result["geometry"]["location"]
                
                return {
                    "validated": True,
                    "formatted_address": result.get("formatted_address"),
                    "latitude": location.get("lat"),
                    "longitude": location.get("lng"),
                    "location_type": result["geometry"].get("location_type"),  ***REMOVED*** ROOFTOP, RANGE_INTERPOLATED, etc.
                    "accuracy": self._calculate_accuracy(result["geometry"]),
                    "address_components": result.get("address_components", []),
                    "source": "google_maps"
                }
        except Exception as e:
            print(f"Google Maps validation error: {e}")
            return None
        
        return None
    
    def validate_address_openstreetmap(
        self,
        address_line1: str,
        city: Optional[str] = None,
        state: Optional[str] = None,
        postal_code: Optional[str] = None,
        country: Optional[str] = None
    ) -> Optional[Dict]:
        """Validate address with OpenStreetMap Nominatim API (free)"""
        ***REMOVED*** Build address string
        address_parts = [address_line1]
        if city:
            address_parts.append(city)
        if state:
            address_parts.append(state)
        if postal_code:
            address_parts.append(postal_code)
        if country:
            address_parts.append(country)
        
        address_string = ", ".join(address_parts)
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address_string,
            "format": "json",
            "limit": 1,
            "addressdetails": 1
        }
        headers = {
            "User-Agent": "B2B-Finder-OS/1.0"  ***REMOVED*** Nominatim requires User-Agent
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                result = data[0]
                
                return {
                    "validated": True,
                    "formatted_address": result.get("display_name"),
                    "latitude": float(result.get("lat")),
                    "longitude": float(result.get("lon")),
                    "location_type": result.get("type"),
                    "accuracy": 10.0,  ***REMOVED*** Nominatim typically 10-50m accuracy
                    "address_components": result.get("address", {}),
                    "source": "openstreetmap"
                }
        except Exception as e:
            print(f"OpenStreetMap validation error: {e}")
            return None
        
        return None
    
    def _calculate_accuracy(self, geometry: Dict) -> float:
        """Calculate accuracy from geometry information (meters)"""
        location_type = geometry.get("location_type")
        
        ***REMOVED*** Google Maps location_type mapping
        accuracy_map = {
            "ROOFTOP": 5.0,  ***REMOVED*** ~5 meters
            "RANGE_INTERPOLATED": 10.0,  ***REMOVED*** ~10 meters
            "GEOMETRIC_CENTER": 25.0,  ***REMOVED*** ~25 meters
            "APPROXIMATE": 100.0  ***REMOVED*** ~100 meters
        }
        
        return accuracy_map.get(location_type, 50.0)
    
    def validate_company_address(self, company: Company) -> bool:
        """Validate company address and update coordinates"""
        if not company.address_line1:
            return False
        
        ***REMOVED*** Try Google Maps first
        result = self.validate_address_google_maps(
            address_line1=company.address_line1,
            city=company.city,
            state=company.state,
            postal_code=company.postal_code,
            country=company.country
        )
        
        ***REMOVED*** Try OpenStreetMap if Google Maps fails
        if not result and self.openstreetmap_enabled:
            result = self.validate_address_openstreetmap(
                address_line1=company.address_line1,
                city=company.city,
                state=company.state,
                postal_code=company.postal_code,
                country=company.country
            )
        
        if result and result.get("validated"):
            ***REMOVED*** Update company information
            customer_pool_service.update_company(
                company.id,
                latitude=result.get("latitude"),
                longitude=result.get("longitude"),
                address_validated=True,
                address_validation_date=datetime.utcnow(),
                address_validation_source=result.get("source")
            )
            return True
        
        return False
    
    def batch_validate_addresses(self, company_ids: Optional[List[int]] = None, limit: int = 100) -> Dict:
        """Batch address validation"""
        if company_ids:
            companies = [customer_pool_service.get_company_by_id(cid) for cid in company_ids]
            companies = [c for c in companies if c is not None]
        else:
            companies = customer_pool_service.get_companies_without_address_validation(limit=limit)
        
        validated_count = 0
        failed_count = 0
        
        for company in companies:
            if self.validate_company_address(company):
                validated_count += 1
            else:
                failed_count += 1
        
        return {
            "total": len(companies),
            "validated": validated_count,
            "failed": failed_count,
            "success_rate": (validated_count / len(companies) * 100) if companies else 0
        }


***REMOVED*** Global instance
address_validation_service = AddressValidationService()

