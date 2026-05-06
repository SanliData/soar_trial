"""
SERVICE: location_affinity_service
PURPOSE: Location affinity service for map-based and physical location signals
ENCODING: UTF-8 WITHOUT BOM

Location Affinity is a first-class attribute in persona matching.
Supports:
- Map-based location selection (radius, polygon)
- Physical location signals (urban, coastal, industrial, etc.)
- Proximity clustering
- Location affinity scoring (0.0 to 1.0)
"""

import math
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from src.models.persona import Persona


class LocationAffinityService:
    """Service for managing location affinity in personas"""
    
    def __init__(self, db: Session):
        self.db = db
    
    ***REMOVED*** ========================================================================
    ***REMOVED*** LOCATION SIGNAL EXTRACTION
    ***REMOVED*** ========================================================================
    
    def extract_location_signals(
        self,
        latitude: float,
        longitude: float,
        address: Optional[str] = None
    ) -> List[str]:
        """
        Extract physical location signals from coordinates and address.
        
        Returns list of signals like: ["urban", "coastal", "industrial", "suburban", "tourist-destination"]
        
        Note: This is a simplified version. In production, you would:
        - Use reverse geocoding APIs (Google Maps, OpenStreetMap Nominatim)
        - Check proximity to coastlines, urban centers, industrial zones
        - Classify based on address components
        """
        signals = []
        
        ***REMOVED*** Basic signal extraction (would be enhanced with real geocoding APIs)
        if address:
            address_lower = address.lower()
            
            ***REMOVED*** Urban signals
            if any(keyword in address_lower for keyword in ["center", "downtown", "şehir", "merkez"]):
                signals.append("urban")
            
            ***REMOVED*** Coastal signals
            if any(keyword in address_lower for keyword in ["coast", "beach", "sahil", "deniz", "marina"]):
                signals.append("coastal")
            
            ***REMOVED*** Industrial signals
            if any(keyword in address_lower for keyword in ["industrial", "sanayi", "zone", "park"]):
                signals.append("industrial")
            
            ***REMOVED*** Tourist destination signals
            if any(keyword in address_lower for keyword in ["tourist", "resort", "hotel", "otel", "turizm"]):
                signals.append("tourist-destination")
        
        ***REMOVED*** If no specific signals found, default to urban
        if not signals:
            signals.append("urban")
        
        return signals
    
    ***REMOVED*** ========================================================================
    ***REMOVED*** LOCATION AFFINITY SCORING
    ***REMOVED*** ========================================================================
    
    def calculate_location_affinity_score(
        self,
        persona_lat: float,
        persona_lng: float,
        persona_signals: List[str],
        persona_radius: Optional[int],
        persona_polygon: Optional[Dict],
        target_lat: float,
        target_lng: float,
        target_signals: Optional[List[str]] = None
    ) -> float:
        """
        Calculate location affinity score (0.0 to 1.0) between persona and target.
        
        Factors:
        1. Distance (within radius/polygon = higher score)
        2. Signal matching (matching signals = higher score)
        3. Proximity (closer = higher score, but capped by radius)
        """
        ***REMOVED*** Calculate distance (Haversine formula)
        distance_km = self._haversine_distance(persona_lat, persona_lng, target_lat, target_lng)
        
        ***REMOVED*** Factor 1: Distance score (0.0 to 1.0)
        distance_score = 0.0
        
        if persona_polygon:
            ***REMOVED*** Check if target is within polygon
            is_inside = self._point_in_polygon(target_lat, target_lng, persona_polygon)
            if is_inside:
                distance_score = 1.0
            else:
                ***REMOVED*** Score decreases with distance from polygon
                distance_score = max(0.0, 1.0 - (distance_km / 100.0))  ***REMOVED*** Decay over 100km
        elif persona_radius:
            ***REMOVED*** Check if target is within radius
            distance_meters = distance_km * 1000
            if distance_meters <= persona_radius:
                distance_score = 1.0
            else:
                ***REMOVED*** Score decreases with distance beyond radius
                excess_distance = distance_meters - persona_radius
                distance_score = max(0.0, 1.0 - (excess_distance / (persona_radius * 2)))  ***REMOVED*** Decay over 2x radius
        else:
            ***REMOVED*** No radius/polygon, use distance decay
            distance_score = max(0.0, 1.0 - (distance_km / 50.0))  ***REMOVED*** Decay over 50km
        
        ***REMOVED*** Factor 2: Signal matching score (0.0 to 1.0)
        signal_score = 0.0
        if persona_signals and target_signals:
            matching_signals = set(persona_signals) & set(target_signals)
            if matching_signals:
                signal_score = len(matching_signals) / max(len(persona_signals), len(target_signals))
        elif persona_signals or target_signals:
            ***REMOVED*** If only one side has signals, no match = 0.5 (neutral)
            signal_score = 0.5
        else:
            ***REMOVED*** No signals on either side = 0.5 (neutral)
            signal_score = 0.5
        
        ***REMOVED*** Combined score (weighted average: 70% distance, 30% signals)
        location_affinity_score = (distance_score * 0.7) + (signal_score * 0.3)
        
        return min(1.0, max(0.0, location_affinity_score))
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula (in kilometers)"""
        ***REMOVED*** Earth radius in kilometers
        R = 6371.0
        
        ***REMOVED*** Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        ***REMOVED*** Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def _point_in_polygon(self, lat: float, lng: float, polygon: Dict) -> bool:
        """
        Check if a point is inside a GeoJSON polygon.
        
        Polygon format: {
            "type": "Polygon",
            "coordinates": [[[lng, lat], [lng, lat], ...]]  ***REMOVED*** First ring is exterior
        }
        """
        try:
            ***REMOVED*** Get coordinates from GeoJSON polygon
            if polygon.get("type") != "Polygon":
                return False
            
            coordinates = polygon.get("coordinates", [])
            if not coordinates or not coordinates[0]:
                return False
            
            ***REMOVED*** Extract exterior ring (first ring)
            exterior_ring = coordinates[0]
            
            ***REMOVED*** Ray casting algorithm
            inside = False
            j = len(exterior_ring) - 1
            
            for i in range(len(exterior_ring)):
                xi, yi = exterior_ring[i]  ***REMOVED*** [lng, lat]
                xj, yj = exterior_ring[j]  ***REMOVED*** [lng, lat]
                
                intersect = ((yi > lng) != (yj > lng)) and (lat < (xj - xi) * (lng - yi) / (yj - yi) + xi)
                if intersect:
                    inside = not inside
                j = i
            
            return inside
        except Exception:
            ***REMOVED*** If polygon is invalid, return False
            return False
    
    ***REMOVED*** ========================================================================
    ***REMOVED*** LOCATION AFFINITY MANAGEMENT
    ***REMOVED*** ========================================================================
    
    def set_location_affinity(
        self,
        persona_id: int,
        latitude: float,
        longitude: float,
        location_signals: Optional[List[str]] = None,
        radius_meters: Optional[int] = None,
        polygon: Optional[Dict] = None,
        proximity_clusters: Optional[List[str]] = None
    ) -> Persona:
        """
        Set location affinity for a persona.
        
        Args:
            persona_id: Persona ID
            latitude: Center latitude
            longitude: Center longitude
            location_signals: List of physical location signals (auto-extracted if None)
            radius_meters: Radius in meters (for circular targeting)
            polygon: GeoJSON polygon (for custom area targeting)
            proximity_clusters: List of cluster IDs
        """
        persona = self.db.query(Persona).filter(Persona.id == persona_id).first()
        if not persona:
            raise ValueError(f"Persona with ID {persona_id} not found")
        
        ***REMOVED*** Extract location signals if not provided
        if location_signals is None:
            location_signals = self.extract_location_signals(
                latitude,
                longitude,
                persona.work_address
            )
        
        ***REMOVED*** Update persona location affinity
        if persona.work_location is None:
            persona.work_location = {}
        
        persona.work_location["latitude"] = latitude
        persona.work_location["longitude"] = longitude
        
        persona.location_signals = location_signals
        persona.location_radius_meters = radius_meters
        persona.location_polygon = polygon
        persona.location_proximity_clusters = proximity_clusters
        
        ***REMOVED*** Calculate initial affinity score (will be updated during matching)
        if persona.work_location:
            persona.location_affinity_score = 0.5  ***REMOVED*** Default neutral score
        
        self.db.commit()
        self.db.refresh(persona)
        
        return persona
    
    def calculate_affinity_for_target(
        self,
        persona_id: int,
        target_latitude: float,
        target_longitude: float,
        target_signals: Optional[List[str]] = None
    ) -> float:
        """
        Calculate location affinity score between a persona and a target location.
        
        Returns:
            float: Affinity score (0.0 to 1.0)
        """
        persona = self.db.query(Persona).filter(Persona.id == persona_id).first()
        if not persona:
            raise ValueError(f"Persona with ID {persona_id} not found")
        
        if not persona.work_location:
            return 0.0
        
        persona_lat = persona.work_location.get("latitude")
        persona_lng = persona.work_location.get("longitude")
        
        if persona_lat is None or persona_lng is None:
            return 0.0
        
        score = self.calculate_location_affinity_score(
            persona_lat=persona_lat,
            persona_lng=persona_lng,
            persona_signals=persona.location_signals or [],
            persona_radius=persona.location_radius_meters,
            persona_polygon=persona.location_polygon,
            target_lat=target_latitude,
            target_lng=target_longitude,
            target_signals=target_signals
        )
        
        return score
